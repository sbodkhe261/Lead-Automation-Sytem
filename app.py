import os
import sys
import asyncio

# Ensure Windows uses ProactorEventLoop so Playwright subprocesses run without NotImplementedError
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import io
import csv
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
from sqlalchemy import func, or_

from database.db import init_db, SessionLocal
from database.models import Lead
from scraper.google_maps import scrape_google_maps, detect_area, PUNE_ZONES
from scraper.web_scraper import scrape_website
from scraper.job_intent_scraper import scrape_pune_job_intent
from scraper.decision_maker_enricher import enrich_decision_maker_contact
from scraper.mca_enrichment import enrich_mca_financials
from scraper.technographic_scanner import scan_technographics
from agent.gemini_agent import analyze_lead_with_gemini
from agent.notifier import dispatch_all_alerts, get_notifier_config, send_direct_whatsapp, send_direct_email, send_telegram_alert
from agent.drip_campaign import advance_campaign_step, run_due_campaign_sweeps, get_campaign_templates

load_dotenv()

app = FastAPI(title="Autonomous Enterprise Lead Intelligence Engine", version="4.0.0")

# Mount Static UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# Global pipeline status tracking
pipeline_state = {
    "is_running": False,
    "current_step": "Idle",
    "leads_processed": 0,
    "total_target": 0,
    "last_error": None
}

# Auto-Pilot Autonomous Engine State (Daily Scheduled Sweeps)
autopilot_state = {
    "enabled": True,
    "interval_hours": 24, # Daily scheduled discovery (every 24 hours)
    "last_run": None,
    "next_run": None,
    "total_runs": 0,
    "leads_found": 0,
    "status": "Active (Daily sweep scheduled)",
    "is_running_now": False
}

async def run_autopilot_sweep() -> int:
    """Autonomous worker that sweeps all Pune industrial zones daily for new leads without human intervention."""
    autopilot_state["is_running_now"] = True
    new_leads_count = 0
    print("[AUTOPILOT DAILY] Beginning systematic daily lead discovery sweep across all Pune industrial zones...")
    
    try:
        session = SessionLocal()
        existing_companies = set(r[0].lower() for r in session.query(Lead.company_name).all())
        session.close()

        # Systematic multi-sector daily sweep across all 6 Pune industrial zones
        for zone in PUNE_ZONES:
            zone_queries = [
                f"Manufacturing companies in {zone} Pune",
                f"Industrial automation and robotics in {zone} Pune",
                f"Precision engineering and auto components in {zone} Pune"
            ]

            for query in zone_queries:
                print(f"[AUTOPILOT DAILY] Sweeping {zone} with targeted query: '{query}'...")
                try:
                    scraped_items = await scrape_google_maps(query, max_results=3)
                except Exception as e:
                    print(f"[AUTOPILOT SCRAPE ERROR] {zone}: {e}")
                    continue

                session = SessionLocal()
                for item in scraped_items:
                    company_name = item.get('company_name', 'Unknown')
                    if company_name.lower() in existing_companies:
                        continue # Skip duplicates to ensure only fresh leads are processed
                    
                    existing_companies.add(company_name.lower())
                    website = item.get('url', '')
                    raw_text = item.get('raw_text', '')
                    
                    if website and website.startswith("http") and "google.com" not in website:
                        try:
                            content = await scrape_website(website)
                            if content:
                                raw_text = f"{raw_text}\n{content}"
                        except Exception:
                            pass

                    # Autonomous Gemini AI Lead Analysis
                    analysis = analyze_lead_with_gemini(
                        raw_text=raw_text,
                        company_name=company_name,
                        location_hint=f"{zone}, Pune, Maharashtra"
                    )
                    
                    score = int(analysis.get('score', 0))
                    priority = analysis.get('priority', 'Low')
                    tech_val = analysis.get('tech_stack', [])
                    tech_str = ",".join(tech_val) if isinstance(tech_val, list) else str(tech_val)
                    score_breakdown_str = json.dumps(analysis.get('score_breakdown', {}))

                    new_lead = Lead(
                        company_name=company_name,
                        website=website,
                        phone=item.get('phone', ''),
                        address=item.get('address', f"{zone}, Pune, Maharashtra"),
                        area=zone,
                        google_rating=item.get('rating', 4.5),
                        source='autopilot_autonomous',
                        raw_text=raw_text[:2000],
                        tech_stack=tech_str,
                        pain_points=analysis.get('pain_points', ''),
                        decision_maker=analysis.get('decision_maker', ''),
                        relevance_score=score,
                        priority=priority,
                        score_breakdown=score_breakdown_str,
                        score_reasoning=analysis.get('reasoning', ''),
                        generated_pitch=analysis.get('email_pitch', ''),
                        whatsapp_pitch=analysis.get('whatsapp_pitch', ''),
                        alert_sent=False
                    )
                    session.add(new_lead)
                    session.commit()
                    new_leads_count += 1
                    
                    # AUTOMATIC DISPATCH: If High Priority lead (Score >= 75 or Priority == 'High'),
                    # automatically dispatch to Telegram and Email immediately without user needing to click!
                    if (score >= 75 or priority == "High"):
                        print(f"[AUTOPILOT AUTO-DISPATCH] High Priority Lead detected: '{company_name}' ({score}/100, {priority})! Automatically dispatching to Telegram & Email...")
                        dispatched = send_lead_alert(new_lead)
                        if dispatched:
                            new_lead.alert_sent = True
                            session.commit()
                            print(f"[AUTOPILOT AUTO-DISPATCH SUCCESS] Lead '{company_name}' dispatched automatically to Telegram (@BBI_leads_alert_bot) & Email!")

                session.close()

    except Exception as e:
        print(f"[AUTOPILOT ERROR] Daily sweep encountered error: {e}")
    finally:
        autopilot_state["is_running_now"] = False

    return new_leads_count

async def autopilot_scheduler_loop():
    """Background daemon loop that executes autonomous lead discovery on a daily schedule."""
    # Initialize next run time immediately
    next_dt = datetime.now() + timedelta(hours=autopilot_state["interval_hours"])
    autopilot_state["next_run"] = next_dt.strftime("%Y-%m-%d %H:%M")
    autopilot_state["status"] = f"Daily Auto-Pilot Active (Next run: {autopilot_state['next_run']})"

    # Brief initial pause to let server finish bootstrapping
    await asyncio.sleep(10)
    
    while True:
        try:
            if autopilot_state["enabled"]:
                autopilot_state["status"] = "Harvesting daily leads across Pune hubs..."
                now = datetime.now()
                autopilot_state["last_run"] = now.strftime("%Y-%m-%d %H:%M")
                
                new_count = await run_autopilot_sweep()
                autopilot_state["total_runs"] += 1
                autopilot_state["leads_found"] += new_count
                
                next_dt = datetime.now() + timedelta(hours=autopilot_state["interval_hours"])
                autopilot_state["next_run"] = next_dt.strftime("%Y-%m-%d %H:%M")
                autopilot_state["status"] = f"Daily Auto-Pilot Active (Next run: {autopilot_state['next_run']})"
                print(f"[AUTOPILOT DAILY] Completed daily cycle. Harvested: {new_count} new leads. Next run at: {autopilot_state['next_run']}")
            else:
                autopilot_state["status"] = "Paused by user"
        except Exception as e:
            autopilot_state["status"] = f"Scheduler error: {e}"

        # Sleep in 15-second slices so config changes or manual toggles take effect immediately
        sleep_total = max(60, int(autopilot_state["interval_hours"] * 3600))
        for _ in range(sleep_total // 15):
            if not autopilot_state["enabled"]:
                break
            await asyncio.sleep(15)

@app.on_event("startup")
async def on_startup():
    init_db()
    # Arm background Auto-Pilot daily daemon
    asyncio.create_task(autopilot_scheduler_loop())
    print("[SERVER STARTUP] Daily Auto-Pilot scheduler armed and running in background.")
    print("[SERVER STARTUP] Auto-Pilot scheduler armed and running in background.")

@app.get("/")
def serve_index():
    return FileResponse("ui/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "app": "Lead Automation System"}

class ScrapeRequest(BaseModel):
    query: str
    max_results: int = 5
    area: Optional[str] = None

class BulkScrapeRequest(BaseModel):
    results_per_area: int = 4

class AutoPilotConfig(BaseModel):
    enabled: Optional[bool] = None
    interval_hours: Optional[int] = None

@app.get("/api/status")
def get_pipeline_status():
    return pipeline_state

@app.get("/api/autopilot/status")
def get_autopilot_status():
    return autopilot_state

@app.post("/api/autopilot/toggle")
def toggle_autopilot():
    autopilot_state["enabled"] = not autopilot_state["enabled"]
    autopilot_state["status"] = "Active (Next run scheduled)" if autopilot_state["enabled"] else "Paused by user"
    if autopilot_state["enabled"]:
        next_dt = datetime.now() + timedelta(hours=autopilot_state["interval_hours"])
        autopilot_state["next_run"] = next_dt.strftime("%Y-%m-%d %H:%M")
    return autopilot_state

@app.post("/api/autopilot/config")
def set_autopilot_config(config: AutoPilotConfig):
    if config.enabled is not None:
        autopilot_state["enabled"] = config.enabled
    if config.interval_hours is not None and config.interval_hours >= 1:
        autopilot_state["interval_hours"] = config.interval_hours
        next_dt = datetime.now() + timedelta(hours=autopilot_state["interval_hours"])
        autopilot_state["next_run"] = next_dt.strftime("%Y-%m-%d %H:%M")
    return autopilot_state

@app.post("/api/autopilot/trigger")
async def trigger_autopilot_now(background_tasks: BackgroundTasks):
    if autopilot_state["is_running_now"]:
        raise HTTPException(status_code=400, detail="Auto-pilot is already executing a sweep.")
    background_tasks.add_task(run_autopilot_sweep)
    return {"message": "Auto-Pilot sweep triggered immediately in background."}

@app.get("/api/stats")
def get_stats(area: Optional[str] = Query(None), priority: Optional[str] = Query(None)):
    session = SessionLocal()
    try:
        # Global Database Totals (for top KPI Ribbon)
        total_global = session.query(Lead).count()
        high_global = session.query(Lead).filter(Lead.priority == "High").count()
        medium_global = session.query(Lead).filter(Lead.priority == "Medium").count()
        low_global = session.query(Lead).filter(Lead.priority == "Low").count()
        alerted_global = session.query(Lead).filter(Lead.alert_sent == True).count()
        
        # Area-Filtered Priority Counts (tailored to selected area)
        area_q = session.query(Lead)
        if area and area != "All":
            area_q = area_q.filter(
                or_(
                    Lead.area.ilike(f"%{area}%"),
                    Lead.address.ilike(f"%{area}%")
                )
            )

        area_total = area_q.count()
        area_high = area_q.filter(Lead.priority == "High").count()
        area_medium = area_q.filter(Lead.priority == "Medium").count()
        area_low = area_q.filter(Lead.priority == "Low").count()
        area_alerted = area_q.filter(Lead.alert_sent == True).count()

        # Priority-Filtered Area Counts (tailored to selected priority)
        prio_q = session.query(Lead)
        if priority and priority != "All":
            if priority == "Alerted":
                prio_q = prio_q.filter(Lead.alert_sent == True)
            else:
                prio_q = prio_q.filter(Lead.priority == priority)

        area_counts = {}
        for zone in PUNE_ZONES:
            zone_count = prio_q.filter(
                or_(
                    Lead.area.ilike(f"%{zone}%"),
                    Lead.address.ilike(f"%{zone}%")
                )
            ).count()
            area_counts[zone] = zone_count
                    
        return {
            # Global KPI ribbon stats
            "total_leads": total_global,
            "high_priority": high_global,
            "medium_priority": medium_global,
            "low_priority": low_global,
            "alerts_dispatched": alerted_global,
            
            # Dynamic badge counts for the currently selected area
            "area_scoped": {
                "total": area_total,
                "high": area_high,
                "medium": area_medium,
                "low": area_low,
                "alerted": area_alerted
            },
            
            # Dynamic area tab badges for the currently selected priority
            "area_counts": area_counts
        }
    finally:
        session.close()

@app.get("/api/leads")
def get_leads(
    priority: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    alerted_only: Optional[bool] = Query(None)
):
    session = SessionLocal()
    try:
        q = session.query(Lead)
        
        # 1. Filter by Priority or Alerted status
        if priority == "Alerted" or alerted_only:
            q = q.filter(Lead.alert_sent == True)
        elif priority and priority != "All":
            q = q.filter(Lead.priority == priority)
            
        # 2. Filter by Area / Zone
        if area and area != "All":
            q = q.filter(
                or_(
                    Lead.area.ilike(f"%{area}%"),
                    Lead.address.ilike(f"%{area}%")
                )
            )
            
        # 3. Minimum Score filter
        if min_score is not None:
            q = q.filter(Lead.relevance_score >= min_score)
            
        # 4. Keyword Search filter
        if search and search.strip():
            term = f"%{search.strip()}%"
            q = q.filter(
                or_(
                    Lead.company_name.ilike(term),
                    Lead.address.ilike(term),
                    Lead.tech_stack.ilike(term),
                    Lead.area.ilike(term),
                    Lead.pain_points.ilike(term),
                    Lead.score_reasoning.ilike(term),
                    Lead.generated_pitch.ilike(term)
                )
            )
            
        leads = q.order_by(Lead.relevance_score.desc(), Lead.id.desc()).all()
        return [l.to_dict() for l in leads]
    finally:
        session.close()

def send_lead_alert(lead: Lead) -> bool:
    """Dispatches lead alert automatically via configured channels (Direct Telegram, Direct Email)."""
    try:
        cfg = get_notifier_config()
        cfg["whatsapp_enabled"] = False  # WhatsApp is permanently disabled
        cfg["telegram_enabled"] = True
        cfg["email_enabled"] = True
        results = dispatch_all_alerts(lead, custom_cfg=cfg)
        print(f"[AUTO-ALERT DISPATCH RESULTS] Lead: {getattr(lead, 'company_name', 'Unknown')}: {results}")
        # Consider dispatched if any active channel succeeded or responded
        if any(r.get("success", False) for r in results.values() if isinstance(r, dict)):
            return True
    except Exception as e:
        print(f"[ALERT DISPATCH ERROR] Failed to dispatch alerts for {getattr(lead, 'company_name', 'Lead')}: {e}")
    return False

def run_single_pipeline(query: str, max_results: int, area_override: Optional[str] = None):
    """Executes scraping, enrichment, Gemini scoring, and storage for a query."""
    global pipeline_state
    detected_target_area = area_override or detect_area(query=query)
    pipeline_state["is_running"] = True
    pipeline_state["current_step"] = f"Scraping {detected_target_area}..."
    pipeline_state["leads_processed"] = 0
    pipeline_state["total_target"] = max_results
    pipeline_state["last_error"] = None

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process():
        global pipeline_state
        try:
            scraped_items = await scrape_google_maps(query, max_results)
            session = SessionLocal()
            
            for idx, item in enumerate(scraped_items, 1):
                company_name = item.get('company_name', 'Unknown')
                website = item.get('url', '')
                item_area = item.get('area') or detected_target_area
                pipeline_state["current_step"] = f"Evaluating [{item_area}] {idx}/{len(scraped_items)}: {company_name}"
                
                raw_text = item.get('raw_text', '')
                if website and website.startswith("http") and "google.com" not in website:
                    try:
                        content = await scrape_website(website)
                        if content:
                            raw_text = f"{raw_text}\n{content}"
                    except Exception as e:
                        print(f"Website scrape error: {e}")
                        
                analysis = analyze_lead_with_gemini(
                    raw_text=raw_text,
                    company_name=company_name,
                    location_hint=f"{item_area}, Pune, Maharashtra"
                )
                
                score = int(analysis.get('score', 0))
                priority = analysis.get('priority', 'Low')
                score_breakdown_str = json.dumps(analysis.get('score_breakdown', {}))
                
                existing = session.query(Lead).filter(Lead.company_name == company_name).first()
                if existing:
                    target_lead = existing
                    target_lead.area = item_area
                    target_lead.relevance_score = score
                    target_lead.priority = priority
                    target_lead.score_breakdown = score_breakdown_str
                    target_lead.score_reasoning = analysis.get('reasoning', '')
                    target_lead.generated_pitch = analysis.get('email_pitch', '')
                    target_lead.whatsapp_pitch = analysis.get('whatsapp_pitch', '')
                    target_lead.decision_maker = analysis.get('decision_maker', '')
                    target_lead.pain_points = analysis.get('pain_points', '')
                else:
                    tech_val = analysis.get('tech_stack', [])
                    tech_str = ",".join(tech_val) if isinstance(tech_val, list) else str(tech_val)
                    
                    target_lead = Lead(
                        company_name=company_name,
                        website=website,
                        phone=item.get('phone', ''),
                        address=item.get('address', f"{item_area}, Pune, Maharashtra"),
                        area=item_area,
                        google_rating=item.get('rating', 4.5),
                        source='google_maps',
                        raw_text=raw_text[:2000],
                        tech_stack=tech_str,
                        pain_points=analysis.get('pain_points', ''),
                        decision_maker=analysis.get('decision_maker', ''),
                        relevance_score=score,
                        priority=priority,
                        score_breakdown=score_breakdown_str,
                        score_reasoning=analysis.get('reasoning', ''),
                        generated_pitch=analysis.get('email_pitch', ''),
                        whatsapp_pitch=analysis.get('whatsapp_pitch', ''),
                        alert_sent=False
                    )
                    session.add(target_lead)
                    
                session.commit()
                
                # AUTOMATIC DISPATCH: High Priority leads (Score >= 75 or Priority == 'High')
                # automatically trigger instant Telegram and Email alerts without needing manual clicks!
                if (score >= 75 or priority == "High") and not target_lead.alert_sent:
                    print(f"[AUTO-DISPATCH] High Priority Lead detected: '{company_name}' ({score}/100, {priority})! Automatically dispatching to Telegram & Email...")
                    dispatched = send_lead_alert(target_lead)
                    if dispatched:
                        target_lead.alert_sent = True
                        session.commit()
                        print(f"[AUTO-DISPATCH SUCCESS] Lead '{company_name}' dispatched to Telegram & Email!")
                        
                pipeline_state["leads_processed"] = idx
                
            session.close()
            pipeline_state["current_step"] = f"Completed successfully for {detected_target_area}"
        except Exception as e:
            pipeline_state["last_error"] = str(e)
            pipeline_state["current_step"] = f"Failed: {e}"
        finally:
            pipeline_state["is_running"] = False

    loop.run_until_complete(process())
    loop.close()

def run_bulk_pipeline(results_per_area: int):
    """Runs scraping across all 6 Pune industrial zones in sequence."""
    global pipeline_state
    pipeline_state["is_running"] = True
    total_expected = len(PUNE_ZONES) * results_per_area
    pipeline_state["total_target"] = total_expected
    pipeline_state["leads_processed"] = 0
    pipeline_state["last_error"] = None

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def process():
        global pipeline_state
        try:
            total_done = 0
            for zone in PUNE_ZONES:
                pipeline_state["current_step"] = f"Harvesting all leads in {zone}..."
                query = f"Manufacturing companies in {zone} Pune"
                items = await scrape_google_maps(query, results_per_area)
                
                session = SessionLocal()
                for item in items:
                    company_name = item.get('company_name', 'Unknown')
                    website = item.get('url', '')
                    raw_text = item.get('raw_text', '')
                    
                    analysis = analyze_lead_with_gemini(
                        raw_text=raw_text,
                        company_name=company_name,
                        location_hint=f"{zone}, Pune, Maharashtra"
                    )
                    
                    score = int(analysis.get('score', 0))
                    priority = analysis.get('priority', 'Low')
                    score_breakdown_str = json.dumps(analysis.get('score_breakdown', {}))
                    
                    existing = session.query(Lead).filter(Lead.company_name == company_name).first()
                    if existing:
                        target_lead = existing
                        target_lead.area = zone
                        target_lead.relevance_score = score
                        target_lead.priority = priority
                        target_lead.score_breakdown = score_breakdown_str
                        target_lead.score_reasoning = analysis.get('reasoning', '')
                        target_lead.generated_pitch = analysis.get('email_pitch', '')
                        target_lead.whatsapp_pitch = analysis.get('whatsapp_pitch', '')
                    else:
                        tech_val = analysis.get('tech_stack', [])
                        tech_str = ",".join(tech_val) if isinstance(tech_val, list) else str(tech_val)
                        
                        target_lead = Lead(
                            company_name=company_name,
                            website=website,
                            phone=item.get('phone', ''),
                            address=item.get('address', f"{zone}, Pune, Maharashtra"),
                            area=zone,
                            google_rating=item.get('rating', 4.5),
                            source='pune_midc_registry',
                            raw_text=raw_text[:2000],
                            tech_stack=tech_str,
                            pain_points=analysis.get('pain_points', ''),
                            decision_maker=analysis.get('decision_maker', ''),
                            relevance_score=score,
                            priority=priority,
                            score_breakdown=score_breakdown_str,
                            score_reasoning=analysis.get('reasoning', ''),
                            generated_pitch=analysis.get('email_pitch', ''),
                            whatsapp_pitch=analysis.get('whatsapp_pitch', ''),
                            alert_sent=False
                        )
                        session.add(target_lead)
                    
                    session.commit()

                    # AUTOMATIC DISPATCH: High Priority leads (Score >= 75 or Priority == 'High')
                    # automatically trigger instant Telegram and Email alerts without needing manual clicks!
                    if (score >= 75 or priority == "High") and not target_lead.alert_sent:
                        print(f"[BULK AUTO-DISPATCH] High Priority Lead detected: '{company_name}' ({score}/100, {priority})! Automatically dispatching to Telegram & Email...")
                        dispatched = send_lead_alert(target_lead)
                        if dispatched:
                            target_lead.alert_sent = True
                            session.commit()
                            print(f"[BULK AUTO-DISPATCH SUCCESS] Lead '{company_name}' dispatched to Telegram & Email!")

                    total_done += 1
                    pipeline_state["leads_processed"] = total_done
                    
                session.close()
                
            pipeline_state["current_step"] = "Bulk harvest across all Pune hubs complete!"
        except Exception as e:
            pipeline_state["last_error"] = str(e)
            pipeline_state["current_step"] = f"Bulk scrape error: {e}"
        finally:
            pipeline_state["is_running"] = False

    loop.run_until_complete(process())
    loop.close()

@app.post("/api/scrape")
def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    if pipeline_state["is_running"]:
        raise HTTPException(status_code=400, detail="A scraping pipeline is already running.")
    background_tasks.add_task(run_single_pipeline, request.query, request.max_results, request.area)
    return {"message": f"Autonomous scraper pipeline initiated for {request.query} in background."}

@app.post("/api/scrape/bulk")
def trigger_bulk_scrape(request: BulkScrapeRequest, background_tasks: BackgroundTasks):
    if pipeline_state["is_running"]:
        raise HTTPException(status_code=400, detail="A scraping pipeline is already running.")
    background_tasks.add_task(run_bulk_pipeline, request.results_per_area)
    return {"message": "Bulk scraper initiated across ALL Pune Industrial Hubs in background."}

@app.post("/api/leads/{lead_id}/rescore")
def rescore_lead(lead_id: int):
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
            
        analysis = analyze_lead_with_gemini(
            raw_text=lead.raw_text or lead.company_name,
            company_name=lead.company_name,
            location_hint=f"{lead.area or 'Pune MIDC'}, Pune, Maharashtra"
        )
        
        lead.relevance_score = int(analysis.get('score', 0))
        lead.priority = analysis.get('priority', 'Low')
        lead.score_reasoning = analysis.get('reasoning', '')
        lead.generated_pitch = analysis.get('email_pitch', '')
        lead.whatsapp_pitch = analysis.get('whatsapp_pitch', '')
        lead.decision_maker = analysis.get('decision_maker', '')
        lead.pain_points = analysis.get('pain_points', '')
        
        tech_val = analysis.get('tech_stack', [])
        lead.tech_stack = ",".join(tech_val) if isinstance(tech_val, list) else str(tech_val)
        
        # AUTO-DISPATCH ALERT: If re-scored lead is High Priority (>= 75) and not yet sent
        if (lead.relevance_score >= 75 or lead.priority == "High") and not lead.alert_sent:
            print(f"[RE-SCORE AUTO-ALERT] High Priority lead '{lead.company_name}' ({lead.relevance_score}/100) detected on rescore. Dispatching alert...")
            if send_lead_alert(lead):
                lead.alert_sent = True

        session.commit()
        return lead.to_dict()
    finally:
        session.close()

async def enrich_single_lead_record(lead: Lead, session) -> Lead:
    """Enriches lead with Technographics, MCA Financials, and Decision Maker / LinkedIn data."""
    domain = lead.website or ""
    
    # 1. Technographics
    tech_data = await scan_technographics(domain)
    lead.technographics = json.dumps(tech_data)
    
    # Technographic score booster
    if tech_data.get("sap_subdomain_detected") and lead.relevance_score < 85:
        lead.relevance_score = min(lead.relevance_score + 15, 100)
        lead.priority = "High" if lead.relevance_score >= 75 else lead.priority
    if tech_data.get("microsoft_365") and lead.relevance_score < 80:
        lead.relevance_score = min(lead.relevance_score + 10, 100)
        lead.priority = "High" if lead.relevance_score >= 75 else lead.priority

    # 2. MCA Financials & Scale
    mca_data = await enrich_mca_financials(lead.company_name)
    lead.cin = mca_data.get("cin", "")
    lead.revenue_range = mca_data.get("revenue_range", "")
    lead.automation_budget = mca_data.get("automation_budget", "")
    lead.directors = json.dumps(mca_data.get("directors", []))

    # 3. Decision Maker & LinkedIn Discovery
    dm_data = await enrich_decision_maker_contact(lead.company_name, domain)
    lead.decision_maker_name = dm_data.get("name", "")
    lead.decision_maker_email = dm_data.get("email", "")
    lead.decision_maker_linkedin = dm_data.get("linkedin_url", "")
    if dm_data.get("title") and (not lead.decision_maker or lead.decision_maker == "Operations"):
        lead.decision_maker = dm_data.get("title")

    # AUTO-DISPATCH ALERT: If lead is High Priority (>= 75) and not yet sent, trigger immediately!
    if (lead.relevance_score >= 75 or lead.priority == "High") and not lead.alert_sent:
        print(f"[AUTO-ALERT] High Priority lead '{lead.company_name}' ({lead.relevance_score}/100) detected during enrichment. Dispatching to Telegram & Email...")
        if send_lead_alert(lead):
            lead.alert_sent = True

    session.commit()
    return lead

@app.post("/api/leads/{lead_id}/enrich")
async def enrich_lead(lead_id: int):
    """Enriches a specific lead with Technographics, MCA Financials, and Decision Maker / LinkedIn data."""
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        updated = await enrich_single_lead_record(lead, session)
        return {"status": "success", "lead": updated.to_dict()}
    finally:
        session.close()

@app.post("/api/leads/enrich-all")
async def enrich_all_leads():
    """Enriches all leads in database that have missing decision maker or technographic info."""
    session = SessionLocal()
    try:
        leads = session.query(Lead).filter(
            or_(Lead.decision_maker_email == None, Lead.technographics == None, Lead.cin == None)
        ).all()
        enriched_count = 0
        for l in leads:
            await enrich_single_lead_record(l, session)
            enriched_count += 1
        return {"status": "success", "enriched_count": enriched_count}
    finally:
        session.close()

@app.post("/api/jobs/scrape")
async def trigger_job_intent_scrape(limit: int = 10):
    """
    Scrapes live hiring intent for SAP, Power BI, and PLC Automation across Pune industrial zones.
    Automatically boosts relevance and adds new intent opportunities to the pipeline.
    """
    jobs = await scrape_pune_job_intent(max_results=limit)
    session = SessionLocal()
    added = 0
    updated = 0
    try:
        for job in jobs:
            comp_name = job["company_name"]
            existing = session.query(Lead).filter(Lead.company_name.ilike(f"%{comp_name}%")).first()
            
            job_badge = json.dumps([{
                "title": job["job_title"],
                "service": job.get("service_fit", ""),
                "reason": job.get("intent_reason", ""),
                "url": job.get("job_url", ""),
                "posted": job.get("posted", "Active")
            }])
            
            if existing:
                existing.hiring_signals = job_badge
                # Boost priority because they have active hiring budget!
                existing.relevance_score = min(existing.relevance_score + 25, 100)
                if existing.relevance_score >= 75:
                    existing.priority = "High"
                    if not existing.alert_sent:
                        if send_lead_alert(existing):
                            existing.alert_sent = True
                updated += 1
            else:
                # Add as high-intent lead
                new_lead = Lead(
                    company_name=comp_name,
                    website=f"https://www.{comp_name.lower().replace(' ', '')}.com",
                    address=job.get("location", "Pune Industrial Corridor, Maharashtra"),
                    area="Chakan MIDC" if "chakan" in job.get("location", "").lower() else "Pune MIDC",
                    google_rating=4.5,
                    source="naukri_hiring_intent",
                    raw_text=f"Company actively hiring: {job['job_title']}. Service Fit: {job.get('service_fit')}. {job.get('intent_reason')}",
                    tech_stack=f"{job.get('service_fit')}, Enterprise Manufacturing",
                    pain_points=job.get("intent_reason", "Active hiring indicates critical operational bottleneck"),
                    decision_maker="Plant Head / VP Operations",
                    hiring_signals=job_badge,
                    relevance_score=90,
                    priority="High",
                    score_reasoning=f"High-intent signal: Actively recruiting for {job['job_title']} in Pune.",
                    generated_pitch=f"Subject: Accelerating your {job['job_title']} initiative for {comp_name}\n\nHi Team,\n\nI noticed {comp_name} is actively recruiting for a {job['job_title']}. At BrownBox Innovation (Pune), we can immediately deploy turnkey {job.get('service_fit')} without the 3-month hiring ramp.\n\nOpen for a quick 10-minute briefing?",
                    whatsapp_pitch=f"Hi {comp_name}! Noticed you are hiring for a {job['job_title']}. BrownBox Innovation provides turnkey {job.get('service_fit')} in Pune MIDC. Quick 5-min chat?",
                    alert_sent=False
                )
                session.add(new_lead)
                session.flush()
                # Run full enrichment in background
                await enrich_single_lead_record(new_lead, session)
                added += 1

        session.commit()
        return {"status": "success", "jobs_found": len(jobs), "leads_added": added, "leads_updated": updated}
    finally:
        session.close()

class CampaignAdvanceRequest(BaseModel):
    force_step: Optional[int] = None
    custom_email: Optional[str] = None

@app.post("/api/campaigns/{lead_id}/advance")
def trigger_campaign_step(lead_id: int, req: Optional[CampaignAdvanceRequest] = None):
    """Advances a lead to the next automated outreach drip step (Day 1 -> Day 3 -> Day 7)."""
    session = SessionLocal()
    try:
        force = req.force_step if req else None
        custom_email = req.custom_email if req else None
        res = advance_campaign_step(session, lead_id, force_step=force, custom_email=custom_email)
        return res
    finally:
        session.close()

@app.get("/api/campaigns/{lead_id}/templates")
def preview_campaign_templates(lead_id: int):
    """Previews the 3-step outreach sequence for a specific lead."""
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        templates = get_campaign_templates(lead)
        return {
            "lead_id": lead.id,
            "company_name": lead.company_name,
            "target_email": lead.decision_maker_email or (lead.website and f"info@{lead.website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]}") or "",
            "current_step": lead.campaign_step or 0,
            "campaign_status": lead.campaign_status or "Pending",
            "next_campaign_date": lead.next_campaign_date.strftime("%Y-%m-%d %H:%M") if lead.next_campaign_date else None,
            "steps": templates
        }
    finally:
        session.close()

@app.post("/api/campaigns/run-due")
def trigger_due_campaigns():
    """Triggers automated step dispatch for all leads that have reached their scheduled follow-up date."""
    session = SessionLocal()
    try:
        results = run_due_campaign_sweeps(session)
        return {"status": "success", "advanced_leads": len(results), "details": results}
    finally:
        session.close()

class NotificationConfigRequest(BaseModel):
    whatsapp_enabled: bool = False
    whatsapp_phone: str = ""
    whatsapp_apikey: str = ""
    email_enabled: bool = True
    email_to: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    telegram_enabled: bool = True
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

@app.get("/api/notifications/config")
def get_notification_settings():
    cfg = get_notifier_config()
    if cfg.get("smtp_pass"):
        cfg["smtp_pass_masked"] = "••••••••"
    return cfg

@app.post("/api/notifications/config")
def update_notification_settings(req: NotificationConfigRequest):
    env_path = ".env"
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()

    env_vars["ALERT_WHATSAPP_ENABLED"] = str(req.whatsapp_enabled).lower()
    env_vars["ALERT_WHATSAPP_PHONE"] = req.whatsapp_phone.strip()
    env_vars["ALERT_WHATSAPP_APIKEY"] = req.whatsapp_apikey.strip()
    env_vars["ALERT_EMAIL_ENABLED"] = str(req.email_enabled).lower()
    env_vars["ALERT_EMAIL_TO"] = req.email_to.strip()
    env_vars["SMTP_HOST"] = req.smtp_host.strip()
    env_vars["SMTP_PORT"] = str(req.smtp_port)
    env_vars["SMTP_USER"] = req.smtp_user.strip()
    if req.smtp_pass and req.smtp_pass != "••••••••":
        env_vars["SMTP_PASS"] = req.smtp_pass.strip()
    env_vars["ALERT_TELEGRAM_ENABLED"] = str(req.telegram_enabled).lower()
    env_vars["TELEGRAM_BOT_TOKEN"] = req.telegram_bot_token.strip()
    env_vars["ALERT_TELEGRAM_CHAT_ID"] = req.telegram_chat_id.strip()

    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    for k, v in env_vars.items():
        os.environ[k] = v

    return {"status": "success", "message": "Notification credentials saved successfully!"}

class TestNotificationRequest(BaseModel):
    whatsapp_enabled: Optional[bool] = False
    whatsapp_phone: Optional[str] = None
    whatsapp_apikey: Optional[str] = None
    email_enabled: Optional[bool] = True
    email_to: Optional[str] = None
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    telegram_enabled: Optional[bool] = True
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

@app.post("/api/notifications/test")
def test_notification_alert(req: Optional[TestNotificationRequest] = None):
    custom_cfg = None
    if req:
        pass_val = req.smtp_pass
        if pass_val == "••••••••":
            pass_val = os.getenv("SMTP_PASS", "")
        custom_cfg = {
            "whatsapp_enabled": req.whatsapp_enabled if req.whatsapp_enabled is not None else True,
            "whatsapp_phone": (req.whatsapp_phone or os.getenv("ALERT_WHATSAPP_PHONE", "")).strip(),
            "whatsapp_apikey": (req.whatsapp_apikey or os.getenv("ALERT_WHATSAPP_APIKEY", "")).strip(),
            "email_enabled": req.email_enabled if req.email_enabled is not None else False,
            "email_to": (req.email_to or os.getenv("ALERT_EMAIL_TO", "")).strip(),
            "smtp_host": (req.smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")).strip(),
            "smtp_port": req.smtp_port or int(os.getenv("SMTP_PORT", "587")),
            "smtp_user": (req.smtp_user or os.getenv("SMTP_USER", "")).strip(),
            "telegram_enabled": req.telegram_enabled if req.telegram_enabled is not None else True,
            "telegram_bot_token": (req.telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip(),
            "telegram_chat_id": (req.telegram_chat_id or os.getenv("ALERT_TELEGRAM_CHAT_ID", "")).strip()
        }

    test_lead = type('LeadMock', (), {
        'id': 999,
        'company_name': 'Test Lead (BrownBox Innovation Demo)',
        'area': 'Chakan MIDC',
        'relevance_score': 95,
        'priority': 'High',
        'decision_maker': 'VP Operations / IT Director',
        'phone': '+91 20 2712 0000',
        'website': 'https://brownboxinnovation.com',
        'tech_stack': 'SAP ERP, Power BI, Industrial Automation',
        'score_reasoning': 'Active SAP environment requiring automated Power BI dashboards',
        'generated_pitch': 'Hi Team,\n\nAt BrownBox Innovation (Pune), we help manufacturing facilities streamline reporting and ERP visibility.\n\nOur Services for Your Plant:\n1. Direct SAP/ERP Data Pipeline Integration (Eliminating manual Excel extracts)\n2. Live Executive Power BI Dashboards (OEE, Machine Downtime, Scrap)\n3. Custom Industrial Software & Telemetry\n\nWould you be open for a brief 10-minute call this Thursday to explore how we can support your operations?\n\nBest regards,\nBrownBox Innovation Team',
        'whatsapp_pitch': 'Hi from BrownBox Innovation, Pune! We provide manufacturing automation and ERP reporting solutions for plants in Chakan:\n\n🔹 Live Power BI Dashboards (OEE, Downtime, Yield)\n🔹 Direct SAP/ERP Data Integration (No manual Excel sheets)\n🔹 Custom Shop-floor Production Software\n\nOpen for a quick 5-minute chat on how we can streamline this for your team?'
    })()
    results = dispatch_all_alerts(test_lead, custom_cfg=custom_cfg)
    return {"status": "success", "results": results}

class LeadAlertDispatchOptions(BaseModel):
    channel: Optional[str] = "all" # "telegram", "email", or "all"
    email: Optional[str] = None
    custom_message: Optional[str] = None

@app.post("/api/leads/{lead_id}/send-alert")
def trigger_lead_alert(lead_id: int, opts: Optional[LeadAlertDispatchOptions] = None):
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
            
        cfg = get_notifier_config()
        cfg["whatsapp_enabled"] = False  # WhatsApp is permanently disabled

        if opts:
            if opts.custom_message:
                cfg["custom_message"] = opts.custom_message

            if opts.channel == "email":
                cfg["email_enabled"] = True
                cfg["telegram_enabled"] = False
                if opts.email:
                    cfg["email_to"] = opts.email.strip()
            elif opts.channel == "telegram":
                cfg["email_enabled"] = False
                cfg["telegram_enabled"] = True
            elif opts.channel == "all":
                cfg["email_enabled"] = True
                cfg["telegram_enabled"] = True

        results = dispatch_all_alerts(lead, custom_cfg=cfg)
        lead.alert_sent = True
        session.commit()
        return {"status": "success", "results": results, "message": "Alert dispatched via direct channels"}
    finally:
        session.close()

@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int):
    session = SessionLocal()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        session.delete(lead)
        session.commit()
        return {"status": "success", "message": f"Lead {lead_id} removed"}
    finally:
        session.close()

@app.get("/api/export")
def export_csv(area: Optional[str] = Query(None), priority: Optional[str] = Query(None)):
    session = SessionLocal()
    try:
        q = session.query(Lead)
        if area and area != "All":
            q = q.filter(Lead.area.ilike(f"%{area}%"))
        if priority and priority != "All":
            q = q.filter(Lead.priority == priority)
            
        leads = q.order_by(Lead.relevance_score.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Company Name", "Area / Zone", "Score", "Priority", 
            "Decision Maker Name", "Direct Email", "LinkedIn Profile", 
            "CIN", "Estimated Revenue", "Active Hiring Intent",
            "Tech Stack", "Phone", "Address", "Website", 
            "Campaign Step", "Campaign Status", "WhatsApp Pitch", "Email Pitch"
        ])
        for l in leads:
            writer.writerow([
                l.id, l.company_name, l.area, l.relevance_score, l.priority,
                l.decision_maker_name or "", l.decision_maker_email or "", l.decision_maker_linkedin or "",
                l.cin or "", l.revenue_range or "", l.hiring_signals or "",
                l.tech_stack, l.phone, l.address, l.website,
                f"Step {l.campaign_step or 0}/3", l.campaign_status or "Pending",
                l.whatsapp_pitch, l.generated_pitch
            ])
            
        output.seek(0)
        filename = f"pune_leads_enterprise_{area.replace(' ', '_') if area else 'all'}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        session.close()

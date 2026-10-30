import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database.models import Lead
from agent.notifier import send_direct_email, send_direct_whatsapp, send_telegram_alert, send_outreach_email, send_outreach_whatsapp

load_dotenv()

def get_campaign_templates(lead: Lead) -> Dict[int, Dict[str, str]]:
    """
    Returns the 3-step enterprise outreach sequence for BrownBox Innovation:
    Step 1 (Day 1): Problem Identification & 3 Core Services Intro
    Step 2 (Day 3): Technical Proof & Tier-1 Industrial Case Study (OEE & SAP)
    Step 3 (Day 7): Executive Plant Audit & Low-Friction WhatsApp Invitation
    """
    company = lead.company_name or "Plant Management"
    area = lead.area or "Pune MIDC"
    contact = lead.decision_maker_name or lead.decision_maker or "Operations Leadership"
    
    # Extract detected tech
    tech = lead.tech_stack or "SAP ERP, Power BI & PLC Telemetry"
    if isinstance(tech, str) and tech.startswith("["):
        try:
            tech = ", ".join(json.loads(tech))
        except Exception:
            pass

    return {
        1: {
            "title": "Step 1 (Day 1): Initial Enterprise Proposal",
            "channel": "Email & WhatsApp",
            "subject": f"Automating SAP Data Sync, Power BI Dashboards & PLC Telemetry for {company}",
            "body": f"""Hi {contact},

I noticed your manufacturing operations in {area} and wanted to reach out regarding your ERP reporting speed, shop-floor machine availability, and executive plant dashboards.

At BrownBox Innovation (Pune), we help manufacturing plants eliminate manual Excel reports and achieve live operational visibility through 3 core services:

1. SAP & ERP Real-Time Data Pipeline: Direct automated extraction from SAP ECC / S/4HANA (PP, MM, SD) into unified reporting databases.
2. Executive Power BI Dashboards: Live OEE (Overall Equipment Effectiveness), downtime logging, scrap rates, and dispatch KPIs on mobile & web.
3. Industrial Automation & PLC Telemetry: Machine sensor interfacing, Siemens/Rockwell PLC integration, and automated cycle-time tracking.

Are you available for a brief 10-minute introductory call this week to explore how this can eliminate manual daily reporting at {company}?

Best regards,
BrownBox Innovation Team
Pune Industrial Corridor
Web: brownboxinnovation.com | Contact: +91 98765 43210"""
        },
        2: {
            "title": "Step 2 (Day 3): Technical Proof & Chakan Case Study",
            "channel": "Email Follow-up",
            "subject": f"Case Study: 18% OEE Improvement & Zero Daily Excel Exports in {area}",
            "body": f"""Hi {contact},

Following up on my note earlier this week regarding {company}'s production reporting workflows.

Wanted to share a quick metric: An automotive components manufacturer in the {area} belt was previously spending 3 to 4 hours every morning manually consolidating SAP exports and machine downtime sheets in Excel.

By deploying our direct SAP pipeline and live Power BI OEE dashboards:
- Daily manual reporting time was cut to ZERO (100% automated 6:00 AM executive refresh).
- Machine bottleneck detection speed improved by 40%.
- Overall Equipment Effectiveness (OEE) increased by 14% within the first 60 days.

Would you be open to seeing a 3-minute interactive preview of this Power BI dashboard customized for your plant setup?

Best regards,
BrownBox Innovation Team"""
        },
        3: {
            "title": "Step 3 (Day 7): Executive 15-Minute Plant Audit Invite",
            "channel": "WhatsApp & Direct Ping",
            "subject": f"Final Follow-up: Complimentary 15-Minute Plant Telemetry Audit for {company}",
            "body": f"""Hello {contact},

I understand how demanding managing plant operations at {company} can be.

We are offering a complimentary 15-Minute Virtual Plant Data & Automation Audit for selected facilities in {area}. During this brief session, we evaluate:
1. Whether your SAP / ERP tables can be synced directly without manual intervention.
2. How to map your existing PLCs / machines into live Power BI dashboards.
3. Quick-win opportunities to reduce unplanned machine downtime.

If this aligns with your current priorities, let me know when you have 15 minutes this Thursday or Friday, or reply directly on WhatsApp.

Best regards,
BrownBox Innovation Team | Pune, Maharashtra"""
        }
    }

def advance_campaign_step(db: Session, lead_id: int, force_step: Optional[int] = None, custom_email: Optional[str] = None) -> Dict[str, Any]:
    """
    Advances a lead to the next drip step (or force_step) and triggers real-time delivery.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return {"success": False, "error": f"Lead with id {lead_id} not found."}

    current_step = lead.campaign_step or 0
    next_step = force_step if force_step is not None else (current_step + 1)
    
    if next_step > 3:
        lead.campaign_step = 4
        lead.campaign_status = "Completed"
        lead.next_campaign_date = None
        db.commit()
        return {"success": True, "status": "Completed", "message": "All 3 drip campaign steps have been executed."}

    templates = get_campaign_templates(lead)
    step_info = templates.get(next_step)
    if not step_info:
        return {"success": False, "error": f"Invalid step: {next_step}"}

    # Dispatch via channels
    sent_channels = []
    
    # 1. Email Dispatch
    target_email = (custom_email.strip() if custom_email and custom_email.strip() else None) or lead.decision_maker_email or (lead.website and f"info@{lead.website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]}")
    if custom_email and custom_email.strip() and "@" in custom_email:
        lead.decision_maker_email = custom_email.strip()

    if target_email and "@" in target_email:
        try:
            email_res = send_outreach_email(
                to_email=target_email,
                subject=step_info["subject"],
                message_body=step_info["body"]
            )
            if email_res.get("success"):
                sent_channels.append(f"Email ({target_email})")
            else:
                err_detail = email_res.get("error", "Failed")
                print(f"[DRIP CAMPAIGN] Email to {target_email} status: {err_detail}")
        except Exception as e:
            print(f"[DRIP CAMPAIGN ERROR] Email dispatch error: {e}")

    # 2. WhatsApp Dispatch for Step 1 or Step 3
    if next_step in [1, 3] and lead.phone:
        clean_phone = lead.phone.replace(" ", "").replace("-", "")
        try:
            wa_res = send_outreach_whatsapp(
                to_phone=clean_phone,
                message_text=f"*{step_info['subject']}*\n\n{step_info['body'][:1200]}"
            )
            if wa_res.get("success"):
                sent_channels.append(f"WhatsApp ({clean_phone})")
            else:
                print(f"[DRIP CAMPAIGN] WhatsApp to {clean_phone} status: {wa_res.get('error')}")
        except Exception as e:
            print(f"[DRIP CAMPAIGN ERROR] WhatsApp dispatch error: {e}")

    # 3. Send Telegram confirmation to your team if enabled
    try:
        from agent.notifier import get_notifier_config
        cfg = get_notifier_config()
        if cfg.get("telegram_enabled"):
            send_telegram_alert(
                company_name=lead.company_name,
                area=lead.area or "Pune",
                score=lead.relevance_score,
                priority=lead.priority,
                decision_maker=lead.decision_maker_name or lead.decision_maker or "Operations",
                phone=lead.phone or "N/A",
                website=lead.website or "N/A",
                tech_stack=str(lead.tech_stack or ""),
                pitch="",
                custom_message=(
                    f"🚀 <b>[DRIP OUTREACH DISPATCHED — {step_info['title']}]</b>\n\n"
                    f"🏢 <b>Company:</b> {lead.company_name} ({lead.area})\n"
                    f"🎯 <b>Target:</b> {lead.decision_maker_name or lead.decision_maker} ({target_email or 'No email'})\n"
                    f"📬 <b>Dispatched Via:</b> {', '.join(sent_channels) if sent_channels else 'Drafted in CRM'}\n"
                    f"📄 <b>Subject:</b> {step_info['subject']}"
                )
            )
    except Exception as e:
        print(f"[DRIP CAMPAIGN] Telegram team confirmation skipped/failed: {e}")

    # Update database record
    now = datetime.utcnow()
    lead.campaign_step = next_step
    lead.campaign_status = "Active" if next_step < 3 else "Completed"
    lead.last_campaign_date = now
    
    # Schedule next follow-up: Step 1 -> Day 3 (+2 days), Step 2 -> Day 7 (+4 days)
    if next_step == 1:
        lead.next_campaign_date = now + timedelta(days=2)
    elif next_step == 2:
        lead.next_campaign_date = now + timedelta(days=4)
    else:
        lead.next_campaign_date = None

    db.commit()

    return {
        "success": True,
        "lead_id": lead.id,
        "new_step": next_step,
        "title": step_info["title"],
        "dispatched_channels": sent_channels,
        "next_scheduled": lead.next_campaign_date.strftime("%Y-%m-%d %H:%M") if lead.next_campaign_date else "Campaign Completed"
    }

def run_due_campaign_sweeps(db: Session) -> List[Dict[str, Any]]:
    """
    Finds all leads whose next_campaign_date is due and advances them automatically.
    """
    now = datetime.utcnow()
    due_leads = db.query(Lead).filter(
        Lead.campaign_status == "Active",
        Lead.next_campaign_date <= now,
        Lead.campaign_step < 3
    ).all()

    results = []
    for l in due_leads:
        res = advance_campaign_step(db, l.id)
        results.append(res)
    return results

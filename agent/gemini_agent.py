import os
import json
import re
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Strict Qualification Rubric aligned with BrownBox Innovation's 3 Core Services
RUBRIC_GUIDELINES = """
Lead Qualification Rubric (0 - 100 Scale):
+35 Points: SAP Fit (Mentions SAP ECC, S/4HANA, SAP Business One, ERP data extraction, or inventory/production tables).
+35 Points: Power BI Fit (Mentions Power BI, executive dashboards, OEE tracking, downtime reporting, scrap metrics, or analytics).
+30 Points: Industrial Automation Fit (Mentions PLC/SCADA, MES, CNC automation, shop-floor robotics, sensors, or line telemetry).
Bonus Signals: Pune industrial cluster (+15 pts), active IT/automation hiring (+10 pts).

Priority Thresholds:
- High Priority: Score >= 75 (Immediate auto-dispatch to Telegram & Email, high-relevance proposal)
- Medium Priority: Score 45 - 74 (Review pipeline, automation & BI proposal)
- Low Priority: Score < 45 (Archive, baseline intro)
"""

SYSTEM_PROMPT = f"""
You are the Chief Enterprise Intelligence Agent for BrownBox Innovation, an industrial technology and enterprise solutions firm based in Pune, India.
Your mission is to analyze prospective manufacturing facilities and qualify them strictly for our 3 core services:

BrownBox Innovation 3 Core Services:
1. SAP Services & ERP Pipeline Integration:
   - Automated real-time data sync from SAP ECC / S/4HANA and legacy ERPs directly into databases and dashboards.
   - Eliminating manual daily Excel exports from SAP production (PP), material management (MM), and sales (SD) modules.
   - Multi-plant centralized data pipeline architecture.

2. Executive Power BI Dashboards:
   - Live visual executive dashboards tracking plant OEE (Overall Equipment Effectiveness), machine availability, performance, and scrap rates.
   - Real-time mobile and web visibility for Plant Heads, Operations VPs, and Managing Directors.
   - Automated daily production summary, bottleneck detection, and dispatch metrics.

3. Industrial Automation & Shop-Floor Telemetry:
   - Machine sensor interfacing and PLC / SCADA integration (Siemens, Rockwell Automation, Mitsubishi, Omron).
   - Custom MES (Manufacturing Execution Systems) and digital work-order tracking.
   - Automated machine downtime logging, cycle-time telemetry, and predictive maintenance triggers.

{RUBRIC_GUIDELINES}

IMPORTANT MESSAGING RULES:
- Never mention or name external third-party partners or confidential partner companies.
- In both the email_pitch and whatsapp_pitch, you MUST clearly structure the proposal around our 3 core services:
  (1) SAP & ERP Integration, (2) Power BI Executive Dashboards, and (3) Industrial Automation.
- Emphasize how these services eliminate manual reporting, increase machine uptime, and provide real-time plant visibility.

You must extract key facts and return a STRICT JSON output adhering to this exact schema:
{{
  "score": <integer 0-100>,
  "priority": "<High | Medium | Low>",
  "score_breakdown": {{
    "sap_fit": <integer 0-35>,
    "power_bi_fit": <integer 0-35>,
    "industrial_automation_fit": <integer 0-30>
  }},
  "reasoning": "<Short explanation for points awarded across SAP, Power BI, and Industrial Automation>",
  "tech_stack": ["<detected technologies, e.g. SAP ERP, Power BI, PLC/SCADA, Siemens, SQL Server>"],
  "pain_points": "<Identified business, reporting, or automation bottlenecks>",
  "decision_maker": "<Recommended outreach title, e.g. Head of IT / Plant Operations Director / General Manager Works>",
  "email_pitch": "<Compelling, personalized B2B proposal clearly listing our 3 services (SAP, Power BI, Industrial Automation) for their plant, ending with a low-friction CTA>",
  "whatsapp_pitch": "<Concise, bulleted conversational pitch clearly outlining our SAP, Power BI, and Industrial Automation services>"
}}
Return ONLY the raw JSON object. Do not wrap in markdown or backticks.
"""

def extract_tech_keywords_heuristically(text: str) -> List[str]:
    """Scans raw text for known SAP, Power BI, and Industrial Automation keywords."""
    found = []
    keywords = [
        "SAP", "SAP S/4HANA", "SAP ECC", "SAP Business One", "SAP ERP", "SAP PP", "SAP MM", "SAP SD",
        "Power BI", "PowerBI", "DAX", "Tableau", "Business Intelligence", "OEE Tracking", "OEE Dashboards",
        "SQL Server", "SCADA", "PLC", "Siemens", "Allen-Bradley", "Rockwell Automation", "Omron", "Mitsubishi",
        "MES", "Industry 4.0", "Industrial IoT", "CNC Machinery", "Robotic Automation",
        "Machine Telemetry", "Industrial Automation", "Modbus", "OPC-UA", "Sensors"
    ]
    text_lower = text.lower()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(kw)
    return list(dict.fromkeys(found))

def heuristic_lead_scoring(raw_text: str, company_name: str, location_hint: str = "") -> Dict[str, Any]:
    """
    Deterministic rule-based backup scoring matching the exact 0-100 rubric for BrownBox Innovation:
    1. SAP Integration (+35 pts)
    2. Power BI Dashboards (+35 pts)
    3. Industrial Automation & Telemetry (+30 pts)
    Location Bonus: Pune MIDC Corridor (+10 pts)
    """
    text_lower = f"{company_name} {raw_text}".lower()
    loc_lower = f"{location_hint}".lower()
    
    # 1. SAP Fit (+35 pts)
    has_sap = any(k in text_lower for k in [
        "sap s/4hana", "sap ecc", "sap erp", "sap bi", "sap bw", "sap business one",
        "erp integration", "sap database", "sap mm", "sap pp", "sap sd", "sap hana"
    ]) or (re.search(r'\bsap\b', text_lower) and any(k in text_lower for k in ["erp", "reporting", "plant", "manufacturing", "enterprise"]))
    sap_pts = 35 if has_sap else 0
    
    # 2. Power BI Fit (+35 pts)
    has_power_bi = any(k in text_lower for k in [
        "power bi", "powerbi", "bi dashboard", "business intelligence", "oee dashboard",
        "machine downtime tracking", "production analytics", "kpi reporting", "tableau", "visual reporting"
    ]) or ("dashboard" in text_lower and any(k in text_lower for k in ["reporting", "plant", "production", "analytics", "kpi"]))
    power_bi_pts = 35 if has_power_bi else (20 if any(k in text_lower for k in ["reporting", "analytics", "downtime", "scrap", "oee"]) else 0)
    
    # 3. Industrial Automation Fit (+30 pts)
    has_automation = any(k in text_lower for k in [
        "automation", "industrial automation", "plc", "scada", "mes", "manufacturing execution", 
        "industrial iot", "iot telemetry", "cnc machinery", "robotic welding", "robotics",
        "siemens", "rockwell", "allen-bradley", "mitsubishi", "omron", "sensor", "telemetry", "opc-ua"
    ])
    automation_pts = 30 if has_automation else (15 if any(k in text_lower for k in ["manufacturing", "machining", "fabrication", "assembly", "tooling"]) else 0)
    
    # Location bonus (Pune Industrial Belt)
    pune_hubs = ["midc", "chakan", "bhosari", "talegaon", "ranjangaon", "hadapsar", "pimpri", "chinchwad", "sanaswadi"]
    is_in_midc = any(hub in loc_lower or hub in text_lower for hub in pune_hubs)
    loc_pts = 10 if is_in_midc else 0
    
    total_score = min(sap_pts + power_bi_pts + automation_pts + loc_pts, 100)
    
    # Priority Thresholds
    if total_score >= 75:
        priority = "High"
    elif total_score >= 45:
        priority = "Medium"
    else:
        priority = "Low"
        
    tech_stack = extract_tech_keywords_heuristically(f"{company_name} {raw_text}")
    if not tech_stack:
        defaults = []
        if has_sap: defaults.append("SAP ERP")
        if has_power_bi: defaults.append("Power BI")
        if has_automation: defaults.append("Industrial Automation / PLC")
        tech_stack = defaults if defaults else ["Industrial Manufacturing"]
            
    loc_display = location_hint or "Pune"

    # Structured B2B outreach proposals highlighting our 3 core services:
    email_pitch = f"""Subject: SAP Integration, Power BI Dashboards & Industrial Automation for {company_name}

Hi Team {company_name},

I noticed your manufacturing operations in {loc_display} and wanted to reach out regarding your ERP data visibility, plant reporting, and shop-floor automation workflows.

At BrownBox Innovation (Pune), we specialize in 3 core enterprise services tailored for industrial plants:

1. SAP / ERP Pipeline Integration:
   - Direct, automated real-time data sync from SAP ECC / S/4HANA into centralized databases.
   - Eliminates daily manual Excel exports from SAP production (PP), materials (MM), and sales (SD).

2. Executive Power BI Dashboards:
   - Live visual executive dashboards tracking plant OEE (Overall Equipment Effectiveness), machine availability, scrap rate, and yield.
   - Instant web and mobile visibility for Plant Heads, Operations VPs, and Managing Directors.

3. Industrial Automation & Shop-Floor Telemetry:
   - Direct machine PLC / SCADA integration (Siemens, Rockwell, Mitsubishi) and custom MES software.
   - Real-time machine downtime logging, automated cycle-time tracking, and bottleneck alerts.

Would you be open for a brief 10-minute discovery call this Thursday to explore how we can support operations at {company_name}?

Best regards,
BrownBox Innovation Team
Pune, Maharashtra | +91 91234 56789 | www.brownboxinnovation.com"""

    whatsapp_pitch = f"Hi from BrownBox Innovation, Pune! We support manufacturing plants in {loc_display} with 3 specialized industrial services:\n\n• 1. SAP / ERP Integration (Automated data pipelines, eliminating manual Excel extracts)\n• 2. Live Power BI Dashboards (Real-time OEE, Machine Downtime, Scrap tracking)\n• 3. Industrial Automation & MES (PLC/SCADA machine telemetry and digital work orders)\n\nOpen for a quick 5-minute chat on how we can streamline this for {company_name}?"

    reasoning_parts = []
    if sap_pts:
        reasoning_parts.append(f"+{sap_pts}: SAP ERP Integration Fit")
    if power_bi_pts:
        reasoning_parts.append(f"+{power_bi_pts}: Power BI & Analytics Fit")
    if automation_pts:
        reasoning_parts.append(f"+{automation_pts}: Industrial Automation / PLC / MES Fit")
    if loc_pts:
        reasoning_parts.append(f"+{loc_pts}: Pune Industrial Corridor (MIDC) Presence")

    return {
        "score": total_score,
        "priority": priority,
        "score_breakdown": {
            "sap_fit": sap_pts,
            "power_bi_fit": power_bi_pts,
            "industrial_automation_fit": automation_pts,
            "location_fit": loc_pts
        },
        "reasoning": " | ".join(reasoning_parts) if reasoning_parts else "Standard manufacturing workshop",
        "tech_stack": tech_stack,
        "pain_points": "Manual Excel exports from SAP ERP, lack of centralized Power BI OEE dashboards and automated machine telemetry" if priority == "High" else "Shop-floor machine downtime tracking and manual production logs",
        "decision_maker": "Head of IT / Plant Operations Director / General Manager Works",
        "email_pitch": email_pitch,
        "whatsapp_pitch": whatsapp_pitch
    }

def analyze_lead_with_gemini(raw_text: str, company_name: str, location_hint: str = "") -> Dict[str, Any]:
    """
    Main intelligence entrypoint:
    Uses Google Gemini Cloud API to evaluate lead, score 0-100, and craft custom pitches.
    Gracefully falls back to calibrated heuristic engine if key is absent or quota exceeded.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    if not api_key:
        print(f"[INFO] GEMINI_API_KEY not configured in .env. Using calibrated heuristic engine for {company_name}.")
        return heuristic_lead_scoring(raw_text, company_name, location_hint)

    prompt = f"""
Analyze this prospective industrial lead:
Company Name: {company_name}
Location / Region: {location_hint or 'Pune Industrial Area'}
Scraped Content & Web Intelligence:
\"\"\"
{raw_text[:8000]}
\"\"\"

Follow the 0-100 scoring rubric strictly and output the JSON schema.
"""

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(
            model=model_name,
            contents=[SYSTEM_PROMPT, prompt],
        )
        
        if response and response.text:
            text_resp = response.text.strip()
            text_resp = re.sub(r'^```json\s*', '', text_resp)
            text_resp = re.sub(r'\s*```$', '', text_resp)
            data = json.loads(text_resp)
            
            data["score"] = int(data.get("score", 50))
            if data["score"] >= 75:
                data["priority"] = "High"
            elif data["score"] >= 45:
                data["priority"] = "Medium"
            else:
                data["priority"] = "Low"
                
            return data
    except Exception as e:
        print(f"[WARN] google.genai error: {e}. Trying legacy google.generativeai fallback...")

    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(prompt)
        if response and response.text:
            text_resp = response.text.strip()
            text_resp = re.sub(r'^```json\s*', '', text_resp)
            text_resp = re.sub(r'\s*```$', '', text_resp)
            data = json.loads(text_resp)
            return data
    except Exception as e:
        print(f"[WARN] google.generativeai error: {e}. Falling back to calibrated heuristic engine.")

    return heuristic_lead_scoring(raw_text, company_name, location_hint)

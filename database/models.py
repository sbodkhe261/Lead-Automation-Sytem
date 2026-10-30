from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import json

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    website = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    area = Column(String(100), default="Chakan MIDC") # e.g. Chakan, Bhosari, Talegaon, Ranjangaon, Hadapsar, Pimpri
    google_rating = Column(Float, default=0.0)
    source = Column(String(100), default="google_maps")
    
    # Scraped Content
    raw_text = Column(Text)
    
    # AI Enrichment & Stack
    tech_stack = Column(Text) # JSON list or comma-separated
    pain_points = Column(Text)
    decision_maker = Column(String(255))
    
    # Qualification Engine (0 - 100)
    relevance_score = Column(Integer, default=0)
    priority = Column(String(50), default="Low") # High, Medium, Low
    score_breakdown = Column(Text) # JSON string: {power_bi_sap: 40, pune_midc: 30, ...}
    score_reasoning = Column(Text)
    
    # AI Outreach Pitches
    generated_pitch = Column(Text) # Tailored B2B cold email format
    whatsapp_pitch = Column(Text) # Direct WhatsApp format
    
    # Alert & Dispatch Status
    alert_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 1. Decision Maker & Contact Enrichment (Apollo / Hunter / LinkedIn)
    decision_maker_name = Column(String(255))
    decision_maker_email = Column(String(255))
    decision_maker_linkedin = Column(String(500))

    # 2. Hiring Intent & Job Openings (Naukri / Indeed / LinkedIn Jobs)
    hiring_signals = Column(Text) # JSON array of active jobs: [{title, department, url, posted}]

    # 3. Financial & Scale Qualification (MCA / Zauba Corp / Tofler)
    cin = Column(String(50)) # Corporate Identity Number
    revenue_range = Column(String(100)) # e.g. "INR 500 Cr - 1,000 Cr"
    automation_budget = Column(String(100)) # e.g. "INR 25 Lakhs - 80 Lakhs (SAP & BI)"
    directors = Column(Text) # Comma-separated or JSON list of directors

    # 4. Technographics & Subdomain Scan
    technographics = Column(Text) # JSON: {subdomains: [], email_provider: "", erp_hint: ""}

    # 5. Multi-Step Outreach Sequencing (Drip Campaigns)
    campaign_step = Column(Integer, default=0) # 0: New, 1: Intro Sent, 2: Case Study Sent, 3: Audit Offer Sent, 4: Completed
    campaign_status = Column(String(50), default="Pending") # Pending, Active, Paused, Responded, Completed
    last_campaign_date = Column(DateTime)
    next_campaign_date = Column(DateTime)

    def to_dict(self):
        # Safely parse tech stack
        parsed_tech = []
        if self.tech_stack:
            try:
                parsed_tech = json.loads(self.tech_stack) if self.tech_stack.startswith("[") else [t.strip() for t in self.tech_stack.split(",") if t.strip()]
            except:
                parsed_tech = [t.strip() for t in self.tech_stack.split(",") if t.strip()]

        # Safely parse score breakdown
        breakdown = {}
        if self.score_breakdown:
            try:
                breakdown = json.loads(self.score_breakdown)
            except:
                breakdown = {}

        # Safely parse hiring signals
        hiring = []
        if self.hiring_signals:
            try:
                hiring = json.loads(self.hiring_signals)
            except:
                hiring = [{"title": self.hiring_signals}] if self.hiring_signals else []

        # Safely parse technographics
        tech_data = {}
        if self.technographics:
            try:
                tech_data = json.loads(self.technographics)
            except:
                tech_data = {"raw": self.technographics}

        # Safely parse directors
        dirs = []
        if self.directors:
            try:
                dirs = json.loads(self.directors) if self.directors.startswith("[") else [d.strip() for d in self.directors.split(",") if d.strip()]
            except:
                dirs = [d.strip() for d in self.directors.split(",") if d.strip()]

        return {
            "id": self.id,
            "company_name": self.company_name,
            "website": self.website,
            "phone": self.phone,
            "address": self.address,
            "area": self.area or "Pune MIDC",
            "google_rating": self.google_rating,
            "source": self.source,
            "tech_stack": parsed_tech,
            "pain_points": self.pain_points,
            "decision_maker": self.decision_maker,
            "decision_maker_name": self.decision_maker_name,
            "decision_maker_email": self.decision_maker_email,
            "decision_maker_linkedin": self.decision_maker_linkedin,
            "cin": self.cin,
            "revenue_range": self.revenue_range,
            "automation_budget": self.automation_budget,
            "directors": dirs,
            "hiring_signals": hiring,
            "technographics": tech_data,
            "campaign_step": self.campaign_step or 0,
            "campaign_status": self.campaign_status or "Pending",
            "last_campaign_date": self.last_campaign_date.strftime("%Y-%m-%d %H:%M") if self.last_campaign_date else None,
            "next_campaign_date": self.next_campaign_date.strftime("%Y-%m-%d %H:%M") if self.next_campaign_date else None,
            "score": self.relevance_score,
            "priority": self.priority,
            "score_breakdown": breakdown,
            "score_reasoning": self.score_reasoning,
            "pitch": self.generated_pitch,
            "whatsapp_pitch": self.whatsapp_pitch,
            "alert_sent": self.alert_sent,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }

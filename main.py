import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from database.db import init_db, SessionLocal
from database.models import Lead
from scraper.google_maps import scrape_google_maps
from scraper.web_scraper import scrape_website
from agent.gemini_agent import analyze_lead_with_gemini

async def main():
    print("=" * 60)
    print(">>> PUNE INDUSTRIAL LEAD INTELLIGENCE SYSTEM <<<")
    print(f"Database: {os.getenv('DB_URL', 'sqlite:///leads.db')}")
    print("=" * 60)
    
    # Initialize Database
    init_db()
    
    print("\n--- PHASE 1: Data Acquisition (Google Maps & MIDC) ---")
    query = "Manufacturing companies in Pune MIDC Chakan"
    leads = await scrape_google_maps(query, 2)
    print(f"Collected {len(leads)} target industrial companies.")
    
    print("\n--- PHASE 2 & 3: Gemini Cloud Qualification & Scoring ---")
    session = SessionLocal()
    for l_data in leads:
        company_name = l_data.get('company_name', 'Unknown')
        print(f"\n[EVALUATING] {company_name}")
        
        # Scrape website or use contextual profile
        website = l_data.get('url', '')
        raw_text = l_data.get('raw_text', '')
        if website and website.startswith("http") and "google.com" not in website:
            site_content = await scrape_website(website)
            if site_content:
                raw_text = f"{raw_text}\n{site_content}"
                
        # Run Autonomous Gemini Agent
        analysis = analyze_lead_with_gemini(raw_text, company_name, l_data.get('address', 'Pune MIDC'))
        
        # Save to DB
        db_lead = Lead(
            company_name=company_name,
            website=website,
            phone=l_data.get('phone', ''),
            address=l_data.get('address', 'Pune, Maharashtra'),
            google_rating=l_data.get('rating', 4.5),
            source=l_data.get('source', 'google_maps'),
            raw_text=raw_text[:2000],
            tech_stack=",".join(analysis.get('tech_stack', [])) if isinstance(analysis.get('tech_stack'), list) else str(analysis.get('tech_stack', '')),
            pain_points=analysis.get('pain_points', ''),
            decision_maker=analysis.get('decision_maker', ''),
            relevance_score=int(analysis.get('score', 0)),
            priority=analysis.get('priority', 'Low'),
            score_reasoning=analysis.get('reasoning', ''),
            generated_pitch=analysis.get('email_pitch', ''),
            whatsapp_pitch=analysis.get('whatsapp_pitch', '')
        )
        session.add(db_lead)
        session.commit()
        
        print(f"[QUALIFIED] Score: {analysis.get('score')}/100 | Priority: {analysis.get('priority')}")
        print(f"  Reasoning: {analysis.get('reasoning')}")
        print(f"  Target Persona: {analysis.get('decision_maker')}")
        print(f"  Tech Stack: {analysis.get('tech_stack')}")
        print(f"  WhatsApp Pitch: {analysis.get('whatsapp_pitch')}")
    
    session.close()
    print("\n[COMPLETE] Lead Automation Pipeline run finished successfully!")

if __name__ == "__main__":
    asyncio.run(main())

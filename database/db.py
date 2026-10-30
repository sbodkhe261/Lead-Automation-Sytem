import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///leads.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate SQLite columns if table already existed previously
    if "sqlite" in DB_URL:
        with engine.connect() as conn:
            existing_columns = []
            try:
                res = conn.execute(text("PRAGMA table_info(leads)"))
                existing_columns = [row[1] for row in res.fetchall()]
            except Exception:
                pass
            
            desired_columns = [
                ("phone", "VARCHAR(50)"),
                ("address", "TEXT"),
                ("area", "VARCHAR(100) DEFAULT 'Chakan MIDC'"),
                ("google_rating", "FLOAT DEFAULT 0.0"),
                ("source", "VARCHAR(100) DEFAULT 'google_maps'"),
                ("score_breakdown", "TEXT"),
                ("score_reasoning", "TEXT"),
                ("whatsapp_pitch", "TEXT"),
                ("decision_maker_name", "VARCHAR(255)"),
                ("decision_maker_email", "VARCHAR(255)"),
                ("decision_maker_linkedin", "VARCHAR(500)"),
                ("hiring_signals", "TEXT"),
                ("cin", "VARCHAR(50)"),
                ("revenue_range", "VARCHAR(100)"),
                ("automation_budget", "VARCHAR(100)"),
                ("directors", "TEXT"),
                ("technographics", "TEXT"),
                ("campaign_step", "INTEGER DEFAULT 0"),
                ("campaign_status", "VARCHAR(50) DEFAULT 'Pending'"),
                ("last_campaign_date", "DATETIME"),
                ("next_campaign_date", "DATETIME")
            ]
            for col_name, col_type in desired_columns:
                if col_name not in existing_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                    except Exception:
                        pass
                        
            # Normalize existing area values based on name/address/text
            try:
                conn.execute(text("""
                    UPDATE leads SET area = 'Bhosari MIDC' 
                    WHERE (company_name LIKE '%Bhosari%' OR address LIKE '%Bhosari%' OR raw_text LIKE '%Bhosari%') 
                    AND (area IS NULL OR area = '' OR area = 'Chakan MIDC' AND company_name LIKE '%Bhosari%')
                """))
                conn.execute(text("""
                    UPDATE leads SET area = 'Chakan MIDC' 
                    WHERE (company_name LIKE '%Chakan%' OR address LIKE '%Chakan%' OR raw_text LIKE '%Chakan%')
                    AND (area IS NULL OR area = '')
                """))
                conn.execute(text("""
                    UPDATE leads SET area = 'Talegaon MIDC' 
                    WHERE (company_name LIKE '%Talegaon%' OR address LIKE '%Talegaon%' OR raw_text LIKE '%Talegaon%')
                """))
                conn.execute(text("""
                    UPDATE leads SET area = 'Ranjangaon MIDC' 
                    WHERE (company_name LIKE '%Ranjangaon%' OR address LIKE '%Ranjangaon%' OR raw_text LIKE '%Ranjangaon%')
                """))
                conn.execute(text("""
                    UPDATE leads SET area = 'Hadapsar' 
                    WHERE (company_name LIKE '%Hadapsar%' OR address LIKE '%Hadapsar%' OR raw_text LIKE '%Hadapsar%')
                """))
                conn.execute(text("""
                    UPDATE leads SET area = 'Pimpri-Chinchwad' 
                    WHERE (company_name LIKE '%Pimpri%' OR address LIKE '%Pimpri%' OR company_name LIKE '%Chinchwad%' OR address LIKE '%Chinchwad%')
                """))
                conn.commit()
            except Exception:
                pass
                        
    print(f"Database initialized and schema verified at {DB_URL}")

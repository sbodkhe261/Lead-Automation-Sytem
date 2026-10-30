"""
Backward compatible bridge from agent/crew.py to Google Gemini Cloud Agent
"""
from typing import Dict, Any

try:
    from .gemini_agent import analyze_lead_with_gemini, heuristic_lead_scoring
except ImportError:
    try:
        from gemini_agent import analyze_lead_with_gemini, heuristic_lead_scoring
    except ImportError:
        from agent.gemini_agent import analyze_lead_with_gemini, heuristic_lead_scoring

def analyze_lead(raw_text: str, company_name: str, location_hint: str = "") -> Dict[str, Any]:
    """
    Main entry point for lead qualification.
    Routes to Google Gemini Cloud with structured JSON output and scoring.
    """
    return analyze_lead_with_gemini(raw_text, company_name, location_hint)

if __name__ == "__main__":
    test_text = "We are an auto-component manufacturer in MIDC Chakan Pune running SAP ERP. We are actively hiring a Power BI developer to build live production dashboards for plant management."
    result = analyze_lead(test_text, "Chakan Precision Auto Ltd", "MIDC Chakan, Pune")
    print("Scoring Result:", result)

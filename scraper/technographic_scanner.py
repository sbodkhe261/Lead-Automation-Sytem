import asyncio
import socket
import urllib.parse
from typing import Dict, Any, List
import httpx

SUBDOMAIN_CANDIDATES = [
    "sap", "erp", "s4hana", "ecc", "bi", "powerbi", 
    "vpn", "portal", "remote", "mail", "webmail", 
    "scada", "mes", "iot", "dashboard"
]

def clean_domain(url_or_domain: str) -> str:
    """Extracts clean root domain from URL or string."""
    if not url_or_domain:
        return ""
    if url_or_domain.startswith("http://") or url_or_domain.startswith("https://"):
        parsed = urllib.parse.urlparse(url_or_domain)
        netloc = parsed.netloc
    else:
        netloc = url_or_domain.split('/')[0]
    
    # Strip port if any
    netloc = netloc.split(':')[0]
    # Strip www.
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc.lower().strip()

def resolve_host_sync(hostname: str) -> str:
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        return ""

async def scan_technographics(domain_or_url: str) -> Dict[str, Any]:
    """
    Asynchronously scans domain for enterprise technographic signals:
    - Active enterprise subdomains (sap.company.com, vpn.company.com, bi.company.com)
    - MX / Email infrastructure (Microsoft 365 = massive Power BI indicator)
    - HTTP Server & Tech footprint
    """
    domain = clean_domain(domain_or_url)
    if not domain or "." not in domain or "google.com" in domain:
        return {
            "domain": domain,
            "active_subdomains": [],
            "email_infrastructure": "Standard / Self-Hosted",
            "microsoft_365": False,
            "sap_subdomain_detected": False,
            "powerbi_subdomain_detected": False,
            "vpn_remote_detected": False,
            "tech_signals": []
        }

    active_subdomains = []
    
    # 1. Check Subdomains in parallel
    async def check_sub(sub: str):
        fqdn = f"{sub}.{domain}"
        ip = await asyncio.to_thread(resolve_host_sync, fqdn)
        if ip:
            return {"sub": sub, "fqdn": fqdn, "ip": ip}
        return None

    tasks = [check_sub(sub) for sub in SUBDOMAIN_CANDIDATES]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in results:
        if isinstance(r, dict) and r is not None:
            active_subdomains.append(r["fqdn"])

    # 2. Check MX Records or mail host
    mail_fqdn = f"mail.{domain}"
    mail_ip = await asyncio.to_thread(resolve_host_sync, mail_fqdn)
    
    # Check common Microsoft 365 MX naming pattern
    m365_fqdn = f"{domain.replace('.', '-')}.mail.protection.outlook.com"
    m365_ip = await asyncio.to_thread(resolve_host_sync, m365_fqdn)
    is_m365 = bool(m365_ip)

    # 3. Check Web Headers if accessible
    tech_signals = []
    sap_sub = any("sap" in s for s in active_subdomains)
    bi_sub = any(b in s for b in ["bi", "powerbi", "dashboard"] for s in active_subdomains)
    vpn_sub = any(v in s for v in ["vpn", "portal", "remote"] for s in active_subdomains)

    if sap_sub:
        tech_signals.append("SAP Subdomain Active (High Enterprise ERP Fit)")
    if bi_sub:
        tech_signals.append("BI/Dashboard Subdomain Active")
    if vpn_sub:
        tech_signals.append("Enterprise Remote VPN/Portal Active")
    if is_m365:
        tech_signals.append("Microsoft 365 Cloud Enterprise (Prime Power BI Candidate)")

    # Probe live home URL for server header
    try:
        async with httpx.AsyncClient(timeout=5.0, verify=False, follow_redirects=True) as client:
            resp = await client.head(f"https://{domain}")
            server = resp.headers.get("server", "")
            x_powered = resp.headers.get("x-powered-by", "")
            if server:
                tech_signals.append(f"Server: {server}")
            if "asp.net" in x_powered.lower() or "microsoft" in server.lower():
                tech_signals.append("Microsoft Enterprise Stack")
    except Exception:
        pass

    return {
        "domain": domain,
        "active_subdomains": active_subdomains,
        "email_infrastructure": "Microsoft 365 (Enterprise Cloud)" if is_m365 else "Corporate Mail Server",
        "microsoft_365": is_m365,
        "sap_subdomain_detected": sap_sub,
        "powerbi_subdomain_detected": bi_sub,
        "vpn_remote_detected": vpn_sub,
        "tech_signals": tech_signals
    }

if __name__ == "__main__":
    res = asyncio.run(scan_technographics("https://www.tatamotors.com"))
    print("Technographic Scan:", res)

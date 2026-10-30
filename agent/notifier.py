import os
import smtplib
import urllib.parse
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from dotenv import load_dotenv

load_dotenv()

def get_notifier_config():
    """Returns current notification configuration from environment variables."""
    return {
        "whatsapp_provider": os.getenv("WHATSAPP_PROVIDER", "twilio"),
        "twilio_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "twilio_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "twilio_from": os.getenv("TWILIO_FROM", "whatsapp:+14155238886"),
        "twilio_to": os.getenv("TWILIO_TO", ""),
        "whatsapp_enabled": os.getenv("ALERT_WHATSAPP_ENABLED", "true").lower() == "true",
        "whatsapp_phone": os.getenv("ALERT_WHATSAPP_PHONE", ""),
        "whatsapp_apikey": os.getenv("ALERT_WHATSAPP_APIKEY", ""),
        "email_enabled": os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true",
        "email_to": os.getenv("ALERT_EMAIL_TO", ""),
        "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_pass": os.getenv("SMTP_PASS", ""),
        "telegram_enabled": os.getenv("ALERT_TELEGRAM_ENABLED", "false").lower() == "true",
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "telegram_chat_id": os.getenv("ALERT_TELEGRAM_CHAT_ID", "")
    }

import html

def send_telegram_alert(company_name: str, area: str, score: int, priority: str, 
                        decision_maker: str, phone: str, website: str, tech_stack: str, pitch: str,
                        custom_token: str = None, custom_chat_id: str = None,
                        custom_message: str = None) -> dict:
    """
    Sends an instant lead alert directly to your phone via Telegram Bot.
    100% free, never gets banned by WhatsApp, takes 30 seconds to set up.
    """
    cfg = get_notifier_config()
    token = (custom_token if custom_token is not None else cfg.get("telegram_bot_token", "")).strip()
    chat_id = (custom_chat_id if custom_chat_id is not None else cfg.get("telegram_chat_id", "")).strip()

    if not token:
        return {"success": False, "error": "Telegram Bot Token is missing in settings."}
    if not chat_id:
        return {"success": False, "error": "Telegram Chat ID is missing in settings."}

    if custom_message:
        msg = custom_message
    else:
        esc_comp = html.escape(str(company_name or 'Company'))
        esc_area = html.escape(str(area or 'Pune'))
        esc_priority = html.escape(str(priority or 'High'))
        esc_dm = html.escape(str(decision_maker or 'Plant Operations / IT Head'))
        esc_phone = html.escape(str(phone or 'Available on Google Maps'))
        esc_web = html.escape(str(website or 'N/A'))
        esc_tech = html.escape(str(tech_stack or 'Manufacturing'))
        esc_pitch = html.escape(str(pitch[:600] if pitch else ''))
        
        msg = (
            f"🚨 <b>[NEW LEAD ALERT — SAP, POWER BI & AUTOMATION]</b>\n\n"
            f"🏢 <b>Company:</b> {esc_comp}\n"
            f"📍 <b>Area:</b> {esc_area}, Pune\n"
            f"★ <b>Score:</b> {score}/100 ({esc_priority} Priority)\n"
            f"🎯 <b>Decision Maker:</b> {esc_dm}\n"
            f"📞 <b>Contact Phone:</b> {esc_phone}\n"
            f"🌐 <b>Website:</b> {esc_web}\n"
            f"⚙️ <b>Tech Stack:</b> {esc_tech}\n\n"
            f"💬 <b>Tailored Outreach Pitch:</b>\n{esc_pitch}"
        )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if data.get("ok"):
            print(f"[TELEGRAM ALERT] Delivered to chat_id {chat_id}")
            return {"success": True, "message": "Lead alert sent to Telegram successfully!"}
        else:
            # Fallback to plain text if HTML parse error
            plain_text = (
                f"🚨 [NEW LEAD ALERT — SAP, POWER BI & AUTOMATION]\n\n"
                f"🏢 Company: {company_name}\n"
                f"📍 Area: {area}, Pune\n"
                f"★ Score: {score}/100 ({priority} Priority)\n"
                f"🎯 Decision Maker: {decision_maker or 'Plant Operations / IT Head'}\n"
                f"📞 Contact Phone: {phone or 'Available on Google Maps'}\n"
                f"🌐 Website: {website or 'N/A'}\n"
                f"⚙️ Tech Stack: {tech_stack or 'Manufacturing'}\n\n"
                f"💬 Tailored Outreach Pitch:\n{pitch[:600] if pitch else ''}"
            )
            fallback_res = requests.post(url, json={"chat_id": chat_id, "text": plain_text}, timeout=10)
            fb_data = fallback_res.json()
            if fb_data.get("ok"):
                print(f"[TELEGRAM ALERT] Delivered via plain text fallback to chat_id {chat_id}")
                return {"success": True, "message": "Lead alert sent to Telegram successfully!"}
            return {"success": False, "error": f"Telegram error: {data.get('description', res.text)}"}
    except Exception as e:
        print(f"[TELEGRAM ALERT ERROR] {e}")
        return {"success": False, "error": str(e)}

def send_twilio_whatsapp(company_name: str, area: str, score: int, priority: str, 
                         decision_maker: str, phone: str, website: str, tech_stack: str, pitch: str,
                         custom_sid: str = None, custom_token: str = None, 
                         custom_to: str = None, custom_from: str = None) -> dict:
    """
    Sends an official, 100% Meta-approved WhatsApp alert via Twilio REST API.
    """
    cfg = get_notifier_config()
    account_sid = (custom_sid if custom_sid is not None else cfg.get("twilio_sid", "")).strip()
    auth_token = (custom_token if custom_token is not None else cfg.get("twilio_token", "")).strip()
    to_phone = (custom_to if custom_to is not None else (cfg.get("twilio_to", "") or cfg.get("whatsapp_phone", ""))).strip()
    from_phone = (custom_from if custom_from is not None else cfg.get("twilio_from", "whatsapp:+14155238886")).strip()

    if not account_sid:
        return {"success": False, "error": "Twilio Account SID is missing in settings."}
    if not auth_token:
        return {"success": False, "error": "Twilio Auth Token is missing in settings."}
    if not to_phone:
        return {"success": False, "error": "Recipient phone number is missing in settings."}

    # Normalize phone: ensure whatsapp:+91... format
    clean_to = to_phone.replace(" ", "").replace("-", "")
    if clean_to.startswith("whatsapp:"):
        clean_to = clean_to[len("whatsapp:"):]
    if not clean_to.startswith("+"):
        clean_to = "+91" + clean_to if len(clean_to) == 10 else "+" + clean_to
    formatted_to = f"whatsapp:{clean_to}"

    clean_from = from_phone if from_phone.startswith("whatsapp:") else f"whatsapp:{from_phone}"

    msg = (
        f"🚨 *[HOT LEAD ALERT]*\n\n"
        f"🏢 *Company:* {company_name}\n"
        f"📍 *Area:* {area}\n"
        f"★ *Score:* {score}/100 ({priority} Priority)\n"
        f"🎯 *Decision Maker:* {decision_maker or 'Head of IT / Plant Operations'}\n"
        f"📞 *Lead Contact:* {phone or 'Available on Maps'}\n"
        f"🌐 *Website:* {website or 'N/A'}\n"
        f"⚙️ *Tech:* {tech_stack or 'Manufacturing'}\n\n"
        f"💬 *Proposed Pitch:*\n{pitch[:300] if pitch else ''}"
    )

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    post_data = {
        "From": clean_from,
        "To": formatted_to,
        "Body": msg
    }

    try:
        res = requests.post(url, data=post_data, auth=(account_sid, auth_token), timeout=10)
        try:
            data = res.json()
        except Exception:
            data = {}

        if res.status_code in [200, 201]:
            print(f"[TWILIO ALERT] Successfully sent WhatsApp alert to {formatted_to}")
            return {"success": True, "message": f"Twilio WhatsApp alert delivered to {clean_to}!"}
        else:
            err_msg = data.get("message", res.text)
            err_code = data.get("code", res.status_code)
            if err_code == 21608:
                err_msg += " (Make sure you joined the Twilio WhatsApp Sandbox first by sending the join keyword to +1 415 523 8886)"
            return {"success": False, "error": f"Twilio Error ({err_code}): {err_msg}"}
    except Exception as e:
        print(f"[TWILIO ALERT ERROR] {e}")
        return {"success": False, "error": str(e)}

def send_outreach_email(to_email: str, subject: str, message_body: str, is_html: bool = False,
                        custom_smtp_user: str = None, custom_smtp_pass: str = None,
                        custom_smtp_host: str = None, custom_smtp_port: int = None) -> dict:
    """
    Sends a direct client-facing outreach proposal or drip campaign step email.
    """
    cfg = get_notifier_config()
    smtp_user = (custom_smtp_user if custom_smtp_user is not None else cfg.get("smtp_user", "")).strip()
    smtp_pass = (custom_smtp_pass if custom_smtp_pass is not None else cfg.get("smtp_pass", "")).strip()
    smtp_host = (custom_smtp_host if custom_smtp_host is not None else cfg.get("smtp_host", "smtp.gmail.com")).strip()
    smtp_port = custom_smtp_port if custom_smtp_port is not None else cfg.get("smtp_port", 587)

    if not to_email or not str(to_email).strip() or "@" not in str(to_email):
        return {"success": False, "error": f"Invalid recipient email: {to_email}"}
    if not smtp_user or not smtp_pass:
        return {"success": False, "error": "SMTP sender credentials missing in Settings."}

    # Pre-flight DNS check to protect sender reputation against bounce-backs
    domain_part = to_email.strip().split('@')[1] if '@' in to_email else ''
    try:
        import socket
        socket.gethostbyname(domain_part)
    except Exception:
        err_msg = f"Recipient domain '{domain_part}' does not exist on DNS. Delivery skipped to avoid bounce-back."
        print(f"[OUTREACH EMAIL SKIPPED] {err_msg}")
        return {"success": False, "error": err_msg, "dns_invalid": True}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email.strip()

        formatted_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b; white-space: pre-wrap; padding: 12px 0;">
{message_body}
        </div>
        """
        msg.attach(MIMEText(message_body, "plain"))
        msg.attach(MIMEText(formatted_html, "html"))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=12)
            server.ehlo()
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=12)
            server.ehlo()
            server.starttls()
            server.ehlo()

        clean_pass = smtp_pass.replace(" ", "").strip()
        try:
            server.login(smtp_user, smtp_pass)
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
            server.login(smtp_user, clean_pass)

        server.sendmail(smtp_user, to_email.strip(), msg.as_string())
        server.quit()
        print(f"[OUTREACH EMAIL] Successfully delivered proposal to {to_email}")
        return {"success": True, "message": f"Proposal email dispatched to {to_email}"}
    except Exception as e:
        print(f"[OUTREACH EMAIL ERROR] {e}")
        return {"success": False, "error": str(e)}

def send_outreach_whatsapp(to_phone: str, message_text: str, custom_apikey: str = None) -> dict:
    """
    Sends an automated WhatsApp proposal message to a prospect or client via CallMeBot.
    """
    cfg = get_notifier_config()
    clean_phone = to_phone.replace("+", "").replace("-", "").replace(" ", "").strip()
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone

    api_key = (custom_apikey if custom_apikey is not None else cfg.get("whatsapp_apikey", "")).strip()
    if not api_key:
        return {"success": False, "error": "CallMeBot WhatsApp API key missing in Settings."}

    encoded_text = urllib.parse.quote(message_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={api_key}"
    try:
        res = requests.get(url, timeout=12)
        body = res.text.strip() if res.text else ""
        if "error" in body.lower() or "not correct" in body.lower() or "not registered" in body.lower():
            import re
            clean_err = re.sub(r'<[^>]+>', '', body).strip()
            return {"success": False, "error": f"WhatsApp Error: {clean_err}"}
        if res.status_code in [200, 201]:
            print(f"[OUTREACH WHATSAPP] Dispatched to +{clean_phone} successfully.")
            return {"success": True, "message": f"WhatsApp message sent to +{clean_phone}"}
        return {"success": False, "error": f"CallMeBot returned status {res.status_code}: {body}"}
    except Exception as e:
        print(f"[OUTREACH WHATSAPP ERROR] {e}")
        return {"success": False, "error": str(e)}

def send_direct_whatsapp(company_name: str = "", area: str = "", score: int = 0, priority: str = "Medium", 
                         decision_maker: str = "", phone: str = "", website: str = "", tech_stack: str = "", pitch: str = "",
                         custom_phone: str = None, custom_apikey: str = None, **kwargs) -> dict:
    """
    Sends a direct WhatsApp alert to the user's phone using CallMeBot API.
    CallMeBot is free and sends WhatsApp messages via HTTP GET.
    Also handles outreach mode when invoked with to_phone=..., message_text=...
    """
    if "to_phone" in kwargs or "message_text" in kwargs:
        to_phone = kwargs.get("to_phone", custom_phone or "")
        message_text = kwargs.get("message_text", pitch or "")
        return send_outreach_whatsapp(to_phone=to_phone, message_text=message_text, custom_apikey=custom_apikey)

    cfg = get_notifier_config()
    target_phone = custom_phone if custom_phone is not None else cfg.get("whatsapp_phone", "")
    api_key = custom_apikey if custom_apikey is not None else cfg.get("whatsapp_apikey", "")

    if not target_phone or not target_phone.strip():
        return {
            "success": False, 
            "error": "WhatsApp phone number is missing in settings."
        }

    if not api_key or not api_key.strip():
        return {
            "success": False, 
            "error": "CallMeBot API Key is missing. Send 'I allow callmebot to send me messages' to +34 644 44 22 55 on WhatsApp to get your free key."
        }

    # Normalize phone: remove spaces, plus, dashes
    clean_phone = target_phone.replace("+", "").replace("-", "").replace(" ", "").strip()
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone  # Default to India (+91) if 10 digits

    # Format the WhatsApp message
    msg = (
        f"🚨 *[HOT LEAD ALERT]*\n\n"
        f"🏢 *Company:* {company_name}\n"
        f"📍 *Area:* {area}\n"
        f"★ *Score:* {score}/100 ({priority} Priority)\n"
        f"🎯 *Decision Maker:* {decision_maker or 'Head of IT / Plant Operations'}\n"
        f"📞 *Lead Contact:* {phone or 'Available on Maps'}\n"
        f"🌐 *Website:* {website or 'N/A'}\n"
        f"⚙️ *Tech:* {tech_stack or 'Manufacturing'}\n\n"
        f"💬 *Proposed Pitch:*\n{pitch[:300] if pitch else ''}"
    )

    encoded_text = urllib.parse.quote(msg)
    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={api_key.strip()}"

    try:
        res = requests.get(url, timeout=10)
        body = res.text.strip() if res.text else ""
        
        # CallMeBot returns HTTP 200 or 201 on both success and errors, so check body text
        if "error" in body.lower() or "not correct" in body.lower() or "not registered" in body.lower() or "can not be" in body.lower():
            import re
            clean_err = re.sub(r'<[^>]+>', '', body).strip()
            return {"success": False, "error": f"CallMeBot Error: {clean_err}"}
        
        if res.status_code in [200, 201]:
            print(f"[WHATSAPP ALERT] Sent to {clean_phone} successfully.")
            return {"success": True, "message": f"WhatsApp alert sent to +{clean_phone}"}
        else:
            return {"success": False, "error": f"CallMeBot returned status {res.status_code}: {body}"}
    except Exception as e:
        print(f"[WHATSAPP ALERT ERROR] Failed to send WhatsApp: {e}")
        return {"success": False, "error": str(e)}

def send_direct_email(company_name: str = "", area: str = "", score: int = 0, priority: str = "Medium", 
                      decision_maker: str = "", phone: str = "", website: str = "", tech_stack: str = "", 
                      score_reasoning: str = "", email_pitch: str = "", whatsapp_pitch: str = "",
                      custom_email_to: str = None, custom_smtp_user: str = None,
                      custom_smtp_pass: str = None, custom_smtp_host: str = None,
                      custom_smtp_port: int = None, **kwargs) -> dict:
    """
    Sends a formatted executive lead briefing directly to the user's email via SMTP.
    Works seamlessly with Gmail, Outlook, Zoho, or any SMTP host.
    Also handles outreach mode when invoked with to_email=..., subject=..., message_body=...
    """
    if "to_email" in kwargs or "subject" in kwargs or "message_body" in kwargs:
        to_email = kwargs.get("to_email", custom_email_to or "")
        subject = kwargs.get("subject", f"Outreach Proposal for {company_name or 'Your Organization'}")
        message_body = kwargs.get("message_body", email_pitch or "")
        return send_outreach_email(
            to_email=to_email,
            subject=subject,
            message_body=message_body,
            custom_smtp_user=custom_smtp_user,
            custom_smtp_pass=custom_smtp_pass,
            custom_smtp_host=custom_smtp_host,
            custom_smtp_port=custom_smtp_port
        )
    cfg = get_notifier_config()
    to_email = custom_email_to if custom_email_to is not None else cfg.get("email_to", "")
    smtp_user = custom_smtp_user if custom_smtp_user is not None else cfg.get("smtp_user", "")
    smtp_pass = custom_smtp_pass if custom_smtp_pass is not None else cfg.get("smtp_pass", "")
    smtp_host = custom_smtp_host if custom_smtp_host is not None else cfg.get("smtp_host", "smtp.gmail.com")
    smtp_port = custom_smtp_port if custom_smtp_port is not None else cfg.get("smtp_port", 587)

    if not to_email or not to_email.strip():
        return {
            "success": False, 
            "error": "Destination email address is missing in settings."
        }
    if not smtp_user or not smtp_user.strip():
        return {
            "success": False, 
            "error": "SMTP Username (sender email) is missing in settings."
        }
    if not smtp_pass or not smtp_pass.strip():
        return {
            "success": False, 
            "error": "SMTP Password (or Gmail 16-digit App Password) is missing in settings."
        }

    subject = f"🚨 [Lead Alert] {company_name} ({priority} Priority • Score: {score}/100)"

    # Clean & normalize tech stack pills
    tech_pills_html = ""
    if tech_stack:
        tech_items = [t.strip() for t in str(tech_stack).replace('[', '').replace(']', '').replace('"', '').replace("'", '').split(',') if t.strip()]
        for item in tech_items:
            is_high_impact = any(k in item.lower() for k in ['sap', 'power bi', 'bi', 'erp', 'sql', 'plc', 'scada', 'automation', 'mes', 'robotics', 'telemetry'])
            bg_col = "#e0e7ff" if is_high_impact else "#f1f5f9"
            txt_col = "#3730a3" if is_high_impact else "#475569"
            border_col = "#c7d2fe" if is_high_impact else "#e2e8f0"
            tech_pills_html += f'<span style="display:inline-block; background-color:{bg_col}; color:{txt_col}; border:1px solid {border_col}; padding:3px 10px; border-radius:14px; font-size:12px; font-weight:600; margin:2px 4px 2px 0;">{item}</span>'
    if not tech_pills_html:
        tech_pills_html = '<span style="color:#64748b; font-size:13px;">Industrial Manufacturing</span>'

    # Clean phone link
    clean_digits = re.sub(r'[^0-9]', '', str(phone or ''))
    phone_cta_btn = ""
    if clean_digits:
        phone_cta_btn = f'<a href="tel:{clean_digits}" style="display:inline-block; background-color:#2563eb; color:#ffffff; font-weight:600; font-size:13px; padding:10px 18px; border-radius:6px; text-decoration:none; margin-right:8px;">📞 Call Contact: {phone}</a>'

    website_cta_btn = ""
    if website and str(website).startswith("http"):
        website_cta_btn = f'<a href="{website}" target="_blank" style="display:inline-block; background-color:#0284c7; color:#ffffff; font-weight:600; font-size:13px; padding:10px 18px; border-radius:6px; text-decoration:none;">🌐 View Website</a>'

    priority_upper = (priority or 'HIGH').upper()
    priority_color = "#10b981" if priority_upper == "HIGH" else ("#f59e0b" if priority_upper == "MEDIUM" else "#64748b")
    priority_bg = "#ecfdf5" if priority_upper == "HIGH" else ("#fffbeb" if priority_upper == "MEDIUM" else "#f8fafc")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
    </head>
    <body style="margin:0; padding:24px 0; background-color:#f8fafc; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#0f172a; line-height:1.5;">
      
      <!-- Container -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8fafc; padding:10px;">
        <tr>
          <td align="center">
            
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:640px; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e2e8f0; box-shadow:0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.01);">
              
              <!-- Top Branding Header -->
              <tr>
                <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding:28px 32px; border-bottom:4px solid #38bdf8;">
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td style="vertical-align:top;">
                        <div style="font-size:11px; font-weight:700; letter-spacing:1.5px; color:#38bdf8; text-transform:uppercase; margin-bottom:8px;">
                          BROWNBOX INNOVATION • SAP, POWER BI & INDUSTRIAL AUTOMATION
                        </div>
                        <h1 style="margin:0; font-size:24px; font-weight:800; color:#f8fafc; line-height:1.2;">
                          {company_name}
                        </h1>
                        <div style="margin-top:6px; font-size:13.5px; color:#94a3b8;">
                          📍 {area}, Pune Industrial Corridor
                        </div>
                      </td>
                      <td align="right" style="vertical-align:top; width:130px;">
                        <div style="display:inline-block; background-color:{priority_bg}; color:{priority_color}; border:1px solid {priority_color}40; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:800; letter-spacing:0.5px; text-align:center;">
                          ● {priority_upper}
                        </div>
                        <div style="margin-top:8px; font-size:20px; font-weight:800; color:#38bdf8; text-align:center;">
                          {score}<span style="font-size:13px; color:#64748b; font-weight:600;">/100</span>
                        </div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Main Content Body -->
              <tr>
                <td style="padding:28px 32px;">
                  
                  <!-- Section: Core Intelligence Snapshot -->
                  <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; color:#64748b; margin-bottom:12px;">
                    EXECUTIVE TARGET PROFILE
                  </div>

                  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:24px;">
                    <tr>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; width:38%; font-size:13px; font-weight:600; color:#64748b;">
                        🎯 Target Decision Maker
                      </td>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; font-size:14px; font-weight:700; color:#0f172a;">
                        {decision_maker or 'Head of IT / Plant Operations'}
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; font-size:13px; font-weight:600; color:#64748b;">
                        📞 Contact Phone
                      </td>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; font-size:14px; font-weight:700; color:#2563eb;">
                        {phone or 'Available on Google Maps / Directory'}
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; font-size:13px; font-weight:600; color:#64748b;">
                        🌐 Company Website
                      </td>
                      <td style="padding:14px 18px; border-bottom:1px solid #e2e8f0; font-size:14px; font-weight:600; color:#0284c7;">
                        {f'<a href="{website}" target="_blank" style="color:#0284c7; text-decoration:none;">{website}</a>' if website else '<span style="color:#94a3b8;">Not Available</span>'}
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px; font-size:13px; font-weight:600; color:#64748b; vertical-align:top;">
                        ⚙️ Detected Stack & Signals
                      </td>
                      <td style="padding:14px 18px; font-size:13px; color:#0f172a;">
                        <div style="line-height:1.7;">
                          {tech_pills_html}
                        </div>
                      </td>
                    </tr>
                  </table>

                  <!-- AI Qualification Reasoning -->
                  {f'''
                  <div style="background-color:#eff6ff; border-left:4px solid #3b82f6; border-radius:6px; padding:14px 18px; margin-bottom:24px;">
                    <div style="font-size:12px; font-weight:700; color:#1d4ed8; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">
                      🔍 AI Qualification Signals & Rationale
                    </div>
                    <div style="font-size:13.5px; color:#1e3a8a; line-height:1.6;">
                      {score_reasoning}
                    </div>
                  </div>
                  ''' if score_reasoning else ''}

                  <!-- Cold Email Pitch -->
                  <div style="margin-bottom:28px; border:1px solid #e0e7ff; background-color:#f8faff; border-radius:8px; overflow:hidden;">
                    <div style="background-color:#eef2ff; padding:10px 18px; font-size:12px; font-weight:700; color:#4338ca; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid #e0e7ff;">
                      ✉️ Tailored Cold Outreach Email (Services & Value Proposal)
                    </div>
                    <div style="padding:18px; font-size:13.5px; color:#312e81; line-height:1.7; font-family:'Segoe UI', Roboto, sans-serif; white-space:pre-wrap;">{email_pitch}</div>
                  </div>

                  <!-- Quick Action Buttons -->
                  <div style="text-align:center; padding:10px 0 6px 0;">
                    {phone_cta_btn}
                    {website_cta_btn}
                  </div>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background-color:#f1f5f9; padding:20px 32px; border-top:1px solid #e2e8f0; text-align:center;">
                  <div style="font-size:12px; font-weight:600; color:#64748b;">
                    BrownBox Innovation • Autonomous Industrial Lead Engine
                  </div>
                  <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
                    Real-time alert triggered automatically for High-Priority Pune MIDC prospects.
                  </div>
                </td>
              </tr>

            </table>

          </td>
        </tr>
      </table>

    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html"))

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            server.ehlo()
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
        clean_pass = smtp_pass.replace(" ", "").strip()
        try:
            server.login(smtp_user, smtp_pass)
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected):
            # Retry with spaces stripped from App Password
            server.login(smtp_user, clean_pass)

        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"[EMAIL ALERT] Successfully emailed lead briefing to {to_email}")
        return {"success": True, "message": f"Email alert sent to {to_email}"}
    except smtplib.SMTPAuthenticationError as auth_err:
        err_text = f"Gmail Authentication Failed (535): Incorrect username or App Password. Please generate a fresh 16-digit App Password at https://myaccount.google.com/apppasswords for {smtp_user}."
        print(f"[EMAIL ALERT ERROR] {err_text}")
        return {"success": False, "error": err_text}
    except smtplib.SMTPServerDisconnected as disc_err:
        err_text = f"Gmail disconnected the session. This usually means Google rejected the App Password (BadCredentials). Ensure 2-Step Verification is active on {smtp_user} and generate a new App Password."
        print(f"[EMAIL ALERT ERROR] {err_text}")
        return {"success": False, "error": err_text}
    except Exception as e:
        print(f"[EMAIL ALERT ERROR] Failed to send email via SMTP: {e}")
        return {"success": False, "error": str(e)}

def dispatch_all_alerts(lead, custom_cfg: dict = None) -> dict:
    """
    Main dispatch function called when a lead qualifies for notification.
    Dispatches via Telegram and Email as configured.
    """
    cfg = custom_cfg if custom_cfg is not None else get_notifier_config()
    results = {}

    company_name = getattr(lead, 'company_name', 'Company')
    area = getattr(lead, 'area', 'Pune')
    score = getattr(lead, 'relevance_score', 0)
    priority = getattr(lead, 'priority', 'Low')
    decision_maker = getattr(lead, 'decision_maker', '')
    phone = getattr(lead, 'phone', '')
    website = getattr(lead, 'website', '')
    tech_stack = getattr(lead, 'tech_stack', '')
    score_reasoning = getattr(lead, 'score_reasoning', '')
    email_pitch = getattr(lead, 'generated_pitch', '')
    whatsapp_pitch = getattr(lead, 'whatsapp_pitch', '')

    # 1. Direct WhatsApp Dispatch
    if cfg.get("whatsapp_enabled"):
        target_phone = cfg.get("whatsapp_phone", "")
        apikey = cfg.get("whatsapp_apikey", "")
        if not target_phone or not target_phone.strip():
            results["whatsapp"] = {
                "success": False,
                "error": "WhatsApp phone number not entered in settings."
            }
        elif not apikey or not apikey.strip():
            results["whatsapp"] = {
                "success": False,
                "error": "CallMeBot API Key missing. Send 'I allow callmebot to send me messages' to +34 644 44 22 55 on WhatsApp to get your free key."
            }
        else:
            results["whatsapp"] = send_direct_whatsapp(
                company_name=company_name,
                area=area,
                score=score,
                priority=priority,
                decision_maker=decision_maker,
                phone=phone,
                website=website,
                tech_stack=tech_stack,
                pitch=whatsapp_pitch or email_pitch,
                custom_phone=target_phone,
                custom_apikey=apikey
            )

    # 2. Direct Email Dispatch
    if cfg.get("email_enabled"):
        to_email = cfg.get("email_to", "")
        smtp_user = cfg.get("smtp_user", "")
        smtp_pass = cfg.get("smtp_pass", "")
        if not to_email or not smtp_user or not smtp_pass:
            results["email"] = {
                "success": False,
                "error": "Email address, SMTP User, or SMTP password/App Password missing."
            }
        else:
            results["email"] = send_direct_email(
                company_name=company_name,
                area=area,
                score=score,
                priority=priority,
                decision_maker=decision_maker,
                phone=phone,
                website=website,
                tech_stack=tech_stack,
                score_reasoning=score_reasoning,
                email_pitch=email_pitch,
                whatsapp_pitch=whatsapp_pitch,
                custom_email_to=to_email,
                custom_smtp_user=smtp_user,
                custom_smtp_pass=smtp_pass,
                custom_smtp_host=cfg.get("smtp_host"),
                custom_smtp_port=cfg.get("smtp_port")
            )

    # 3. Direct Telegram Dispatch
    if cfg.get("telegram_enabled"):
        results["telegram"] = send_telegram_alert(
            company_name=company_name,
            area=area,
            score=score,
            priority=priority,
            decision_maker=decision_maker,
            phone=phone,
            website=website,
            tech_stack=tech_stack,
            pitch=email_pitch,
            custom_token=cfg.get("telegram_bot_token"),
            custom_chat_id=cfg.get("telegram_chat_id"),
            custom_message=cfg.get("custom_message")
        )

    return results

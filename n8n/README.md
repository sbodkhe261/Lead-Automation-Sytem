# n8n Automation Engine for Lead Intelligence System

This directory contains the automated workflow and configuration to connect the Lead Scraper & AI Agent with WhatsApp and Email.

---

## 1. Quick Start (How to Launch n8n)

You can launch n8n in either of two ways:

### Option A: 1-Click Batch File (Recommended)
Double-click `start_n8n.bat` in the project root folder. It will automatically check for Docker and fall back to Node.js/npx.

### Option B: Via Docker
If you have Docker Desktop running:
```bash
docker compose up -d n8n
```

### Option C: Via Node.js / npx
```bash
npx -y n8n
```

Once started, open **[http://localhost:5678](http://localhost:5678)** in your browser.

---

## 2. How to Import the Lead Alert Workflow

1. Open **[http://localhost:5678](http://localhost:5678)**.
2. Complete the quick initial admin signup (first time only).
3. On the left navigation, click **Workflows** ➔ **Add Workflow** (or the **+** button).
4. Click the three dots menu (**...**) in the top right ➔ **Import from File**.
5. Select the file:
   `c:\Users\Laptop House\Desktop\BrownBoxInnovation\Lead Automation System\n8n\lead_alert_workflow.json`
6. Click **Activate** (toggle switch in top right to "Active").

---

## 3. How the Pipeline Works

```
[ Lead Scraper / Auto-Pilot ]
           │
           │ (POST /webhook/lead-alert)
           ▼
[ n8n Webhook Trigger ]
           │
           ▼
[ Check Score >= 45 ]
           │
           ▼
[ Format Alert Briefing ]
           │
           ├──► [ WhatsApp Notification ] ──► (Your Phone)
           └──► [ Email / Gmail Node ]   ──► (Your Team Inbox)
```

### Webhook URL
The FastAPI application communicates with:
`http://localhost:5678/webhook/lead-alert`

This URL is pre-configured in your `.env` file (`N8N_WEBHOOK_URL`).

---

## 4. Connecting Your WhatsApp & Email

In the imported n8n workflow canvas:
1. **To send WhatsApp messages:**
   * Add a **Twilio** node, **WhatsApp Cloud API** node, or **HTTP Request** node pointing to your WhatsApp provider (e.g., Green API, UltraMsg, Evolution API).
   * Map the message body to: `{{ $json.whatsapp_message }}`.
2. **To send Emails:**
   * Add a **Gmail** or **Send Email (SMTP)** node.
   * Map Subject to: `{{ $json.email_subject }}`.
   * Map HTML Body to: `{{ $json.email_html }}`.

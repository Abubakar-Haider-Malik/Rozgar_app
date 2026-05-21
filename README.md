

# 🛠️ Rozgar  AI

> AI-powered multilingual service marketplace for Pakistan’s informal economy.

Rozgar AI connects users with local service providers through a conversational AI experience supporting **Urdu**, **Roman Urdu**, and **English**.

The platform uses a multi-agent orchestration system to understand requests, resolve locations, discover providers, rank results, generate bookings, and simulate notifications — all with transparent reasoning traces.

---

# ✨ Features

* 🤖 AI-powered service request understanding
* 🌐 Urdu, Roman Urdu & English support
* 📍 Smart Islamabad/Rawalpindi location resolution
* 🔎 Intelligent provider discovery & ranking
* 📅 Automated booking generation
* 📲 WhatsApp/SMS-style notification simulation
* 🧠 Multi-agent reasoning pipeline
* 📊 Transparent agent trace visualization
* ⚡ Graceful fallback without Gemini API

---

# 🏗️ Architecture

```text
Frontend (Next.js + TailwindCSS)
        │
        ▼
Backend API (FastAPI)
        │
        ▼
RozgarOrchestrator (Antigravity Pattern)

IntentAgent
   ↓
LocationAgent
   ↓
ProviderDiscoveryAgent
   ↓
RankingAgent
   ↓
BookingAgent
   ↓
NotificationAgent
   ↓
FollowUpAgent
```

---

# 🧠 Multi-Agent Workflow

Rozgar AI implements a:

```text
Plan → Reason → Decide → Act → Follow-up
```

workflow using autonomous but coordinated agents.

| Agent                  | Responsibility                          |
| ---------------------- | --------------------------------------- |
| IntentAgent            | Detects language, service type, urgency |
| LocationAgent          | Resolves sectors into coordinates       |
| ProviderDiscoveryAgent | Finds nearby matching providers         |
| RankingAgent           | Scores providers intelligently          |
| BookingAgent           | Generates booking records               |
| NotificationAgent      | Creates simulated notifications         |
| FollowUpAgent          | Schedules follow-up checkpoints         |

---

# 🔍 Transparent AI Reasoning

Each request generates a structured `trace_log` containing:

* timestamps
* agent actions
* reasoning steps
* tool usage
* outputs
* decisions

The frontend visualizes this using `AgentTrace.tsx`.

---

# ⚙️ Tech Stack

## Backend

* Python 3.13
* FastAPI
* Pydantic v2
* Google Gemini API
* Uvicorn

## Frontend

* Next.js 14
* TypeScript
* TailwindCSS

## Deployment

* Docker
* Google Cloud Run

---

# 🌍 Supported Areas

Currently supports selected areas of:

### Islamabad

* G-9
* G-10
* F-7
* F-10
* I-8
* I-10

### Rawalpindi

* near eme area

---

# 📌 Example Request

```json
{
  "message": "G-10 mein plumber chahiye urgently"
}
```

### Example Output

```json
{
  "service": "plumber",
  "location": "G-10",
  "urgency": "high",
  "provider": "Ahmed Plumbing Services",
  "booking_id": "BK-1042"
}
```

---

# ⚠️ Current Limitations

* Static mock provider database
* No persistent database
* No authentication system
* No payment integration
* Simulated notifications only
* Stateless conversations
* Limited to Islamabad & Rawalpindi

---

# 🔮 Future Improvements

* Real provider onboarding
* PostgreSQL integration
* Real-time availability
* WhatsApp/SMS APIs
* Payment gateway support
* Voice input support
* User authentication
* Conversational memory

---

# 📄 License

MIT License

---

# 👨‍💻 Author

Built for improving local service accessibility in Pakistan 🇵🇰

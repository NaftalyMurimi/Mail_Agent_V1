# Email Manager Agent

AI-powered job search automation. Scans your Gmail, 
classifies job emails, scores them against your CV 
and sends recommendations to your Telegram.

## Tech Stack
- **Backend** — FastAPI
- **Frontend** — React
- **Database** — Supabase (PostgreSQL)
- **AI** — Groq LLaMA 3.3
- **Background Jobs** — Celery + Redis
- **Deployment** — Microsoft Azure

## Getting Started

### 1. Clone the repository
git clone https://github.com/yourusername/email-manager-agent.git
cd email-manager-agent

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up environment variables
copy .env.example .env
# Fill in your API keys in .env

### 5. Run the API
cd backend
uvicorn app.main:app --reload

### 6. Visit
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## Project Structure
email-manager-agent/
├── backend/
│   ├── app/
│   │   ├── api/         ← API route handlers
│   │   ├── agent/       ← AI agent logic
│   │   ├── models/      ← Database models
│   │   ├── schemas/     ← Pydantic schemas
│   │   └── utils/       ← Logging, helpers
│   └── tests/
├── frontend/            ← React app
├── docs/                ← CV PDFs
├── config/
└── logs/
# VazhiThunAI

Your AI-powered career companion — adaptive learning paths, pitfall detection, and weekly career intelligence.

## Overview

VazhiThunAI helps learners build career-focused learning journeys by combining personalized planning, automated pitfall detection, semantic retrieval, and curated weekly updates. This repository contains a FastAPI backend and a Vite + React frontend.

## Key Features

- Adaptive learning planner
- Pitfall detection and remediation
- Recommendation engine
- Weekly career intelligence updates
- Retrieval-augmented generation (Pinecone + RAG)
- Email/password authentication and user profiles

## Repo Layout

- `backend/` — FastAPI app, services, scripts, DB models
- `frontend/` — Vite + React SPA, pages, components, public assets
- `data/` — CSVs and seed data used by scripts
- `tests/` — Backend tests

## Quickstart (development)

Prerequisites:
- Node.js 16+ and npm
- Python 3.10+
- Git
- (Optional) Supabase account and Pinecone account for full feature set

1. Clone the repository

```bash
git clone <repo-url>
cd VazhiThunAI
```

2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (see `backend/.env.example` for required variables). Do NOT commit secrets to git.

Run the backend during development:

```bash
uvicorn app.main:app --reload
```

3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open the app (Vite default usually `http://localhost:5173`) and navigate to `/login` or `/register`.

## Environment Variables

The backend requires several env vars for third-party integrations. Copy `backend/.env.example` to `backend/.env` and populate your values.

Important: Never paste production secrets into issue trackers or public PRs. Use your platform's secret manager for production deployments.

## Logo / Branding

- Place the official logo at `frontend/public/vazhithunai-logo.png`. The auth pages already reference this file and display it in the left brand panel.
- Do not alter the artwork or colors of the logo.

## Seeding & Demo Data

Sample seed scripts are available in `backend/app/scripts/` (e.g. `seed_pinecone.py`, `seed_supabase.py`). Run them after configuring your environment variables.

## Running Tests

```bash
cd backend
pytest
```

## Deployment Notes

- Run the FastAPI app with an ASGI server (Uvicorn workers behind Gunicorn, or use a platform that supports ASGI).
- Build the frontend via `npm run build` and serve statically or from the backend.
- Use managed Supabase (or equivalent Postgres) and Pinecone for production vector search.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Add tests and make small, focused PRs

## License

Add your preferred license here (e.g., MIT).

---

If you'd like, I can commit this `README.md` and the `.env.example` for you, or adjust tone/length for a public landing README vs an internal developer README.
# VazhiThunAI

VazhiThunAI is an AI-powered personalized learning companion. It helps users achieve their learning goals by automatically analyzing their current skills, identifying missing gaps, and generating a highly customized, step-by-step learning path using real-time AI generation. 

## Features

- **Personalized Learning Paths:** AI breaks down your broad goal (e.g., "Learn Machine Learning") into an actionable, step-by-step roadmap tailored to your specific background.
- **Adaptive Learning Path:** The curriculum is not static; it dynamically adapts and re-calibrates based on your progress, speed, and changing needs.
- **AI Skill Gap Analysis:** Automatically identifies exactly what you need to learn by comparing your goal against your existing knowledge profile using semantic search.
- **Weekly Updates & Monitoring:** Breaks down long-term goals into manageable weekly targets, providing consistent progress tracking and accountability.
- **Interactive RAG Chatbot:** A built-in AI tutor that retrieves contextually relevant study resources from a vector database to answer your specific questions on the fly.
- **Adaptive Timeline Simulator:** A "What-If" simulator that instantly adjusts your learning timeline if you change your weekly study hours or switch to a faster pace.
- **Pitfall Dashboard:** Warns you about common mistakes and hurdles faced by other learners in similar topics using population data insights.
- **Dynamic Resource Recommendation:** Automatically suggests the best study materials and tutorials based on your preferred learning format (e.g., videos vs. text).
- **Secure Authentication:** Complete user registration, login, and profile management system.

## End-to-End Workflow

1. **Sign Up & Onboarding:** The user creates an account and enters their learning goal along with their available study time.
2. **AI Processing:** 
   - The backend uses a RAG powered Large Language Model to understand the goal.
   - It searches a vector database to find required skills and resources.
   - It generates a structured learning path specifically for that user.
3. **Learning Dashboard:** The user views their personalized path on a dynamic timeline.
4. **Learning & Chatting:** The user can chat with the AI tutor for help on specific topics. The tutor uses Retrieval-Augmented Generation (RAG) to provide accurate answers.
5. **Adaptation:** As the user progresses, they can use the What-If simulator to adapt their schedule dynamically.

## Project Structure

```text
VazhiThunAI/
│
├── frontend/                  
│   ├── src/
│   │   ├── api/               
│   │   ├── components/        
│   │   ├── pages/              
│   │   └── App.jsx             
│   └── package.json
│
└── backend/                    
    ├── app/
    │   ├── ai/                 
    │   ├── api/                
    │   ├── models/             
    │   ├── retrieval/          
    │   ├── services/           
    │   └── main.py             
    ├── requirements.txt        
    └── render_requirements.txt 
```

## Local Setup Instructions

To run this project on your local machine, you will need to start both the backend and frontend servers.

### Prerequisites
- Node.js (v16+)
- Python (3.10+)
- A PostgreSQL Database (e.g., Supabase)
- A Pinecone Vector Database account
- API Keys

### 1. Backend Setup

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file inside the `backend` folder and add your API keys:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENV=your_pinecone_environment
   PINECONE_INDEX_NAME=your_index_name
   HF_API_TOKEN=your_huggingface_token
   ```
5. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The backend will now be running at http://127.0.0.1:8000*

### 2. Frontend Setup

1. Open a new, separate terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install the required Node packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will now be running at http://localhost:5173*

You can now open your browser, navigate to the frontend URL, and use the application locally!
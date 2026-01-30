SME Financial Health Platform - Project Walkthrough
🚀 Live Demo
Frontend (App): https://aifinancialplatform.netlify.app
Backend (API): https://ai-financial-platform-1.onrender.com
GitHub Repo: https://github.com/dhana-dev6/AI-Financial-Platform
🎯 Key Features
1. AI-Powered Financial CFO
Smart Analysis: Uses Llama-3-70b (via Groq) for instant insights, with an automatic fallback to Gemini Flash 2.0 (via OpenRouter) if rate-limited.
Multilingual: Supports analysis in English, Hindi, and other languages.
Secure: Financial data is processed in-memory and encrypted in the database.
2. Interactive Dashboard
Health Score: Real-time gauge (0-100) based on profit margins and stability.
Charts: Interactive Recharts for Revenue/Expense breakdown.
Bank Connect: Mock integration to pull transactions from HDFC/ICICI.
3. Reporting & Compliance
PDF Reports: Generates professional "Investor One-Pagers" on the fly.
Audit Logs: Tracks every AI decision for regulatory compliance (immutable logs).
🛠️ Tech Stack
Frontend: React, Vite, TailwindCSS (Glassmorphism), Recharts.
Backend: FastAPI, Pandas (Data processing), SQLAlchemy (SQLite/Postgres).
AI: Groq Cloud, OpenRouter, Google Gemini.
🏃‍♂️ How to Run Locally
Clone the Repo
git clone https://github.com/dhana-dev6/AI-Financial-Platform.git
Backend Setup
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend Setup
cd frontend
npm install
npm run dev
Built for the AI Hackathon 2026.

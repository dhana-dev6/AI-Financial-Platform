# 🚀 SME Financial Health Platform (AI-Powered CFO)

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://aifinancialplatform.netlify.app)
[![Backend Status](https://img.shields.io/badge/Backend-Render-blue)](https://ai-financial-platform-1.onrender.com/docs)
[![License](https://img.shields.io/badge/License-MIT-gray)]()

> A robust, AI-driven financial dashboard designed to help Small and Medium Enterprises (SMEs) analyze financial risks, optimize costs, and generate investor-ready reports instantly.

---

## 🧐 The Problem
SMEs often struggle with financial literacy, cash flow management, and compliance. Hiring a full-time CFO is expensive, and manual spreadsheet analysis is error-prone and slow.

## 💡 The Solution
An **"Artificial Intelligence CFO"** that:
1.  Ingests financial data (CSV, PDF, Bank APIs).
2.  Analyzes health using **Llama-3-70B** (Groq) & **Gemini Flash 2.0**.
3.  Provides actionable insights (Risk Warnings, Cost-Cutting Strategies).
4.  Generates compliant reports (PDFs) for investors.

---

## ✨ Key Features

### 🧠 1. Dual-AI Intelligence Engine
*   **Primary Brain**: Uses `Llama-3-70b-8192` via Groq Cloud for **ultra-fast** (<2s) analysis.
*   **Smart Fallback**: Automatically switches to `Google Gemini 2.0 Flash` (via OpenRouter) if the primary model is busy or rate-limited.
*   **Multilingual**: Speaks your language! Generates reports in English, Hindi, Tamil, etc. based on user preference.

### 📊 2. Interactive Financial Dashboard
*   **Health Score**: Real-time gauge (0-100) combining Profit Margin, Liquidity, and Solvency.
*   **Visual Analytics**: Interactive Recharts for Revenue/Expense breakdowns.
*   **Glassmorphism UI**: Premium, modern interface with soft gradients and verified accessible contrast.

### 🔒 3. Enterprise-Grade Security
*   **Encryption**: All sensitive financial values (Revenue, Profit) are **AES-Encrypted** before storage.
*   **Audit Trails**: Every AI decision is logged in an immutable `ComplianceLog` table for regulatory review.
*   **Bank Connect**: Mock secure integration patterns for HDFC, ICICI, and Chase banks.

### 📄 4. Automated Reporting
*   **Investor One-Pager**: One-click generation of professional PDF reports containing the Executive Summary and Key Metrics.
*   **Forecasting**: Linear Regression models to predict next month's cash flow.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React 18, Vite, TailwindCSS, Lucide Icons, Recharts |
| **Backend** | FASTAPI (Python), Uvicorn |
| **AI Models** | Groq (Llama 3), OpenRouter (Gemini) |
| **Database** | SQLAlchemy (SQLite for Dev, PostgreSQL ready) |
| **Security** | Python Cryptography (Fernet Encryption) |
| **Deployment** | Netlify (Frontend), Render (Backend) |

---

## 🚀 Getting Started

### Prerequisites
*   Node.js v18+
*   Python 3.10+
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/dhana-dev6/AI-Financial-Platform.git
cd AI-Financial-Platform
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Usage your keys in .env
# Create a .env file with:
# GROQ_API_KEY=gsk_...
# OPENROUTER_API_KEY=sk-or-...

python -m uvicorn main:app --reload
```
*Backend runs on `http://localhost:8000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`*

---

## 🌍 Deployment

### Frontend (Netlify)
The frontend is deployed as a static site.
*   **Build Command**: `npm run build`
*   **Publish Directory**: `dist`
*   **Environment Variable**: `VITE_API_URL` = `https://your-backend.onrender.com`

### Backend (Render)
The backend is a Python Web Service.
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
*   **Environment Variables**: Add your API Keys here.

---

## 🛡️ License
This project is open-source and available under the [MIT License](LICENSE).

---

> Built for **AI Hackathon 2026** by Dhana Akash.

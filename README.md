# 💰 Libertad Wealth Management App & Real Estate Sniper

This project is a comprehensive **Wealth Management application** that combines personal finance tracking with advanced **real estate investment analysis tools** ("Real Estate Sniper").

**Objective:** Centralize your financial health, track income and expenses, and evaluate new investment opportunities from a single modern interface.

---

# 🏗 Project Architecture

The project is divided into two main components:

## 1. Backend (API)

- **Technology:** Python with FastAPI  
- **Location:** `backend/` folder  

**Responsibilities:**

- Financial business logic management  
- Data persistence (transactions and assets)  
- Real estate scraping and analysis  
- AI integration (OpenAI) for the Financial Coach  

**Data Storage**

The system uses a lightweight JSON-based persistence approach to simplify local deployment without requiring complex databases.

data/transactions.json
data/assets.json


---

## 2. Frontend (User Interface)

- **Technology:** React + Vite + TypeScript + Tailwind CSS  
- **Location:** `frontend/` folder  

**Responsibilities:**

- Modern and responsive UI (Apple / Revolut-inspired design)  
- Financial data visualization (charts and KPIs)  
- User interaction (forms, chat interface, navigation)

---

# 🚀 Key Features

## 📊 Financial Dashboard

A visual summary of your financial health in real time.

Features:

- **KPIs:** Total Income, Total Expenses, Savings Rate  
- **Charts:** Monthly comparison of income vs expenses  
- **Automatic updates** when new transactions are added

---

## 📒 Transaction Log

Detailed management of your cash flow.

Features:

- Register **income and categorized expenses**  
- Standard financial categories (Salary, Rent, Housing, Leisure, etc.)  
- Clean and structured **transaction history**

---

## 🎯 Real Estate Sniper

An investment analysis tool based on the **"Libertad Inmobiliaria" methodology**.

Features:

- **Property Analyzer**
  - Paste a property URL (Idealista / Fotocasa) or raw text
  - Automatically extract property data

- **Investment Metrics**
  - Net Yield
  - Cashflow estimation
  - Recommended Maximum Offer (RMO)

- **Integration with Portfolio**
  - Button **"Add to my projections"** to save the property as an asset

- **PDF Report Generator**
  - Creates detailed analysis reports for each property

---

## 🤖 AI Financial Coach

Your personal financial advisor available **24/7**.

Features:

- Integrated **chat interface**
- AI responses based on **your real financial data**
- Understands:
  - expenses
  - savings
  - income
  - financial balance

**AI Engine:** OpenAI (GPT-4o-mini)

---

# 📂 Project Structure

```
sniper-inmobiliario/
├── backend/ # API Server
│ ├── main.py # Entry point and API endpoints
│ ├── finance_service.py # Financial management logic
│ ├── scraper.py # Real estate scraping logic
│ ├── calculator.py # Investment profitability calculations
│ ├── models.py # Pydantic data models
│ ├── llm_extractor.py # AI-based data extraction
│ └── reports/ # Generated PDF reports
│
├── frontend/ # Web client
│ ├── src/
│ │ ├── components/
│ │ │ ├── WealthDashboard.tsx
│ │ │ ├── ExpenseLog.tsx
│ │ │ ├── SniperSection.tsx
│ │ │ ├── AICoach.tsx
│ │ │ └── ...
│ │ ├── pages/
│ │ │ └── Index.tsx
│ │ └── services/
│ │ └── api.ts
│
├── data/ # Local JSON database
│ ├── transactions.json # Income/expense history
│ └── assets.json # Saved real estate assets
│
├── README.md
└── DEBUG_instructions.md
```


# 🛠 Running the Project

To run the full application you need **two terminals**.

---

## Terminal 1 — Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

# Install dependencies (first time only)
```bash
pip install -r requirements.txt

python main.py
```


The backend will run at:

```bash
http://localhost:8000
```

Terminal 2 — Frontend
```bash
cd frontend
```

# Install dependencies (first time only)
```bash
npm install

npm run dev
```

The frontend will run at:

```bash
http://localhost:8081
```

(or a similar port depending on Vite)

## Typical Workflow

### Register transactions
Add your salary and monthly expenses in the Transaction Log tab.

### Monitor your finances
Go to the Dashboard to track your savings rate.

### Analyze a property
Find a property on Idealista and paste the URL into Real Estate Sniper.

### Evaluate the investment
Review the calculated profitability metrics.

### Add to projections
If the investment looks promising, add it to your portfolio.

### Consult the AI Coach
Ask the assistant whether the investment makes sense based on your current finances.

import json
import os
import uuid
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

# Modelos Pydantic
class Transaction(BaseModel):
    id: str
    date: str
    category: str
    concept: str
    amount: float
    account: str

class Asset(BaseModel):
    id: str
    name: str
    type: str  # 'Inmueble', 'Fondo', etc.
    value: float
    details: Dict
    date_added: str

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    savings_rate: float
    balance: float
    monthly_data: Dict[str, Dict[str, float]] # "YYYY-MM": {"income": X, "expenses": Y}

# Rutas de archivos
DATA_DIR = "data"
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
ASSETS_FILE = os.path.join(DATA_DIR, "assets.json")

# Seed Data
SEED_TRANSACTIONS = [
    {
        "id": "seed-1",
        "date": "2026-01-01",
        "category": "Nómina",
        "concept": "Nómina Enero",
        "amount": 2500.0,
        "account": "Trabajo"
    },
    {
        "id": "seed-2",
        "date": "2026-01-02",
        "category": "Vivienda",
        "concept": "Hipoteca/Alquiler",
        "amount": -850.0,
        "account": "Vivienda"
    },
    {
        "id": "seed-3",
        "date": "2026-01-03",
        "category": "Alimentación",
        "concept": "Supermercado",
        "amount": -150.0,
        "account": "Alimentación"
    },
    {
        "id": "seed-4",
        "date": "2026-01-05",
        "category": "Ocio/Restaurantes",
        "concept": "Restaurante Sniper",
        "amount": -60.0,
        "account": "Ocio"
    },
    {
        "id": "seed-5",
        "date": "2026-01-10",
        "category": "Inversiones",
        "concept": "Dividendos",
        "amount": 120.0,
        "account": "Inversiones"
    }
]

class FinanceService:
    def __init__(self):
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Asegura que existan los archivos de datos y carga seed data si están vacíos."""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        # Transactions
        if not os.path.exists(TRANSACTIONS_FILE):
            self._save_transactions(SEED_TRANSACTIONS)
        else:
            # Check if empty list
            try:
                with open(TRANSACTIONS_FILE, 'r') as f:
                    data = json.load(f)
                    if not data:
                        self._save_transactions(SEED_TRANSACTIONS)
            except json.JSONDecodeError:
                self._save_transactions(SEED_TRANSACTIONS)

        # Assets
        if not os.path.exists(ASSETS_FILE):
            self._save_assets([])

    def _load_transactions(self) -> List[dict]:
        with open(TRANSACTIONS_FILE, 'r') as f:
            return json.load(f)

    def _save_transactions(self, data: List[dict]):
        with open(TRANSACTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_assets(self) -> List[dict]:
        with open(ASSETS_FILE, 'r') as f:
            return json.load(f)

    def _save_assets(self, data: List[dict]):
        with open(ASSETS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def get_transactions(self) -> List[Transaction]:
        raw_data = self._load_transactions()
        # Ordenar por fecha descendente
        raw_data.sort(key=lambda x: x['date'], reverse=True)
        return [Transaction(**t) for t in raw_data]

    def add_transaction(self, transaction: Transaction) -> Transaction:
        transactions = self._load_transactions()
        # Ensure ID
        if not transaction.id:
            transaction.id = str(uuid.uuid4())
        
        transactions.append(transaction.dict())
        self._save_transactions(transactions)
        return transaction

    def get_assets(self) -> List[Asset]:
        raw_data = self._load_assets()
        return [Asset(**a) for a in raw_data]

    def add_asset(self, asset: Asset) -> Asset:
        assets = self._load_assets()
        if not asset.id:
            asset.id = str(uuid.uuid4())
        assets.append(asset.dict())
        self._save_assets(assets)
        return asset

    def get_summary(self) -> FinancialSummary:
        transactions = self.get_transactions()
        
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(t.amount for t in transactions if t.amount < 0)
        
        # Calcular tasa de ahorro: ((Ingresos + Gastos) / Ingresos) * 100
        # Gastos es negativo, así que es Ingresos - abs(Gastos)
        savings_rate = 0.0
        if total_income > 0:
            savings_rate = ((total_income + total_expenses) / total_income) * 100
        
        # Datos mensuales para gráficos
        monthly_data = {}
        for t in transactions:
            month_key = t.date[:7] # YYYY-MM
            if month_key not in monthly_data:
                monthly_data[month_key] = {"income": 0.0, "expenses": 0.0}
            
            if t.amount > 0:
                monthly_data[month_key]["income"] += t.amount
            else:
                monthly_data[month_key]["expenses"] += abs(t.amount)

        return FinancialSummary(
            total_income=total_income,
            total_expenses=total_expenses, # Será negativo
            savings_rate=savings_rate,
            balance=total_income + total_expenses,
            monthly_data=monthly_data
        )

finance_service = FinanceService()

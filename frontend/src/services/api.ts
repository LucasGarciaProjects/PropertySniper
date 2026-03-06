/**
 * API Service para comunicarse con el backend de Libertad Sniper AI
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PropertyAnalysisRequest {
  url: string;
}

export interface PropertyData {
  precio: number;
  m2: number;
  habitaciones?: number;
  planta?: string;
  estado?: string;
  ubicacion?: string;
  url_origen: string;
}

export interface RentabilityAnalysis {
  precio_compra: number;
  gastos_adquisicion: number;
  coste_reforma: number;
  inversion_total: number;
  alquiler_mensual: number;
  alquiler_anual: number;
  gastos_fijos_anuales: number;
  beneficio_neto_anual: number;
  rentabilidad_neta: number;
  semaforo: 'VERDE' | 'AMARILLO' | 'ROJO';
  omr: number;
  property_data: PropertyData;
}

export interface ExtractionLog {
  found_fields: string[];
  missing_fields: string[];
  reasoning: string;
  is_complete: boolean;
  warnings?: string[];
}

export interface AnalysisResponse {
  success: boolean;
  analysis?: RentabilityAnalysis;
  pdf_path?: string;
  error?: string;
  extraction_log?: ExtractionLog;
}

/**
 * Analiza una propiedad inmobiliaria desde una URL
 */
export async function analyzeProperty(url: string): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Error HTTP: ${response.status}`);
    }

    const data: AnalysisResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error analyzing property');
  }
}

/**
 * Descarga un PDF generado
 */
export async function downloadPDF(filename: string): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/download/${filename}`);
    
    if (!response.ok) {
      throw new Error(`Error downloading PDF: ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error downloading PDF');
  }
}

/**
 * Analiza una propiedad desde texto plano usando LLM
 */
export async function analyzeFromText(text: string): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_URL}/analyze-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP Error: ${response.status}`);
    }

    const data: AnalysisResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error analyzing text');
  }
}

/**
 * Analiza una propiedad con datos introducidos manualmente
 */
export async function analyzeManual(data: {
  precio: number;
  m2: number;
  habitaciones?: number;
  planta?: string;
  estado?: string;
  ubicacion?: string;
  coste_reforma?: number;
  alquiler_mensual?: number;
}): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_URL}/analyze-manual`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP Error: ${response.status}`);
    }

    const data_response: AnalysisResponse = await response.json();
    return data_response;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error analyzing manual data');
  }
}

/**
 * Recalcula el análisis con un nuevo alquiler mensual
 */
export async function recalculateAnalysis(data: {
  alquiler_mensual: number;
  precio_compra: number;
  m2: number;
  gastos_adquisicion: number;
  coste_reforma: number;
  ubicacion?: string;
  extraction_log?: ExtractionLog;
}): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_URL}/recalculate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP Error: ${response.status}`);
    }

    const data_response: AnalysisResponse = await response.json();
    return data_response;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error recalculating analysis');
  }
}

/**
 * Verifica el estado de salud del backend
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error('Backend is not available');
  }
}

// --- WEALTH MANAGEMENT SERVICES ---

export interface Transaction {
  id: string;
  date: string;
  category: string;
  concept: string;
  amount: number;
  account: string;
}

export interface FinancialSummary {
  total_income: number;
  total_expenses: number;
  savings_rate: number;
  balance: number;
  monthly_data: Record<string, { income: number; expenses: number }>;
}

export interface Asset {
  id: string;
  name: string;
  type: string;
  value: number;
  details: any;
  date_added: string;
}

export async function getDashboardSummary(): Promise<FinancialSummary> {
  const response = await fetch(`${API_URL}/dashboard/summary`);
  if (!response.ok) throw new Error('Error fetching dashboard summary');
  return response.json();
}

export async function getTransactions(): Promise<Transaction[]> {
  const response = await fetch(`${API_URL}/transactions`);
  if (!response.ok) throw new Error('Error fetching transactions');
  return response.json();
}

export async function addTransaction(transaction: Omit<Transaction, 'id'>): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...transaction, id: '' }), 
  });
  if (!response.ok) throw new Error('Error adding transaction');
  return response.json();
}

export async function saveAsset(asset: Omit<Asset, 'id' | 'date_added'>): Promise<Asset> {
  const response = await fetch(`${API_URL}/assets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...asset, id: '', date_added: '' }),
  });
  if (!response.ok) throw new Error('Error saving asset');
  return response.json();
}

export async function chatWithCoach(message: string): Promise<string> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) throw new Error('Error chatting with coach');
  const data = await response.json();
  return data.response;
}


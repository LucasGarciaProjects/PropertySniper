import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardSummary, type FinancialSummary } from "@/services/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown, PiggyBank } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function WealthDashboard() {
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const { t } = useLanguage();

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const data = await getDashboardSummary();
      setSummary(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return <div className="p-8 text-center text-muted-foreground">{t.dashboard.loading}</div>;
  }

  // Transform monthly_data for Recharts
  const chartData = Object.entries(summary.monthly_data).map(([month, values]) => ({
    name: month,
    ingresos: values.income,
    gastos: values.expenses,
  })).sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t.dashboard.totalIncome}</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              +{summary.total_income.toLocaleString('en-US')}€
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t.dashboard.totalExpenses}</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {summary.total_expenses.toLocaleString('en-US')}€
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t.dashboard.savingsRate}</CardTitle>
            <PiggyBank className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {summary.savings_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {t.dashboard.savingsGoal}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="col-span-4 shadow-sm">
        <CardHeader>
          <CardTitle>{t.dashboard.incomeVsExpenses}</CardTitle>
        </CardHeader>
        <CardContent className="pl-2">
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis 
                  dataKey="name" 
                  stroke="#888888" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                />
                <YAxis 
                  stroke="#888888" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                  tickFormatter={(value) => `${value}€`} 
                />
                <Tooltip 
                  cursor={{ fill: '#f3f4f6' }}
                  contentStyle={{ 
                    borderRadius: '8px', 
                    border: 'none', 
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    backgroundColor: 'rgba(255, 255, 255, 0.95)'
                  }}
                />
                <Bar dataKey="ingresos" name={t.dashboard.totalIncome} fill="#22c55e" radius={[4, 4, 0, 0]} maxBarSize={50} />
                <Bar dataKey="gastos" name={t.dashboard.totalExpenses} fill="#ef4444" radius={[4, 4, 0, 0]} maxBarSize={50} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

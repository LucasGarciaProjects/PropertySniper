import { useEffect, useState } from "react";
import { getTransactions, addTransaction, type Transaction } from "@/services/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Plus } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function ExpenseLog() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useLanguage();
  
  // Form State
  const [type, setType] = useState<"income" | "expense">("expense");
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [category, setCategory] = useState("");
  const [concept, setConcept] = useState("");
  const [amount, setAmount] = useState("");
  const [account, setAccount] = useState("Principal");

  const categories = type === "income" ? t.categories.income : t.categories.expense;

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      const data = await getTransactions();
      setTransactions(data);
    } catch (error) {
      toast.error("Error loading transactions");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || !category || !concept) return;

    const numericAmount = parseFloat(amount);
    const finalAmount = type === "expense" ? -Math.abs(numericAmount) : Math.abs(numericAmount);

    try {
      const newTx = await addTransaction({
        date,
        category,
        concept,
        amount: finalAmount,
        account,
      });
      setTransactions([newTx, ...transactions]);
      toast.success("Transaction added");
      // Reset form (keep date and type)
      setConcept("");
      setAmount("");
      setCategory("");
    } catch (error) {
      toast.error("Error saving");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Form Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t.log.newTransaction}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-6 items-end">
            <div className="space-y-2">
              <label className="text-sm font-medium">{t.log.type}</label>
              <Select value={type} onValueChange={(v: any) => { setType(v); setCategory(""); }}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="income">{t.log.income}</SelectItem>
                  <SelectItem value="expense">{t.log.expense}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">{t.log.date}</label>
              <Input type="date" value={date} onChange={e => setDate(e.target.value)} required />
            </div>

            <div className="space-y-2 md:col-span-1">
               <label className="text-sm font-medium">{t.log.category}</label>
               <Select value={category} onValueChange={setCategory} required>
                <SelectTrigger>
                  <SelectValue placeholder={t.log.select} />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(c => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 md:col-span-1">
              <label className="text-sm font-medium">{t.log.concept}</label>
              <Input value={concept} onChange={e => setConcept(e.target.value)} placeholder="Ex: Dinner" required />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">{t.log.amount}</label>
              <Input type="number" step="0.01" value={amount} onChange={e => setAmount(e.target.value)} placeholder="0.00" required />
            </div>

            <Button type="submit" className="w-full">
              <Plus className="mr-2 h-4 w-4" /> {t.log.add}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t.log.history}</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.log.date}</TableHead>
                <TableHead>{t.log.concept}</TableHead>
                <TableHead>{t.log.category}</TableHead>
                <TableHead>{t.log.account}</TableHead>
                <TableHead className="text-right">{t.log.amount}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">{t.log.loading}</TableCell>
                </TableRow>
              ) : transactions.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell>{tx.date}</TableCell>
                  <TableCell className="font-medium">{tx.concept}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                      {tx.category}
                    </span>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{tx.account}</TableCell>
                  <TableCell className={`text-right font-bold ${tx.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {tx.amount > 0 ? '+' : ''}{tx.amount.toLocaleString('en-US')}€
                  </TableCell>
                </TableRow>
              ))}
              {!loading && transactions.length === 0 && (
                 <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">{t.log.noTransactions}</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

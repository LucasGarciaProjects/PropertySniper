import Header from "@/components/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WealthDashboard from "@/components/WealthDashboard";
import ExpenseLog from "@/components/ExpenseLog";
import SniperSection from "@/components/SniperSection";
import AICoach from "@/components/AICoach";
import { LayoutDashboard, Wallet, Home, MessageSquare } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const Index = () => {
  const { t } = useLanguage();

  return (
    <div className="min-h-screen bg-background pb-12">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px] lg:mx-auto bg-muted/50 p-1">
            <TabsTrigger value="dashboard" className="gap-2 data-[state=active]:bg-background data-[state=active]:shadow-sm">
              <LayoutDashboard className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tabs.dashboard}</span>
            </TabsTrigger>
            <TabsTrigger value="log" className="gap-2 data-[state=active]:bg-background data-[state=active]:shadow-sm">
              <Wallet className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tabs.log}</span>
            </TabsTrigger>
            <TabsTrigger value="sniper" className="gap-2 data-[state=active]:bg-background data-[state=active]:shadow-sm">
              <Home className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tabs.sniper}</span>
            </TabsTrigger>
            <TabsTrigger value="coach" className="gap-2 data-[state=active]:bg-background data-[state=active]:shadow-sm">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">{t.tabs.coach}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-4 focus-visible:outline-none focus-visible:ring-0">
            <div className="flex flex-col gap-1 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">{t.dashboard.title}</h2>
              <p className="text-muted-foreground">{t.dashboard.subtitle}</p>
            </div>
            <WealthDashboard />
          </TabsContent>

          <TabsContent value="log" className="space-y-4 focus-visible:outline-none focus-visible:ring-0">
             <div className="flex flex-col gap-1 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">{t.log.title}</h2>
              <p className="text-muted-foreground">{t.log.subtitle}</p>
            </div>
            <ExpenseLog />
          </TabsContent>

          <TabsContent value="sniper" className="space-y-4 focus-visible:outline-none focus-visible:ring-0">
             <div className="flex flex-col gap-1 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">{t.sniper.title}</h2>
              <p className="text-muted-foreground">{t.sniper.subtitle}</p>
            </div>
            <SniperSection />
          </TabsContent>

          <TabsContent value="coach" className="space-y-4 focus-visible:outline-none focus-visible:ring-0">
             <div className="flex flex-col gap-1 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">{t.coach.title}</h2>
              <p className="text-muted-foreground">{t.coach.subtitle}</p>
            </div>
            <AICoach />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="w-full py-8 px-4 border-t border-border mt-12">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-sm text-muted-foreground">
            {t.footer.copyright} <span className="font-medium text-foreground">{t.footer.role}</span>.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;

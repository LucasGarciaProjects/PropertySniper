import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface HeroInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
}

const HeroInput = ({ onAnalyze, isLoading }: HeroInputProps) => {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url);
    }
  };

  return (
    <section className="w-full py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4 animate-fade-in-up">
          Analiza cualquier inversión
          <span className="block text-accent mt-2">en segundos</span>
        </h2>
        <p className="text-muted-foreground text-lg mb-10 animate-fade-in-up animation-delay-100">
          Pega el enlace de Idealista o Fotocasa y descubre si es una oportunidad real
        </p>
        
        <form onSubmit={handleSubmit} className="animate-fade-in-up animation-delay-200">
          <div className="flex flex-col sm:flex-row gap-3 p-2 bg-card rounded-2xl border border-border shadow-lg">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <Input
                type="url"
                placeholder="https://www.idealista.com/inmueble/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full h-14 pl-12 pr-4 text-base bg-muted border-0 rounded-xl focus-visible:ring-2 focus-visible:ring-accent"
              />
            </div>
            <Button 
              type="submit" 
              disabled={isLoading || !url.trim()}
              className="h-14 px-8 text-base font-semibold bg-accent hover:bg-emerald-light text-accent-foreground rounded-xl transition-all duration-300 hover:shadow-lg disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analizando...
                </>
              ) : (
                "Analizar Oportunidad"
              )}
            </Button>
          </div>
        </form>
      </div>
    </section>
  );
};

export default HeroInput;

import { useState, useEffect } from "react";
import { TrendingUp, Wallet, BadgeEuro, Home, Pencil, Check, X } from "lucide-react";
import GaugeChart from "./GaugeChart";
import ResultCard from "./ResultCard";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface DashboardProps {
  data: {
    rentabilidadNeta: number;
    cashflowMensual: number;
    ofertaMaxima: number;
    precioOriginal: number;
    alquilerMensual: number;
    m2: number;
    gastosAdquisicion: number;
    costeReforma: number;
    ubicacion?: string;
  };
  onAlquilerChange?: (newAlquiler: number) => void;
}

const Dashboard = ({ data, onAlquilerChange }: DashboardProps) => {
  const descuento = ((data.precioOriginal - data.ofertaMaxima) / data.precioOriginal * 100).toFixed(1);
  const [isEditingAlquiler, setIsEditingAlquiler] = useState(false);
  const [tempAlquiler, setTempAlquiler] = useState(data.alquilerMensual.toString());

  // Actualizar tempAlquiler cuando cambia data.alquilerMensual
  useEffect(() => {
    setTempAlquiler(data.alquilerMensual.toString());
  }, [data.alquilerMensual]);

  const handleAlquilerSave = () => {
    const newAlquiler = parseFloat(tempAlquiler);
    if (!isNaN(newAlquiler) && newAlquiler > 0 && onAlquilerChange) {
      onAlquilerChange(newAlquiler);
      setIsEditingAlquiler(false);
    }
  };

  const handleAlquilerCancel = () => {
    setTempAlquiler(data.alquilerMensual.toString());
    setIsEditingAlquiler(false);
  };

  const formatEuro = (value: number) => {
    return Math.round(value).toLocaleString('es-ES') + ' €';
  };

  return (
    <section className="w-full py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Rentabilidad Neta */}
          <ResultCard title="Rentabilidad Neta" delay={0}>
            <div className="flex flex-col items-center">
              <GaugeChart 
                value={data.rentabilidadNeta} 
                maxValue={15}
                label="Objetivo: 8%+"
              />
              <div className="flex items-center gap-2 mt-4 text-accent">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm font-medium">Por encima de la media</span>
              </div>
            </div>
          </ResultCard>

          {/* Alquiler Estimado - Editable */}
          <ResultCard title="Alquiler Estimado" delay={100}>
            <div className="flex flex-col items-center justify-center h-full min-h-[160px]">
              {!isEditingAlquiler ? (
                <>
                  <div className="flex flex-col items-center gap-2">
                    <div className="flex items-center gap-2">
                      <Home className="w-6 h-6 text-accent" />
                      <span className="text-sm font-medium text-muted-foreground">
                        Alquiler Estimado:
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-4xl sm:text-5xl font-bold text-foreground">
                        {formatEuro(data.alquilerMensual)}
                      </span>
                      <button
                        onClick={() => setIsEditingAlquiler(true)}
                        className="p-1.5 hover:bg-muted rounded transition-colors"
                        title="Editar alquiler"
                      >
                        <Pencil className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                      </button>
                    </div>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {data.m2 > 0 && `${Math.round(data.alquilerMensual / data.m2)} €/m²`}
                  </span>
                </>
              ) : (
                <div className="w-full space-y-3">
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={tempAlquiler}
                      onChange={(e) => setTempAlquiler(e.target.value)}
                      className="text-2xl font-bold text-center"
                      autoFocus
                      min="0"
                      step="50"
                    />
                    <span className="text-2xl font-bold">€</span>
                  </div>
                  <div className="flex gap-2 justify-center">
                    <Button
                      size="sm"
                      onClick={handleAlquilerSave}
                      className="bg-accent hover:bg-accent/90"
                    >
                      <Check className="w-4 h-4 mr-1" />
                      Aplicar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleAlquilerCancel}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Cancelar
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </ResultCard>

          {/* Cashflow Mensual */}
          <ResultCard title="Cashflow Mensual" delay={150}>
            <div className="flex flex-col items-center justify-center h-full min-h-[160px]">
              <div className="flex items-center gap-3 mb-2">
                <Wallet className="w-8 h-8 text-accent" />
                <span className="text-4xl sm:text-5xl font-bold text-foreground">
                  {data.cashflowMensual > 0 ? '+' : ''}{Math.round(data.cashflowMensual).toLocaleString('es-ES')} €
                </span>
              </div>
              <span className={cn(
                "text-sm font-medium px-3 py-1 rounded-full",
                data.cashflowMensual > 0 
                  ? "bg-accent/10 text-accent" 
                  : "bg-destructive/10 text-destructive"
              )}>
                {data.cashflowMensual > 0 ? 'Cashflow Positivo' : 'Cashflow Negativo'}
              </span>
            </div>
          </ResultCard>

          {/* OMR */}
          <ResultCard title="Oferta Máxima Recomendada" variant="gold" delay={250}>
            <div className="flex flex-col items-center justify-center h-full min-h-[160px]">
              <div className="flex items-center gap-3 mb-2">
                <BadgeEuro className="w-8 h-8 text-gold" />
                <span className="text-4xl sm:text-5xl font-bold gradient-text-gold">
                  {formatEuro(data.ofertaMaxima)}
                </span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <span className="text-sm text-muted-foreground line-through">
                  Precio actual: {formatEuro(data.precioOriginal)}
                </span>
                <span className="text-sm font-semibold text-gold">
                  Descuento del {descuento}%
                </span>
              </div>
            </div>
          </ResultCard>
        </div>
      </div>
    </section>
  );
};

// Helper to use cn
import { cn } from "@/lib/utils";

export default Dashboard;

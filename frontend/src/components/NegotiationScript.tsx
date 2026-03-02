import { MessageSquare, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";

interface NegotiationScriptProps {
  script: string;
  puntoDebiles: string[];
}

const NegotiationScript = ({ script, puntoDebiles }: NegotiationScriptProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(script);
    setCopied(true);
    toast.success("Guion copiado al portapapeles");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section 
      className="w-full py-8 px-4 sm:px-6 lg:px-8 opacity-0"
      style={{ animation: "fadeInUp 0.6s ease-out 300ms forwards" }}
    >
      <div className="max-w-7xl mx-auto">
        <div className="card-elevated p-6 sm:p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">Guion de Negociación</h3>
                <p className="text-sm text-muted-foreground">Basado en puntos débiles detectados</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-accent" />
                  Copiado
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copiar
                </>
              )}
            </Button>
          </div>

          {/* Puntos Débiles Tags */}
          <div className="flex flex-wrap gap-2 mb-6">
            {puntoDebiles.map((punto, index) => (
              <span 
                key={index}
                className="px-3 py-1 text-sm bg-destructive/10 text-destructive rounded-full font-medium"
              >
                {punto}
              </span>
            ))}
          </div>

          {/* Script */}
          <div className="bg-muted rounded-xl p-6 border border-border">
            <p className="text-foreground leading-relaxed whitespace-pre-line">
              {script}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default NegotiationScript;

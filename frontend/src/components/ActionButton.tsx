import { FileText, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface ActionButtonProps {
  onDownloadPDF?: () => void;
}

const ActionButton = ({ onDownloadPDF }: ActionButtonProps) => {
  const handleGeneratePDF = () => {
    if (onDownloadPDF) {
      onDownloadPDF();
    } else {
      toast.info("El PDF se generará automáticamente después del análisis", {
        description: "Espera a que se complete el análisis",
      });
    }
  };

  return (
    <section 
      className="w-full py-12 px-4 sm:px-6 lg:px-8 opacity-0"
      style={{ animation: "fadeInUp 0.6s ease-out 400ms forwards" }}
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button
            onClick={handleGeneratePDF}
            size="lg"
            className="h-14 px-8 text-base font-semibold bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl transition-all duration-300 hover:shadow-lg gap-3"
          >
            <FileText className="w-5 h-5" />
            Generar Informe PDF para el Banco
            <Download className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-center text-sm text-muted-foreground mt-4">
          Incluye análisis completo, proyecciones y documentación para solicitar financiación
        </p>
      </div>
    </section>
  );
};

export default ActionButton;

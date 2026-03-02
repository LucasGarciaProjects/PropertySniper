import { useState } from "react";
import { CheckCircle2, AlertCircle, ChevronDown, ChevronUp, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import type { ExtractionLog } from "@/services/api";

interface AnalysisBreakdownProps {
  extractionLog: ExtractionLog;
}

const AnalysisBreakdown = ({ extractionLog }: AnalysisBreakdownProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const fieldLabels: Record<string, string> = {
    precio: "Precio de Venta",
    metros_cuadrados: "Metros Cuadrados",
    habitaciones: "Habitaciones",
    planta: "Planta",
    estado: "Estado",
    ubicacion: "Ubicación",
    tiene_ascensor: "Ascensor",
  };

  return (
    <Card className="w-full max-w-4xl mx-auto mt-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-accent" />
            <CardTitle>Auditoría de IA</CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-2"
          >
            {isOpen ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Ocultar detalle
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Ver detalle del análisis técnico
              </>
            )}
          </Button>
        </div>
        <CardDescription>
          Detalle de cómo la IA ha extraído y procesado los datos del anuncio
        </CardDescription>
      </CardHeader>

      {isOpen && (
        <CardContent className="space-y-6">
          {/* Estado del análisis */}
          <div className="flex items-center gap-2 p-3 rounded-lg bg-muted">
            {extractionLog.is_complete ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span className="font-semibold text-green-700 dark:text-green-400">
                  Análisis completo: Todos los datos críticos encontrados
                </span>
              </>
            ) : (
              <>
                <AlertCircle className="w-5 h-5 text-orange-500" />
                <span className="font-semibold text-orange-700 dark:text-orange-400">
                  Análisis incompleto: Faltan datos críticos
                </span>
              </>
            )}
          </div>

          {/* Campos encontrados */}
          <div className="space-y-3">
            <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              Campos encontrados directamente en el texto
            </h3>
            <div className="flex flex-wrap gap-2">
              {extractionLog.found_fields.length > 0 ? (
                extractionLog.found_fields.map((field) => (
                  <Badge
                    key={field}
                    variant="outline"
                    className="bg-green-50 text-green-700 border-green-300 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800"
                  >
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    {fieldLabels[field] || field}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-muted-foreground">
                  No se encontraron campos directamente en el texto
                </span>
              )}
            </div>
          </div>

          {/* Campos estimados */}
          {extractionLog.missing_fields.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-orange-500" />
                Campos estimados o asumidos
              </h3>
              <div className="flex flex-wrap gap-2">
                {extractionLog.missing_fields.map((field) => (
                  <Badge
                    key={field}
                    variant="outline"
                    className="bg-orange-50 text-orange-700 border-orange-300 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800"
                  >
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {fieldLabels[field] || field}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {extractionLog.warnings && extractionLog.warnings.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                Avisos Importantes
              </h3>
              <div className="space-y-2">
                {extractionLog.warnings.map((warning, index) => (
                  <div
                    key={index}
                    className="p-3 rounded-lg bg-red-50 border border-red-200 dark:bg-red-900/20 dark:border-red-800"
                  >
                    <p className="text-sm text-red-700 dark:text-red-400">{warning}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Razonamiento de la IA */}
          <div className="space-y-3">
            <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
              <Brain className="w-4 h-4 text-accent" />
              Razonamiento de la IA
            </h3>
            <Textarea
              value={extractionLog.reasoning}
              readOnly
              className="min-h-[120px] bg-muted/50 text-sm resize-none"
              placeholder="El razonamiento de la IA aparecerá aquí..."
            />
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default AnalysisBreakdown;


import { useState, useMemo, useEffect } from "react";
import MultiInput from "@/components/MultiInput";
import Dashboard from "@/components/Dashboard";
import NegotiationScript from "@/components/NegotiationScript";
import ActionButton from "@/components/ActionButton";
import AnalysisBreakdown from "@/components/AnalysisBreakdown";
import { analyzeProperty, analyzeFromText, analyzeManual, downloadPDF, recalculateAnalysis, saveAsset, type RentabilityAnalysis, type ExtractionLog } from "@/services/api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Save } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

interface AnalysisData {
  rentabilidadNeta: number;
  cashflowMensual: number;
  ofertaMaxima: number;
  precioOriginal: number;
  alquilerMensual: number;
  m2: number;
  gastosAdquisicion: number;
  costeReforma: number;
  ubicacion?: string;
}

export default function SniperSection() {
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [negotiationScript, setNegotiationScript] = useState<string>("");
  const [puntosDebiles, setPuntosDebiles] = useState<string[]>([]);
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [extractionLog, setExtractionLog] = useState<ExtractionLog | null>(null);
  const [alquilerMensual, setAlquilerMensual] = useState<number | null>(null);
  const { t } = useLanguage();

  const processAnalysisResponse = (response: any) => {
    if (response.extraction_log) {
      setExtractionLog(response.extraction_log);
      if (!response.extraction_log.is_complete) {
        toast.error(response.error || "Análisis incompleto: faltan datos críticos", { duration: 5000 });
        setShowResults(false);
        return;
      }
    } else {
      setExtractionLog(null);
    }

    if (!response.success || !response.analysis) {
      throw new Error(response.error || "Error al analizar la propiedad");
    }

    const analysis = response.analysis;

    const mappedData: AnalysisData = {
      rentabilidadNeta: analysis.rentabilidad_neta,
      cashflowMensual: analysis.alquiler_mensual - (analysis.gastos_fijos_anuales / 12),
      ofertaMaxima: analysis.omr,
      precioOriginal: analysis.precio_compra,
      alquilerMensual: analysis.alquiler_mensual,
      m2: analysis.property_data.m2,
      gastosAdquisicion: analysis.gastos_adquisicion,
      costeReforma: analysis.coste_reforma,
      ubicacion: analysis.property_data.ubicacion,
    };

    setAnalysisData(mappedData);
    setAlquilerMensual(analysis.alquiler_mensual);
    setPdfPath(response.pdf_path || null);

    generateNegotiationScript(analysis);

    setShowResults(true);
    toast.success(t.sniper.analysisComplete, { duration: 3000 });
  };

  const recalculateInversion = useMemo(() => {
    return (nuevoAlquiler: number, baseData: AnalysisData): AnalysisData => {
      const precioCompra = baseData.precioOriginal;
      const m2 = baseData.m2;
      const costeReforma = baseData.costeReforma;
      const gastosAdquisicion = precioCompra * 0.10 + 3000;
      const inversionTotal = precioCompra + gastosAdquisicion + costeReforma;
      const alquilerAnual = nuevoAlquiler * 12;
      const gastosFijosAnuales = alquilerAnual * 0.20;
      const beneficioNetoAnual = alquilerAnual - gastosFijosAnuales;
      const rentabilidadNeta = (beneficioNetoAnual / inversionTotal) * 100;
      const gastosVariables = nuevoAlquiler * 0.20;
      const cashflowMensual = (nuevoAlquiler * 0.8) - gastosVariables;
      const inversionTotalNecesaria = beneficioNetoAnual / 0.08;
      const omr = (inversionTotalNecesaria - 3000 - costeReforma) / 1.10;

      return {
        ...baseData,
        rentabilidadNeta: Math.max(0, rentabilidadNeta),
        cashflowMensual: Math.max(0, cashflowMensual),
        ofertaMaxima: Math.max(0, omr),
        alquilerMensual: nuevoAlquiler,
        gastosAdquisicion,
      };
    };
  }, []);

  const updatedAnalysisData = useMemo(() => {
    if (!analysisData || alquilerMensual === null) {
      return analysisData;
    }
    return recalculateInversion(alquilerMensual, analysisData);
  }, [analysisData, alquilerMensual, recalculateInversion]);

  useEffect(() => {
    if (updatedAnalysisData && alquilerMensual !== null && analysisData) {
      const alquilerCambio = updatedAnalysisData.alquilerMensual !== analysisData.alquilerMensual;
      if (alquilerCambio) {
        setAnalysisData(updatedAnalysisData);
        generateNegotiationScriptFromData(updatedAnalysisData);
      }
    }
  }, [alquilerMensual]);

  useEffect(() => {
    if (analysisData && showResults) {
      generateNegotiationScriptFromData(analysisData);
    }
  }, [analysisData?.rentabilidadNeta, analysisData?.ofertaMaxima, analysisData?.precioOriginal]);

  const handleAnalyze = async (url: string) => {
    setIsLoading(true);
    setShowResults(false);
    setAnalysisData(null);
    setNegotiationScript("");
    setPuntosDebiles([]);
    setPdfPath(null);
    setExtractionLog(null);

    try {
      toast.info(t.sniper.analyze, { duration: 2000 });
      const response = await analyzeProperty(url);
      processAnalysisResponse(response);
    } catch (error) {
      console.error("Error al analizar:", error);
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      toast.error(errorMessage, { duration: 5000 });
      setShowResults(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeText = async (text: string) => {
    setIsLoading(true);
    setShowResults(false);
    setAnalysisData(null);
    setAlquilerMensual(null);
    setNegotiationScript("");
    setPuntosDebiles([]);
    setPdfPath(null);
    setExtractionLog(null);

    try {
      toast.info(t.sniper.extract, { duration: 2000 });
      const response = await analyzeFromText(text);
      processAnalysisResponse(response);
    } catch (error) {
      console.error("Error al analizar texto:", error);
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      toast.error(errorMessage, { duration: 5000 });
      setShowResults(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeManual = async (data: {
    precio: number;
    m2: number;
    habitaciones?: number;
    planta?: string;
    estado?: string;
    ubicacion?: string;
    coste_reforma?: number;
    alquiler_mensual?: number;
  }) => {
    setIsLoading(true);
    setShowResults(false);
    setAnalysisData(null);
    setAlquilerMensual(null);
    setNegotiationScript("");
    setPuntosDebiles([]);
    setPdfPath(null);
    setExtractionLog(null);

    try {
      toast.info(t.sniper.calculating, { duration: 2000 });
      const response = await analyzeManual(data);
      processAnalysisResponse(response);
    } catch (error) {
      console.error("Error al analizar manual:", error);
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      toast.error(errorMessage, { duration: 5000 });
      setShowResults(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeImage = async (file: File) => {
    toast.info(t.sniper.ocr, { duration: 4000 });
  };

  const generateNegotiationScript = (analysis: RentabilityAnalysis) => {
    const descuento = ((analysis.precio_compra - analysis.omr) / analysis.precio_compra * 100).toFixed(1);
    const ubicacion = analysis.property_data.ubicacion || "la propiedad";
    const estado = analysis.property_data.estado || "bueno";
    const necesitaReforma = estado.toLowerCase().includes("reformar");

    const script = `Buenos días, me interesa ${ubicacion}.

He analizado la propiedad y he detectado que el precio actual está un ${descuento}% por encima de lo que considero adecuado para una inversión rentable.

${necesitaReforma ? `Además, he visto que necesita reforma (estimado: ${analysis.coste_reforma.toLocaleString('es-ES')}€).` : ""}

Tengo la financiación aprobada y puedo cerrar la operación esta semana si llegamos a un acuerdo en ${analysis.omr.toLocaleString('es-ES')}€.

¿Tendría disponibilidad para visitarlo mañana?`;

    setNegotiationScript(script);

    const debiles: string[] = [];
    if (analysis.rentabilidad_neta < 5) debiles.push("Rentabilidad baja");
    if (analysis.rentabilidad_neta < 7) debiles.push("Por debajo del objetivo del 8%");
    if (necesitaReforma) debiles.push("Necesita reforma");
    if (analysis.precio_compra > analysis.omr * 1.1) debiles.push("Precio sobre valor de mercado");
    if (analysis.property_data.planta && analysis.property_data.planta.toLowerCase().includes("baja")) debiles.push("Planta baja");

    setPuntosDebiles(debiles.length > 0 ? debiles : ["Análisis en curso"]);
  };

  const generateNegotiationScriptFromData = (data: AnalysisData) => {
    const descuento = ((data.precioOriginal - data.ofertaMaxima) / data.precioOriginal * 100).toFixed(1);
    const ubicacion = data.ubicacion || "la propiedad";
    const necesitaReforma = data.costeReforma > 1000;

    const script = `Buenos días, me interesa ${ubicacion}.

He analizado la propiedad y he detectado que el precio actual está un ${descuento}% por encima de lo que considero adecuado para una inversión rentable.

${necesitaReforma ? `Además, he visto que necesita reforma (estimado: ${Math.round(data.costeReforma).toLocaleString('es-ES')}€).` : ""}

Tengo la financiación aprobada y puedo cerrar la operación esta semana si llegamos a un acuerdo en ${Math.round(data.ofertaMaxima).toLocaleString('es-ES')}€.

¿Tendría disponibilidad para visitarlo mañana?`;

    setNegotiationScript(script);

    const debiles: string[] = [];
    if (data.rentabilidadNeta < 5) debiles.push("Rentabilidad baja");
    if (data.rentabilidadNeta < 7) debiles.push("Por debajo del objetivo del 8%");
    if (necesitaReforma) debiles.push("Necesita reforma");
    if (data.precioOriginal > data.ofertaMaxima * 1.1) debiles.push("Precio sobre valor de mercado");

    setPuntosDebiles(debiles.length > 0 ? debiles : ["Análisis en curso"]);
  };

  const handleDownloadPDF = async () => {
    if (!analysisData || alquilerMensual === null) {
      toast.error("No hay datos disponibles para generar el PDF");
      return;
    }

    try {
      toast.info(t.sniper.generatePdf, { duration: 2000 });
      
      const response = await recalculateAnalysis({
        alquiler_mensual: alquilerMensual,
        precio_compra: analysisData.precioOriginal,
        m2: analysisData.m2,
        gastos_adquisicion: analysisData.gastosAdquisicion,
        coste_reforma: analysisData.costeReforma,
        ubicacion: analysisData.ubicacion,
        extraction_log: extractionLog || undefined,
      });

      if (!response) throw new Error("No se recibió respuesta del servidor");

      if (response.success && response.pdf_path) {
        const filename = response.pdf_path.split("/").pop() || response.pdf_path.split("\\").pop() || "analisis.pdf";
        setPdfPath(response.pdf_path);
        await downloadPDF(filename);
        toast.success(t.sniper.downloadPdf);
      } else if (response.success && !response.pdf_path) {
        if (pdfPath) {
          const filename = pdfPath.split("/").pop() || pdfPath.split("\\").pop() || "analisis.pdf";
          await downloadPDF(filename);
          toast.success(t.sniper.downloadPdf);
        } else {
          throw new Error("El servidor no generó el PDF y no hay PDF anterior disponible");
        }
      } else {
        throw new Error(response.error || "Error al generar el PDF en el servidor");
      }
    } catch (error) {
      console.error("Error al generar/descargar PDF:", error);
      const errorMessage = error instanceof Error ? error.message : "Error desconocido";
      toast.error(`Error: ${errorMessage}`, { duration: 5000 });
    }
  };

  const handleSaveAsset = async () => {
    if (!analysisData) return;
    try {
      await saveAsset({
        name: analysisData.ubicacion || "Propiedad Sniper",
        type: "Inmueble",
        value: analysisData.ofertaMaxima,
        details: analysisData
      });
      toast.success(t.sniper.added);
    } catch (error) {
      toast.error(t.sniper.error);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <MultiInput 
        onAnalyzeText={handleAnalyzeText}
        onAnalyzeManual={handleAnalyzeManual}
        onAnalyzeImage={handleAnalyzeImage}
        isLoading={isLoading}
      />
      
      {showResults && analysisData && (
        <>
          <div className="flex justify-end">
             <Button onClick={handleSaveAsset} className="gap-2 bg-blue-600 hover:bg-blue-700 text-white">
               <Save className="h-4 w-4" /> {t.sniper.addToProjections}
             </Button>
          </div>

          <Dashboard 
            data={analysisData} 
            onAlquilerChange={async (newAlquiler: number) => {
              setAlquilerMensual(newAlquiler);
              try {
                const response = await recalculateAnalysis({
                  alquiler_mensual: newAlquiler,
                  precio_compra: analysisData.precioOriginal,
                  m2: analysisData.m2,
                  gastos_adquisicion: analysisData.gastosAdquisicion,
                  coste_reforma: analysisData.costeReforma,
                  ubicacion: analysisData.ubicacion,
                  extraction_log: extractionLog || undefined,
                });
                
                if (response.success && response.analysis) {
                  if (response.pdf_path) setPdfPath(response.pdf_path);
                  if (response.extraction_log) setExtractionLog(response.extraction_log);
                }
              } catch (error) {
                console.error("Error al persistir en backend:", error);
              }
            }}
          />
          {extractionLog && (
            <AnalysisBreakdown extractionLog={extractionLog} />
          )}
          {negotiationScript && (
            <NegotiationScript 
              script={negotiationScript} 
              puntoDebiles={puntosDebiles} 
            />
          )}
          <ActionButton onDownloadPDF={pdfPath ? handleDownloadPDF : undefined} />
        </>
      )}
    </div>
  );
}

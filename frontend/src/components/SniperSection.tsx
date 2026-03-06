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
        toast.error(response.error || "Incomplete analysis: critical data missing", { duration: 5000 });
        setShowResults(false);
        return;
      }
    } else {
      setExtractionLog(null);
    }

    if (!response.success || !response.analysis) {
      throw new Error(response.error || "Error analyzing property");
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
      console.error("Error analyzing:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
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
      console.error("Error analyzing text:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
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
      console.error("Error analyzing manual:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
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
    const ubicacion = analysis.property_data.ubicacion || "the property";
    const estado = analysis.property_data.estado || "good";
    const necesitaReforma = estado.toLowerCase().includes("reform") || estado.toLowerCase().includes("fix");

    const script = `Good morning, I am interested in ${ubicacion}.
    I have analyzed the property and detected that the current price is ${descuento}% above what I consider appropriate for a profitable investment.
    ${necesitaReforma ? `Also, I noticed it needs renovation (estimated: ${analysis.coste_reforma.toLocaleString('en-US')}€).` : ""}
    I have approved financing and can close the deal this week if we agree on ${analysis.omr.toLocaleString('en-US')}€.
    Would you be available for a visit tomorrow?`;

    setNegotiationScript(script);

    const debiles: string[] = [];
    if (analysis.rentabilidad_neta < 5) debiles.push("Low yield");
    if (analysis.rentabilidad_neta < 7) debiles.push("Below 8% goal");
    if (necesitaReforma) debiles.push("Needs renovation");
    if (analysis.precio_compra > analysis.omr * 1.1) debiles.push("Price above market value");
    if (analysis.property_data.planta && (analysis.property_data.planta.toLowerCase().includes("baja") || analysis.property_data.planta.toLowerCase().includes("ground"))) debiles.push("Ground floor");

    setPuntosDebiles(debiles.length > 0 ? debiles : ["Analysis in progress"]);
  };

  const generateNegotiationScriptFromData = (data: AnalysisData) => {
    const descuento = ((data.precioOriginal - data.ofertaMaxima) / data.precioOriginal * 100).toFixed(1);
    const ubicacion = data.ubicacion || "the property";
    const necesitaReforma = data.costeReforma > 1000;

    const script = `Good morning, I am interested in ${ubicacion}.
    I have analyzed the property and detected that the current price is ${descuento}% above what I consider appropriate for a profitable investment.
    ${necesitaReforma ? `Also, I noticed it needs renovation (estimated: ${Math.round(data.costeReforma).toLocaleString('en-US')}€).` : ""}
    I have approved financing and can close the deal this week if we agree on ${Math.round(data.ofertaMaxima).toLocaleString('en-US')}€.
    Would you be available for a visit tomorrow?`;

    setNegotiationScript(script);

    const debiles: string[] = [];
    if (data.rentabilidadNeta < 5) debiles.push("Low yield");
    if (data.rentabilidadNeta < 7) debiles.push("Below 8% goal");
    if (necesitaReforma) debiles.push("Needs renovation");
    if (data.precioOriginal > data.ofertaMaxima * 1.1) debiles.push("Price above market value");

    setPuntosDebiles(debiles.length > 0 ? debiles : ["Analysis in progress"]);
  };

  const handleDownloadPDF = async () => {
    if (!analysisData || alquilerMensual === null) {
      toast.error("No data available to generate PDF");
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

      if (!response) throw new Error("No response from server");

      if (response.success && response.pdf_path) {
        const filename = response.pdf_path.split("/").pop() || response.pdf_path.split("\\").pop() || "analysis.pdf";
        setPdfPath(response.pdf_path);
        await downloadPDF(filename);
        toast.success(t.sniper.downloadPdf);
      } else if (response.success && !response.pdf_path) {
        if (pdfPath) {
          const filename = pdfPath.split("/").pop() || pdfPath.split("\\").pop() || "analysis.pdf";
          await downloadPDF(filename);
          toast.success(t.sniper.downloadPdf);
        } else {
          throw new Error("Server did not generate PDF and no previous PDF available");
        }
      } else {
        throw new Error(response.error || "Error generating PDF on server");
      }
    } catch (error) {
      console.error("Error generating/downloading PDF:", error);
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      toast.error(`Error: ${errorMessage}`, { duration: 5000 });
    }
  };

  const handleSaveAsset = async () => {
    if (!analysisData) return;
    try {
      await saveAsset({
        name: analysisData.ubicacion || "Sniper Property",
        type: "Real Estate",
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

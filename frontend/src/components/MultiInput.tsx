import { useState } from "react";
import { FileText, Image, Sliders, Loader2, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { useLanguage } from "@/context/LanguageContext";

interface MultiInputProps {
  onAnalyzeText: (text: string) => void;
  onAnalyzeManual: (data: {
    precio: number;
    m2: number;
    habitaciones?: number;
    planta?: string;
    estado?: string;
    ubicacion?: string;
    coste_reforma?: number;
    alquiler_mensual?: number;
  }) => void;
  onAnalyzeImage: (file: File) => void;
  isLoading: boolean;
}

const MultiInput = ({ onAnalyzeText, onAnalyzeManual, onAnalyzeImage, isLoading }: MultiInputProps) => {
  const [text, setText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { t } = useLanguage();
  
  // Valores manuales
  const [precio, setPrecio] = useState([200000]);
  const [m2, setM2] = useState([80]);
  const [habitaciones, setHabitaciones] = useState([3]);
  const [costeReforma, setCosteReforma] = useState([0]);
  const [alquilerMensual, setAlquilerMensual] = useState([0]);
  const [planta, setPlanta] = useState("");
  const [estado, setEstado] = useState("bueno");
  const [ubicacion, setUbicacion] = useState("");

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      onAnalyzeText(text);
    }
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAnalyzeManual({
      precio: precio[0],
      m2: m2[0],
      habitaciones: habitaciones[0],
      planta: planta || undefined,
      estado: estado || undefined,
      ubicacion: ubicacion || undefined,
      coste_reforma: costeReforma[0] > 0 ? costeReforma[0] : undefined,
      alquiler_mensual: alquilerMensual[0] > 0 ? alquilerMensual[0] : undefined,
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleImageAnalyze = () => {
    if (selectedFile) {
      onAnalyzeImage(selectedFile);
    }
  };

  const handlePaste = async () => {
    try {
      const clipboardText = await navigator.clipboard.readText();
      setText(clipboardText);
    } catch (err) {
      // Fallback: el usuario puede pegar manualmente
    }
  };

  return (
    <section className="w-full py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-4 animate-fade-in-up">
            {t.sniper.multiInput.title}
            <span className="block text-accent mt-2">{t.sniper.multiInput.titleAccent}</span>
          </h2>
          <p className="text-muted-foreground text-lg animate-fade-in-up animation-delay-100">
            {t.sniper.multiInput.subtitle}
          </p>
        </div>

        <Tabs defaultValue="text" className="animate-fade-in-up animation-delay-200">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="text" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              {t.sniper.multiInput.tabs.text}
            </TabsTrigger>
            <TabsTrigger value="image" className="flex items-center gap-2">
              <Image className="w-4 h-4" />
              {t.sniper.multiInput.tabs.image}
            </TabsTrigger>
            <TabsTrigger value="manual" className="flex items-center gap-2">
              <Sliders className="w-4 h-4" />
              {t.sniper.multiInput.tabs.manual}
            </TabsTrigger>
          </TabsList>

          {/* Pestaña 1: Pegar Texto */}
          <TabsContent value="text">
            <Card>
              <CardHeader>
                <CardTitle>{t.sniper.multiInput.textTab.title}</CardTitle>
                <CardDescription>
                  {t.sniper.multiInput.textTab.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleTextSubmit}>
                  <div className="space-y-4">
                    <div className="relative">
                      <Textarea
                        placeholder={t.sniper.multiInput.textTab.placeholder}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        className="min-h-[300px] text-base bg-muted border-border resize-none"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handlePaste}
                        className="absolute top-2 right-2"
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        {t.sniper.multiInput.textTab.paste}
                      </Button>
                    </div>
                    <Button
                      type="submit"
                      disabled={isLoading || !text.trim()}
                      className="w-full h-14 text-base font-semibold bg-accent hover:bg-emerald-light text-accent-foreground"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          {t.sniper.multiInput.textTab.analyzing}
                        </>
                      ) : (
                        t.sniper.multiInput.textTab.analyze
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Pestaña 2: Foto */}
          <TabsContent value="image">
            <Card>
              <CardHeader>
                <CardTitle>{t.sniper.multiInput.imageTab.title}</CardTitle>
                <CardDescription>
                  {t.sniper.multiInput.imageTab.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border-2 border-dashed border-border rounded-xl p-12 text-center hover:border-accent transition-colors">
                    <Image className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <Label htmlFor="image-upload" className="cursor-pointer">
                      <span className="text-accent font-semibold">{t.sniper.multiInput.imageTab.drop}</span> {t.sniper.multiInput.imageTab.dropSuffix}
                    </Label>
                    <Input
                      id="image-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    {selectedFile && (
                      <div className="mt-4 space-y-2">
                        <p className="text-sm text-muted-foreground">
                          {t.sniper.multiInput.imageTab.selected} <span className="font-semibold text-foreground">{selectedFile.name}</span>
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {t.sniper.multiInput.imageTab.size} {(selectedFile.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    )}
                  </div>
                  {selectedFile && (
                    <Button
                      onClick={handleImageAnalyze}
                      disabled={isLoading}
                      className="w-full h-14 text-base font-semibold bg-accent hover:bg-emerald-light text-accent-foreground"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          {t.sniper.multiInput.imageTab.analyzing}
                        </>
                      ) : (
                        <>
                          <Image className="w-5 h-5 mr-2" />
                          {t.sniper.multiInput.imageTab.analyze}
                        </>
                      )}
                    </Button>
                  )}
                  {!selectedFile && (
                    <p className="text-xs text-muted-foreground text-center">
                      {t.sniper.multiInput.imageTab.warning}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Pestaña 3: Manual */}
          <TabsContent value="manual">
            <Card>
              <CardHeader>
                <CardTitle>{t.sniper.multiInput.manualTab.title}</CardTitle>
                <CardDescription>
                  {t.sniper.multiInput.manualTab.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleManualSubmit}>
                  <div className="space-y-6">
                    {/* Precio */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label className="text-base font-semibold">{t.sniper.multiInput.manualTab.labels.price}</Label>
                        <span className="text-2xl font-bold text-accent">
                          {precio[0].toLocaleString('es-ES')} €
                        </span>
                      </div>
                      <Slider
                        value={precio}
                        onValueChange={setPrecio}
                        min={50000}
                        max={1000000}
                        step={5000}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>50.000 €</span>
                        <span>1.000.000 €</span>
                      </div>
                    </div>

                    {/* Metros Cuadrados */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label className="text-base font-semibold">{t.sniper.multiInput.manualTab.labels.m2}</Label>
                        <span className="text-2xl font-bold text-accent">{m2[0]} m²</span>
                      </div>
                      <Slider
                        value={m2}
                        onValueChange={setM2}
                        min={30}
                        max={200}
                        step={5}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>30 m²</span>
                        <span>200 m²</span>
                      </div>
                    </div>

                    {/* Habitaciones */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label className="text-base font-semibold">{t.sniper.multiInput.manualTab.labels.rooms}</Label>
                        <span className="text-2xl font-bold text-accent">{habitaciones[0]}</span>
                      </div>
                      <Slider
                        value={habitaciones}
                        onValueChange={setHabitaciones}
                        min={1}
                        max={6}
                        step={1}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>1</span>
                        <span>6</span>
                      </div>
                    </div>

                    {/* Coste Reforma (Opcional) */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label className="text-base font-semibold">{t.sniper.multiInput.manualTab.labels.reform}</Label>
                        <span className="text-xl font-bold text-accent">
                          {costeReforma[0] > 0 ? costeReforma[0].toLocaleString('es-ES') + ' €' : t.sniper.multiInput.manualTab.auto}
                        </span>
                      </div>
                      <Slider
                        value={costeReforma}
                        onValueChange={setCosteReforma}
                        min={0}
                        max={50000}
                        step={1000}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{t.sniper.multiInput.manualTab.calculated}</span>
                        <span>50.000 €</span>
                      </div>
                    </div>

                    {/* Alquiler Mensual (Opcional) */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <Label className="text-base font-semibold">{t.sniper.multiInput.manualTab.labels.rent}</Label>
                        <span className="text-xl font-bold text-accent">
                          {alquilerMensual[0] > 0 ? alquilerMensual[0].toLocaleString('es-ES') + ' €' : t.sniper.multiInput.manualTab.auto}
                        </span>
                      </div>
                      <Slider
                        value={alquilerMensual}
                        onValueChange={setAlquilerMensual}
                        min={0}
                        max={2000}
                        step={50}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{t.sniper.multiInput.manualTab.estimated}</span>
                        <span>2.000 €</span>
                      </div>
                    </div>

                    {/* Campos adicionales */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                      <div className="space-y-2">
                        <Label>{t.sniper.multiInput.manualTab.labels.floor}</Label>
                        <Input
                          value={planta}
                          onChange={(e) => setPlanta(e.target.value)}
                          placeholder={t.sniper.multiInput.manualTab.placeholders.floor}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>{t.sniper.multiInput.manualTab.labels.status}</Label>
                        <select
                          value={estado}
                          onChange={(e) => setEstado(e.target.value)}
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                        >
                          <option value="bueno">{t.sniper.multiInput.manualTab.options.good}</option>
                          <option value="a reformar">{t.sniper.multiInput.manualTab.options.reform}</option>
                          <option value="excelente">{t.sniper.multiInput.manualTab.options.excellent}</option>
                          <option value="regular">{t.sniper.multiInput.manualTab.options.regular}</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <Label>{t.sniper.multiInput.manualTab.labels.location}</Label>
                        <Input
                          value={ubicacion}
                          onChange={(e) => setUbicacion(e.target.value)}
                          placeholder={t.sniper.multiInput.manualTab.placeholders.location}
                        />
                      </div>
                    </div>

                    <Button
                      type="submit"
                      disabled={isLoading}
                      className="w-full h-14 text-base font-semibold bg-accent hover:bg-emerald-light text-accent-foreground mt-6"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                          {t.sniper.multiInput.manualTab.analyzing}
                        </>
                      ) : (
                        t.sniper.multiInput.manualTab.analyze
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </section>
  );
};

export default MultiInput;


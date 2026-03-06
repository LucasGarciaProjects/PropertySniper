
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/context/LanguageContext";

export const LanguageToggle = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setLanguage(language === 'es' ? 'en' : 'es')}
      className="font-medium"
    >
      {language === 'es' ? 'EN' : 'ES'}
    </Button>
  );
};

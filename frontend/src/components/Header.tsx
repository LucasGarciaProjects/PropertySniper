import { Target } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import { LanguageToggle } from "./LanguageToggle";

const Header = () => {
  const { t } = useLanguage();
  return (
    <header className="w-full py-6 px-4 sm:px-6 lg:px-8 border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <Target className="w-6 h-6 text-primary-foreground" />
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            {t.header.title}
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <LanguageToggle />
          <div className="px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-xs sm:text-sm font-medium">
            {t.header.by} <span className="font-semibold">Álvaro Galán</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

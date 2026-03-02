import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface ResultCardProps {
  title: string;
  children: ReactNode;
  variant?: "default" | "gold";
  className?: string;
  delay?: number;
}

const ResultCard = ({ title, children, variant = "default", className, delay = 0 }: ResultCardProps) => {
  return (
    <div 
      className={cn(
        "card-elevated p-6 transition-all duration-300 opacity-0",
        variant === "gold" && "gradient-border-gold glow-gold",
        className
      )}
      style={{
        animation: `fadeInUp 0.6s ease-out ${delay}ms forwards`,
      }}
    >
      <h3 className={cn(
        "text-sm font-medium mb-4 uppercase tracking-wider",
        variant === "gold" ? "gradient-text-gold" : "text-muted-foreground"
      )}>
        {title}
      </h3>
      {children}
    </div>
  );
};

export default ResultCard;

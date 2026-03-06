interface GaugeChartProps {
  value: number;
  maxValue?: number;
  label: string;
}

const GaugeChart = ({ value, maxValue = 15, label }: GaugeChartProps) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  const strokeDasharray = 251.2; // Circumference for r=40 semicircle (π * 80)
  const strokeDashoffset = strokeDasharray - (strokeDasharray * percentage) / 100;
  
  // Color based on value
  const getColor = () => {
    if (value >= 8) return "hsl(160, 84%, 39%)"; // Emerald - Excellent
    if (value >= 5) return "hsl(45, 93%, 47%)"; // Gold - Good
    return "hsl(0, 84%, 60%)"; // Red - Poor
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-28">
        <svg
          viewBox="0 0 100 60"
          className="w-full h-full"
        >
          {/* Background arc */}
          <path
            d="M 10 55 A 40 40 0 0 1 90 55"
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 10 55 A 40 40 0 0 1 90 55"
            fill="none"
            stroke={getColor()}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray / 2}
            strokeDashoffset={(strokeDasharray / 2) - ((strokeDasharray / 2) * percentage) / 100}
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 8px ${getColor()})`,
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
          <span 
            className="text-3xl font-bold"
            style={{ color: getColor() }}
          >
            {value.toFixed(1)}%
          </span>
        </div>
      </div>
      <span className="text-sm text-muted-foreground mt-2">{label}</span>
    </div>
  );
};

export default GaugeChart;

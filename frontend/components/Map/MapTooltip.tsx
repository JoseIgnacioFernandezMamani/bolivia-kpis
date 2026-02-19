'use client';

export interface TooltipInfo {
  object: Record<string, unknown>;
  x: number;
  y: number;
}

interface Props {
  info: TooltipInfo;
}

export default function MapTooltip({ info }: Props) {
  const { object, x, y } = info;
  const props = (object as { properties?: Record<string, unknown> }).properties ?? object;

  return (
    <div
      className="pointer-events-none absolute z-20 max-w-xs rounded-lg bg-white/95 shadow-lg backdrop-blur-sm border border-gray-200 p-3 text-sm"
      style={{ left: x + 12, top: y + 12 }}
    >
      {Object.entries(props)
        .filter(([, v]) => v !== null && v !== undefined && v !== '')
        .slice(0, 8)
        .map(([key, value]) => (
          <div key={key} className="flex justify-between gap-4">
            <span className="font-medium capitalize text-gray-600">{key.replace(/_/g, ' ')}:</span>
            <span className="text-gray-900 text-right">{String(value)}</span>
          </div>
        ))}
    </div>
  );
}

interface KpiCardProps {
  label: string;
  value: string | number;
  color: string;
}

export default function KpiCard({ label, value, color }: KpiCardProps) {
  return (
    <div className={`rounded-2xl border p-5 ${color}`}>
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-800 mt-1 truncate">{value}</p>
    </div>
  );
}

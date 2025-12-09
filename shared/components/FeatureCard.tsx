// shared/components/FeatureCard.tsx
// shared/components/FeatureCard.tsx
import React from "react";

const FeatureCard: React.FC<{ title: string; subtitle?: string }> = ({ title, subtitle }) => {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm flex flex-col gap-2">
      <div className="font-semibold text-sky-600">{title}</div>
      <div className="text-sm text-slate-500">{subtitle}</div>
    </div>
  );
};
export default FeatureCard;

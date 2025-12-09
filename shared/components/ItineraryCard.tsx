// shared/components/ItineraryCard.tsx
import React from "react";
import SaveItineraryButton from "./SaveItineraryButton";

interface ItineraryCardProps {
  itinerary?: {
    _id: string;
    destination: string;
    travel_duration: number;
    budget: { amount: number; currency: string };
    travel_style: string;
    created_at: string;
    itinerary?: any;
  };
  title?: string;
  days?: string;
  price?: string;
  rating?: string;
  onRefresh?: () => Promise<void>;
}

const ItineraryCard: React.FC<ItineraryCardProps> = ({
  itinerary,
  title,
  days,
  price,
  rating,
  onRefresh,
}) => {
  // If itinerary prop is provided, use it to display itinerary data
  if (itinerary) {
    return (
      <div
        className="bg-white rounded-lg p-6 shadow-lg hover:shadow-xl transition cursor-pointer"
        onClick={() => {
          if (typeof window !== "undefined") {
            window.location.href = `/itinerary/${itinerary._id}`;
          }
        }}
      >
        <h3 className="text-lg font-bold text-gray-800 mb-2">
          {itinerary.destination}
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          {itinerary.travel_duration} days • {itinerary.travel_style}
        </p>
        <p className="text-sky-600 font-bold mb-4">
          ${itinerary.budget.amount} {itinerary.budget.currency}
        </p>
        <div className="flex gap-2 mt-4">
          <SaveItineraryButton
            payload={{
              destination: itinerary.destination,
              budget: itinerary.budget?.amount ?? 0,
              days: itinerary.travel_duration ?? 1,
              travel_style: itinerary.travel_style ?? "leisure",
              itinerary: itinerary.itinerary ?? {}
            }}
            onSaved={() => {
              // optional: show toast or refresh
            }}
          />
        </div>
        <div className="text-xs text-gray-500">
          Created: {new Date(itinerary.created_at).toLocaleDateString()}
        </div>
      </div>
    );
  }

  // Fallback to simple display card
  return (
    <div className="bg-white rounded-lg p-4 shadow-md flex gap-4">
      <div className="w-32 h-20 bg-slate-200 rounded-md overflow-hidden">
        <img
          src="/card-placeholder.jpg"
          alt={title}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="flex-1">
        <div className="font-semibold">{title}</div>
        <div className="text-sm text-slate-500 mt-1">
          {days} • {rating} ⭐
        </div>
        <div className="mt-2 text-sky-600 font-bold">{price}</div>
      </div>
      <div className="flex flex-col gap-2">
        <button className="px-3 py-1 rounded-md border">Book</button>
        <SaveItineraryButton
          payload={{
            destination: title || "Unknown",
            budget: 0,
            days: 1,
            travel_style: "leisure",
            itinerary: { summary: title }
          }}
        />
      </div>
    </div>
  );
};

export default ItineraryCard;

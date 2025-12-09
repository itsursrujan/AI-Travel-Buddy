import React, { useState } from "react";
import { api } from "../api/api";

interface Props {
  payload: any;
  onSaved?: (itinerary: any) => void;
}

const SaveItineraryButton: React.FC<Props> = ({ payload, onSaved }) => {
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async (e: React.MouseEvent) => {
    e.stopPropagation();
    // Ensure user is authenticated
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (!token) {
      // Redirect to login page
      window.location.href = "/auth/login";
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const resp = await api.post("/api/itinerary/save", payload);
      setSaved(true);
      onSaved?.(resp.data.itinerary);
    } catch (err: any) {
      setError(err?.response?.data?.error || err.message || "Save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-stretch">
      <button
        onClick={handleSave}
        className={`px-3 py-1 rounded-md ${saved ? "bg-green-600 text-white" : "bg-sky-500 text-white"}`}
        disabled={loading || saved}
      >
        {loading ? "Saving..." : saved ? "Saved" : "Save"}
      </button>
      {error && <div className="text-xs text-red-500 mt-1">{error}</div>}
    </div>
  );
};

export default SaveItineraryButton;

// shared/api/itinerary.ts
import { api } from "./api";

export interface ItineraryRequest {
  destination: string;
  budget: number;
  days: number;
  travel_style: "leisure" | "adventure" | "cultural" | "budget";
}

export interface Itinerary {
  _id: string;
  destination: string;
  budget: { amount: number; currency: string };
  travel_duration: number;
  travel_style: string;
  itinerary: any;
  created_at: string;
  updated_at: string;
  views: number;
  likes: number;
  status: string;
}

export async function generateItinerary(data: ItineraryRequest): Promise<{ itinerary: Itinerary }> {
  const response = await api.post("/api/itinerary/generate", data);
  return response.data;
}

export async function saveItinerary(data: {
  destination: string;
  budget: number;
  days: number;
  travel_style: string;
  itinerary: any;
  is_public?: boolean;
}): Promise<{ itinerary: Itinerary }> {
  const response = await api.post("/api/itinerary/save", data);
  return response.data;
}

export async function getUserItineraries(userId: string): Promise<{ itineraries: Itinerary[] }> {
  const response = await api.get(`/api/itinerary/user/${userId}`);
  return response.data;
}

export async function getItinerary(itineraryId: string): Promise<Itinerary> {
  const response = await api.get(`/api/itinerary/${itineraryId}`);
  return response.data;
}

export async function deleteItinerary(itineraryId: string): Promise<{ message: string }> {
  const response = await api.delete(`/api/itinerary/${itineraryId}`);
  return response.data;
}


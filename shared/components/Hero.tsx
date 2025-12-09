// shared/components/Hero.tsx
// shared/components/Hero.tsx
import React from "react";

const Hero: React.FC = () => {
  return (
    <section className="w-full pt-16 pb-12 bg-linear-to-b from-sky-50 to-white">
      <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-2 gap-8 items-center">
        <div>
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight text-slate-900">
            it’s a big world out there, go <span className="text-sky-500">explore.</span>
          </h1>
          <p className="mt-6 text-slate-600 max-w-xl">
            discover new attractions and experiences matched to your interests and travel style — personalized
            day-wise itineraries, offline mobile access, and budget-aware suggestions.
          </p>

          <form className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input placeholder="Destination (city/country)" className="p-3 rounded-md border" />
            <input placeholder="Budget (USD)" className="p-3 rounded-md border" />
            <input placeholder="Start date" className="p-3 rounded-md border" />
            <select className="p-3 rounded-md border">
              <option>Travel Style: Leisure</option>
              <option>Adventure</option>
              <option>Family</option>
            </select>
            <button className="col-span-1 sm:col-span-2 mt-2 bg-sky-500 text-white px-6 py-3 rounded-md">
              Book now
            </button>
          </form>

        </div>

        <div className="relative">
          <div className="rounded-2xl overflow-hidden shadow-xl bg-white">
            <img src="/hero-travel.jpg" alt="travel" className="w-full h-72 object-cover" />
            <div className="p-4">
              <div className="flex gap-3 items-center">
                <div className="flex-1">
                  <div className="font-semibold">Top Choices • Quality Guidance • Easy Bookings</div>
                  <div className="text-sm text-slate-500">Total 600+ destinations • Our tour guides 20+ years</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-slate-400">Best in class</div>
                  <div className="text-sky-500 font-bold">Ticket booking system</div>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute -bottom-6 right-6 w-40 rounded-lg bg-white p-3 shadow-lg">
            <div className="font-semibold text-slate-800">Featured</div>
            <div className="text-sm text-slate-500">Mount Bromo • 3D2N</div>
          </div>
        </div>
      </div>
    </section>
  );
};
export default Hero;

// shared/components/Header.tsx
// shared/components/Header.tsx
import React from "react";

const Header: React.FC<{ onLogin?: ()=>void }> = ({ onLogin }) => {
  return (
    <header className="w-full flex items-center justify-between py-4 px-6 bg-white/60 backdrop-blur-sm sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-lg bg-linear-to-br from-sky-400 to-teal-400 flex items-center justify-center text-white font-bold">
          AT
        </div>
        <div className="font-semibold text-lg">AI Travel Buddy</div>
      </div>
      <nav className="hidden md:flex gap-6 items-center text-sm">
        <a className="hover:underline" href="#">Home</a>
        <a className="hover:underline" href="#">Planner</a>
        <a className="hover:underline" href="#">Saved</a>
        <a className="hover:underline" href="#">Analytics</a>
        <a className="hover:underline" href="#">Blog</a>
      </nav>
      <div className="flex items-center gap-3">
        <button
          onClick={onLogin}
          className="px-4 py-2 rounded-md bg-sky-500 text-white hover:bg-sky-600"
        >
          Sign in
        </button>
      </div>
    </header>
  );
};
export default Header;

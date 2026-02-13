"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Process } from "@/components/landing/Process";
import { LivePreview } from "@/components/landing/LivePreview";
import { MultiFarm } from "@/components/landing/MultiFarm";
import { Footer } from "@/components/landing/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
      <Navbar />
      <Hero />
      <Process />
      <LivePreview />
      <MultiFarm />
      <Footer />
    </main>
  );
}

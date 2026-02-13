"use client";

import { Navbar } from "@/components/landing/Navbar";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Footer } from "@/components/landing/Footer";

export default function HowItWorksPage() {
    return (
        <main className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />
            <HowItWorks />
            <Footer />
        </main>
    );
}

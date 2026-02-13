"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Features } from "@/components/landing/Features";
import { Footer } from "@/components/landing/Footer";

export default function FeaturesPage() {
    return (
        <main className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />
            <Features />
            <Footer />
        </main>
    );
}

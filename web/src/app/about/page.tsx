"use client";

import { Navbar } from "@/components/landing/Navbar";
import { About } from "@/components/landing/About";
import { Footer } from "@/components/landing/Footer";

export default function AboutPage() {
    return (
        <main className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />
            <About />
            <Footer />
        </main>
    );
}

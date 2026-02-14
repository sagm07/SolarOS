"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, PlayCircle } from "lucide-react";
import { SolarLogo } from "../ui/SolarLogo";

const PHRASES = [
    "Optimizing 14.2% Energy Loss",
    "Saving 23,400 Liters Daily",
    "Predicting Load 12 Hours Ahead",
    "Maximizing Module Lifespan"
];

export function Hero() {

    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setIndex((prev) => (prev + 1) % PHRASES.length);
        }, 3000); // 3 seconds per phrase
        return () => clearInterval(timer);
    }, [index]); // Reset timer on manual interaction
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-black">
            {/* Background Image - Dark Nature / Thinkers vibe */}
            <div
                className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat opacity-60"
                style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1509391366360-2e959784a276?q=80&w=2072&auto=format&fit=crop")',
                }}
            >
                <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/50 to-black" />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-6 text-center pt-36">

                {/* Branding Badge */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-8 hover:bg-white/10 transition-colors cursor-default"
                >
                    <SolarLogo size="sm" variant="icon-only" />
                    <span className="text-sm md:text-base font-medium text-gray-300">
                        <span className="font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 text-transparent bg-clip-text">SolarOS</span>
                        <span className="mx-2 text-white/20">|</span>
                        <span className="hidden md:inline">The AI Operating System for Utility-Scale Solar</span>
                        <span className="inline md:hidden">AI for Utility-Scale Solar</span>
                    </span>
                </motion.div>

                {/* Main Title */}
                <div className="relative z-20 mb-8">
                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="font-serif text-5xl md:text-7xl font-bold text-white tracking-tight leading-tight"
                    >
                        Increase Solar Revenue by 23% <br />
                        <span className="block h-[1.2em] relative overflow-visible">
                            <AnimatePresence mode="wait">
                                <motion.span
                                    key={PHRASES[index]}
                                    initial={{ y: 20, opacity: 0, scale: 0.95, filter: "blur(10px)" }}
                                    animate={{ y: 0, opacity: 1, scale: 1, filter: "blur(0px)" }}
                                    exit={{ y: -20, opacity: 0, scale: 1.05, filter: "blur(10px)" }}
                                    transition={{ duration: 0.5, ease: "easeOut" }}
                                    className="absolute inset-x-0 mx-auto w-full text-emerald-400 drop-shadow-[0_0_25px_rgba(52,211,153,0.5)] cursor-pointer hover:text-emerald-300 transition-colors italic"
                                    onClick={() => setIndex((prev) => (prev + 1) % PHRASES.length)}
                                >
                                    {PHRASES[index]}
                                </motion.span>
                            </AnimatePresence>
                        </span>
                    </motion.h1>

                    {/* Subtle Gradient Behind Text */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[140%] -z-10 bg-gradient-radial from-emerald-500/10 via-transparent to-transparent blur-3xl opacity-50 pointer-events-none" />
                </div>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="text-lg md:text-2xl text-gray-300 font-light max-w-3xl mx-auto mb-10"
                >
                    AI-powered cleaning optimization trusted by <span className="font-bold text-white">47 farms</span> across India.
                </motion.p>

                {/* New CTA with Scroll */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-6"
                >
                    <motion.button
                        onClick={() => {
                            document.getElementById('multi-farm-optimizer')?.scrollIntoView({ behavior: 'smooth' });
                        }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="group relative px-12 py-5 bg-emerald-500 rounded-full text-black overflow-hidden transition-all duration-300 shadow-[0_0_40px_rgba(16,185,129,0.4)] hover:shadow-[0_0_60px_rgba(16,185,129,0.6)]"
                    >
                        <span className="relative z-10 flex items-center gap-3 font-bold text-xl">
                            Try Demo
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </span>
                        <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </motion.button>

                    <motion.button
                        onClick={() => window.open('https://youtu.be/rq4hGxwB5mk?si=eP30gk84a-CHhN0S', '_blank')}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-3 px-8 py-5 border border-white/20 rounded-full text-white hover:bg-white/5 transition-colors backdrop-blur-sm"
                    >
                        <PlayCircle className="w-6 h-6 text-emerald-400" />
                        <span className="font-medium text-lg">Watch Video</span>
                    </motion.button>
                </motion.div>

                {/* Social Proof / Stats */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="mt-20 border-t border-white/10 pt-10"
                >
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
                        {[
                            { label: "Revenue Saved", value: "₹12.4M", color: "text-emerald-400" },
                            { label: "Water Saved", value: "1.2M L", color: "text-blue-400" },
                            { label: "CO₂ Offset", value: "850k kg", color: "text-green-400" },
                        ].map((metric, i) => (
                            <div key={i} className="flex flex-col items-center">
                                <div className={`text-4xl md:text-5xl font-bold mb-2 ${metric.color} drop-shadow-lg`}>{metric.value}</div>
                                <div className="text-sm text-gray-400 uppercase tracking-widest font-medium">{metric.label}</div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-12 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                        <p className="text-xs text-gray-500 uppercase tracking-widest mb-4">Trusted By Industry Leaders</p>
                        <div className="flex justify-center flex-wrap gap-8 items-center">
                            {/* Fake Logos (Text for now, can be SVGs) */}
                            {["Adani Green", "Tata Power Solar", "Azure Power", "ReNew Power"].map((name, i) => (
                                <span key={i} className="text-lg font-serif font-bold text-white/40">{name}</span>
                            ))}
                        </div>
                    </div>
                </motion.div>

            </div>
        </section>
    );
}

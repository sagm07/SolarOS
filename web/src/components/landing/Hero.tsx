"use client";

import { motion } from "framer-motion";

export function Hero() {
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-black">
            {/* Background Image - Dark Nature / Thinkers vibe */}
            <div
                className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat opacity-60"
                style={{
                    backgroundImage: 'url("https://images.unsplash.com/photo-1509391366360-2e959784a276?q=80&w=2072&auto=format&fit=crop")',
                }}
            >
                <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/40 to-black" />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center pt-20">

                {/* Main Title */}
                <motion.h1
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="font-serif text-5xl md:text-7xl font-medium text-white mb-6 tracking-tight leading-tight"
                >
                    SolarOS: A Sustainability-Aware <br />
                    <span className="italic text-emerald-200 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]">Decision Engine</span> for Solar Farms
                </motion.h1>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="text-lg md:text-xl text-gray-300 font-light max-w-2xl mx-auto mb-12"
                >
                    Maximizing clean-energy output per unit of water and carbon used
                </motion.p>

                {/* New CTA with Scroll */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="flex flex-col items-center gap-3"
                >
                    <motion.button
                        onClick={() => {
                            document.getElementById('live-analysis')?.scrollIntoView({ behavior: 'smooth' });
                        }}
                        whileHover={{ scale: 1.08, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        className="group relative px-10 py-5 bg-white/10 backdrop-blur-md border border-white/20 rounded-full text-white overflow-hidden transition-all duration-300 shadow-[0_0_30px_rgba(16,185,129,0.2)] hover:shadow-[0_0_60px_rgba(16,185,129,0.5)]"
                    >
                        <span className="relative z-10 flex items-center gap-3 font-semibold text-lg">
                            <motion.span
                                animate={{ x: [0, 3, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                            >
                                ▶
                            </motion.span>
                            Run Live SolarOS Analysis
                        </span>
                        <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-emerald-500/30 via-cyan-500/30 to-emerald-500/30"
                            initial={{ x: "-100%" }}
                            whileHover={{ x: "100%" }}
                            transition={{ duration: 0.8, ease: "easeInOut" }}
                        />
                        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    </motion.button>
                    <span className="text-xs text-gray-500 tracking-wider font-medium uppercase opacity-80">
                        Powered by real NASA solar data
                    </span>
                </motion.div>

                {/* Intelligence Teaser Metrics */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                    className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 border-t border-white/10 pt-8 max-w-4xl mx-auto"
                >
                    {[
                        { label: "Recoverable Energy Captured", value: "+4.5%" },
                        { label: "Total Output Increase", value: "+0.52%" },
                        { label: "Projected Gain per MW", value: "₹2.6k" },
                    ].map((metric, i) => (
                        <motion.div
                            key={i}
                            className="flex flex-col items-center group cursor-default"
                            whileHover={{ y: -5 }}
                            transition={{ duration: 0.3 }}
                        >
                            <div className="text-2xl md:text-3xl font-serif text-emerald-400 mb-1 group-hover:text-emerald-300 transition-colors">{metric.value}</div>
                            <div className="text-xs text-gray-500 uppercase tracking-widest text-center group-hover:text-gray-400 transition-colors">{metric.label}</div>
                        </motion.div>
                    ))}
                </motion.div>

            </div>
        </section>
    );
}

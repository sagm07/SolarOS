"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { RainIntelligence } from "@/components/dashboard/RainIntelligence";
import { MultiFarmOptimizer } from "@/components/dashboard/MultiFarmOptimizer";
import { motion } from "framer-motion";
import { Brain, BarChart3, CloudRain } from "lucide-react";

export default function DashboardPage() {
    return (
        <main className="min-h-screen bg-black text-white relative overflow-hidden font-sans">
            <Navbar />

            {/* Hero Section */}
            <section className="pt-32 pb-20 px-6">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center mb-16"
                    >
                        <div className="inline-flex items-center gap-2 text-emerald-400 text-sm font-bold tracking-wider uppercase mb-6">
                            <Brain className="w-4 h-4" />
                            ML Intelligence Dashboard
                        </div>
                        <h1 className="font-serif text-5xl md:text-6xl mb-6">
                            Complete SolarOS Intelligence Suite
                        </h1>
                        <p className="text-gray-400 text-lg max-w-3xl mx-auto">
                            Explore all ML capabilities: Rain forecasting, multi-farm optimization,
                            scenario comparison, and degradation analytics.
                        </p>
                    </motion.div>

                    {/* Dashboard Grid */}
                    <div className="grid lg:grid-cols-2 gap-8">
                        {/* Rain Intelligence Card */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8"
                        >
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                                    <CloudRain className="w-6 h-6 text-cyan-400" />
                                </div>
                                <div>
                                    <h2 className="font-serif text-2xl text-white">Rain Intelligence</h2>
                                    <p className="text-sm text-gray-400">Natural cleaning forecast</p>
                                </div>
                            </div>
                            <RainIntelligence />
                        </motion.div>

                        {/* Multi-Farm Optimizer Card */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8"
                        >
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                                    <BarChart3 className="w-6 h-6 text-emerald-400" />
                                </div>
                                <div>
                                    <h2 className="font-serif text-2xl text-white">Multi-Farm Portfolio</h2>
                                    <p className="text-sm text-gray-400">Optimize across sites</p>
                                </div>
                            </div>
                            <MultiFarmOptimizer />
                        </motion.div>
                    </div>
                </div>
            </section>

            <Footer />
        </main>
    );
}

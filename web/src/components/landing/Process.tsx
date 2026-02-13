"use client";

import { motion } from "framer-motion";
import { Copy, TrendingDown, Scale } from "lucide-react";

const thinkingSteps = [
    {
        icon: Copy, // Digital Twin
        title: "Digital Twin",
        description: "Models real irradiance, temperature & dust physics.",
    },
    {
        icon: TrendingDown, // Degradation
        title: "Degradation Forecast",
        description: "Predicts energy leakage before it happens.",
    },
    {
        icon: Scale, // Optimizer
        title: "Sustainability Optimizer",
        description: "Balances money, carbon, and water.",
    },
];

export function Process() {
    return (
        <section className="py-24 bg-black relative z-10 border-t border-white/5">
            <div className="max-w-7xl mx-auto px-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-16"
                >
                    <h2 className="font-serif text-3xl md:text-4xl text-white mb-4">How SolarOS Thinks</h2>
                    <p className="text-gray-400">From physics to portfolio optimization.</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {thinkingSteps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className="relative group p-8 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md hover:bg-white/10 transition-all hover:-translate-y-1"
                        >
                            <div className="w-14 h-14 rounded-full bg-emerald-900/20 flex items-center justify-center mb-6 border border-emerald-500/20 text-emerald-400 group-hover:scale-110 transition-transform">
                                <step.icon className="w-7 h-7" />
                            </div>
                            <h3 className="font-serif text-2xl text-white mb-3">{step.title}</h3>
                            <p className="text-gray-400 leading-relaxed font-light">{step.description}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

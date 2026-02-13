"use client";

import { motion } from "framer-motion";

const metrics = [
    {
        value: "18,240",
        unit: "kWh",
        label: "Energy Recovered",
        sub: "this month",
        progress: 75,
    },
    {
        value: "13,200",
        unit: "kg",
        label: "CO₂ Offset",
        sub: "and growing",
        progress: 60,
    },
    {
        value: "1,200",
        unit: "L",
        label: "Water Preserved",
        sub: "daily average",
        progress: 85,
    },
];

export function Metrics() {
    return (
        <section className="py-32 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-emerald-900/10 to-transparent pointer-events-none" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <motion.h2
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    className="text-center text-sm font-bold uppercase tracking-widest text-emerald-500 mb-16"
                >
                    Measurable Impact
                </motion.h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
                    {metrics.map((metric, index) => (
                        <motion.div
                            key={index}
                            initial={{ scale: 0.9, opacity: 0 }}
                            whileInView={{ scale: 1, opacity: 1 }}
                            transition={{ type: "spring", stiffness: 100, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className="flex flex-col items-center"
                        >
                            <div className="text-6xl lg:text-7xl font-bold text-gradient mb-2">
                                {metric.value}
                            </div>
                            <div className="text-xl text-white font-medium mb-1">
                                {metric.label}
                            </div>
                            <div className="text-sm text-gray-400 mb-6 font-mono">
                                {metric.sub}
                            </div>

                            {/* Progress Bar */}
                            <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden max-w-[200px]">
                                <motion.div
                                    initial={{ width: 0 }}
                                    whileInView={{ width: `${metric.progress}%` }}
                                    transition={{ duration: 1.5, ease: "easeOut" }}
                                    className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                                />
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

"use client";

import { motion } from "framer-motion";
import { TrendingUp, Droplets, Zap } from "lucide-react";

const valueProps = [
    {
        icon: TrendingUp,
        title: "Increase Revenue 15-25%",
        description: "Precisely timing cleaning cycles to maximize energy recovery when prices are high.",
        color: "text-emerald-400",
        border: "border-emerald-500/20",
        bg: "bg-emerald-900/10"
    },
    {
        icon: Droplets,
        title: "Reduce Water Usage 40%",
        description: "Skip cleaning when rain is forecast or dust impact is negligible.",
        color: "text-blue-400",
        border: "border-blue-500/20",
        bg: "bg-blue-900/10"
    },
    {
        icon: Zap,
        title: "Automate Scheduling",
        description: "Eliminate manual spreadsheets with AI-driven, portfolio-wide cleaning schedules.",
        color: "text-yellow-400",
        border: "border-yellow-500/20",
        bg: "bg-yellow-900/10"
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
                    <h2 className="font-serif text-3xl md:text-5xl text-white mb-4">Why SolarOS?</h2>
                    <p className="text-xl text-gray-400">Physics-based intelligence for your portfolio.</p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {valueProps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className={`relative group p-8 rounded-2xl border ${step.border} ${step.bg} backdrop-blur-md hover:bg-white/5 transition-all hover:-translate-y-2`}
                        >
                            <div className={`w-14 h-14 rounded-full ${step.bg} flex items-center justify-center mb-6 border ${step.border} ${step.color} group-hover:scale-110 transition-transform`}>
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

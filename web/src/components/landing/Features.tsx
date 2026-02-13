"use client";

import { motion } from "framer-motion";
import { Database, Brain, Target, Zap, BarChart3, Building2 } from "lucide-react";

const features = [
    {
        icon: Database,
        title: "Physics-Aware Solar Digital Twin",
        subtitle: "Real-world irradiance. Real degradation. Real decisions.",
        description:
            "SolarOS builds a dynamic digital twin of your solar installation using real satellite irradiance data and thermodynamic modeling.",
        capabilities: [
            "Solar irradiance curves",
            "Panel temperature coupling",
            "Non-linear dust accumulation",
            "Aging degradation",
        ],
        impact:
            "This enables accurate estimation of energy leakage before it becomes visible.",
    },
    {
        icon: Brain,
        title: "Energy Leakage Detection Engine",
        subtitle: "Autonomous degradation intelligence",
        description:
            "SolarOS continuously estimates degradation metrics to quantify opportunity cost rather than detect faults.",
        capabilities: [
            "Effective panel efficiency",
            "Dust saturation percentage",
            "Thermal loss impact",
            "Recoverable energy opportunity",
        ],
        impact:
            "This reframes maintenance from reactive repair to proactive optimization.",
    },
    {
        icon: Target,
        title: "Multi-Objective Sustainability Optimization",
        subtitle: "Balance economics with environmental impact",
        description:
            "SolarOS balances multiple dimensions to align decisions with corporate ESG targets.",
        capabilities: [
            "Financial gain (₹ recovery)",
            "Carbon offset (kg CO₂)",
            "Water cost (liters used)",
            "Cleaning operational cost",
        ],
        impact:
            "Transforms maintenance into a sustainability strategy tool with configurable priority weights.",
    },
    {
        icon: Zap,
        title: "Future Impact Simulation",
        subtitle: "Predictive cleaning scenario modeling",
        description:
            "SolarOS simulates multiple cleaning scenarios to select the optimal window.",
        capabilities: [
            "No cleaning baseline",
            "Clean today analysis",
            "Clean in X days projection",
            "Multi-scenario comparison",
        ],
        impact:
            "Ensures cleaning decisions are economically and environmentally justified.",
    },
    {
        icon: BarChart3,
        title: "Real-Time Sustainability Dashboard",
        subtitle: "Designed for decision-makers, not just engineers",
        description:
            "Clear, actionable insights without technical complexity.",
        capabilities: [
            "Autonomous recommendation (CLEAN / WAIT)",
            "Projected energy recovery",
            "Carbon offset impact",
            "Net sustainability score",
        ],
        impact:
            "Provides transparency and traceability for every decision.",
    },
    {
        icon: Building2,
        title: "Enterprise Readiness",
        subtitle: "Built for scale and compliance",
        description:
            "Designed for multi-site operations and regulatory alignment.",
        capabilities: [
            "Multi-farm prioritization",
            "API integration support",
            "ESG reporting export",
            "Carbon disclosure alignment",
        ],
        impact:
            "Production-ready architecture for deployment across solar portfolios.",
    },
];

export function Features() {
    return (
        <section id="features" className="py-32 bg-gradient-to-b from-black to-zinc-900 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px]" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-20"
                >
                    <div className="inline-flex items-center gap-2 text-emerald-400 text-sm font-bold tracking-wider uppercase mb-6">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        Modular Intelligence Stack
                    </div>
                    <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">
                        Technical Depth Meets Clarity
                    </h2>
                    <p className="text-gray-400 text-lg max-w-3xl mx-auto">
                        SolarOS combines physics-based modeling with sustainability optimization
                        to transform solar maintenance from reactive to strategic.
                    </p>
                </motion.div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-2 gap-8 items-stretch">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.4, delay: index * 0.1 }}
                            whileHover={{ y: -4 }}
                            className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-10 hover:border-emerald-500/40 transition-all duration-300"
                        >
                            {/* Gradient glow on hover */}
                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500/5 to-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                            {/* Subtle section gradient */}
                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-transparent via-white/5 to-transparent opacity-50" />

                            <div className="relative z-10">
                                {/* Icon with intentional glow */}
                                <div className="mb-8 inline-flex p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 group-hover:scale-110 transition-transform duration-300 shadow-[0_0_30px_rgba(16,185,129,0.15)]">
                                    <feature.icon className="w-6 h-6 text-emerald-400" />
                                </div>

                                {/* Title - improved hierarchy */}
                                <h3 className="font-serif text-2xl font-semibold tracking-tight text-white mb-3">
                                    {feature.title}
                                </h3>

                                {/* Subtitle - refined usage */}
                                <p className="text-sm uppercase tracking-wider text-emerald-400 mb-6 font-medium">
                                    {feature.subtitle}
                                </p>

                                {/* Description - better spacing */}
                                <p className="text-base text-gray-400 leading-relaxed mb-8">
                                    {feature.description}
                                </p>

                                {/* Capabilities - improved bullets */}
                                <div className="space-y-3 mb-8">
                                    {feature.capabilities.map((cap, i) => (
                                        <div key={i} className="flex items-start gap-3 text-base text-gray-400">
                                            <div className="w-2 h-2 rounded-full bg-emerald-400 mt-2 flex-shrink-0" />
                                            <span>{cap}</span>
                                        </div>
                                    ))}
                                </div>

                                {/* Impact - premium statement */}
                                <div className="pt-6 border-t border-white/10">
                                    <p className="text-sm italic text-gray-400 leading-relaxed">
                                        {feature.impact}
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}

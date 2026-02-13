"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const commitments = [
    {
        title: "Real environmental data",
        description: "NASA POWER API integration for precise irradiance, temperature, and precipitation forecasting",
    },
    {
        title: "Physics-based modeling",
        description: "Digital twin simulation grounded in thermodynamic principles and empirical degradation curves",
    },
    {
        title: "Transparent sustainability metrics",
        description: "Multi-objective optimization balancing financial returns, carbon offset, and water conservation",
    },
    {
        title: "Scalable architecture",
        description: "Cloud-native infrastructure designed for portfolio-level optimization across distributed assets",
    },
];

export function About() {
    return (
        <section id="about" className="relative py-32 bg-black overflow-hidden">
            {/* Subtle gradient background */}
            <div className="absolute inset-0 bg-gradient-to-b from-black via-emerald-950/5 to-black" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-16"
                >
                    <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">
                        Our Commitment
                    </h2>
                    <p className="text-gray-400 text-lg mb-12">
                        SolarOS is built on:
                    </p>

                    {/* Commitment grid */}
                    <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-12">
                        {commitments.map((item, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="bg-white/[0.02] backdrop-blur-sm border border-emerald-500/20 rounded-xl p-6 hover:bg-white/[0.04] hover:border-emerald-500/40 transition-all duration-300"
                            >
                                <h3 className="text-emerald-400 text-lg font-semibold mb-2">
                                    {item.title}
                                </h3>
                                <p className="text-gray-400 text-sm leading-relaxed">
                                    {item.description}
                                </p>
                            </motion.div>
                        ))}
                    </div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                        className="text-gray-300 italic text-base max-w-3xl mx-auto"
                    >
                        We are committed to advancing intelligent climate infrastructure.
                    </motion.p>
                </motion.div>

                {/* Image gallery */}
                <div className="grid md:grid-cols-3 gap-6 mt-20">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="relative h-80 rounded-2xl overflow-hidden group"
                    >
                        <Image
                            src="https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80"
                            alt="Solar panel farm at sunset"
                            fill
                            className="object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="relative h-80 rounded-2xl overflow-hidden group"
                    >
                        <Image
                            src="https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?w=800&q=80"
                            alt="Aerial view of solar farm"
                            fill
                            className="object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="relative h-80 rounded-2xl overflow-hidden group"
                    >
                        <Image
                            src="https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&q=80"
                            alt="Solar panels against blue sky"
                            fill
                            className="object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    </motion.div>
                </div>

                {/* Mission statement */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="mt-20 text-center max-w-4xl mx-auto"
                >
                    <div className="bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 rounded-2xl p-12">
                        <h3 className="font-serif text-3xl text-white mb-6">
                            Advancing Intelligent Climate Infrastructure
                        </h3>
                        <p className="text-gray-300 text-lg leading-relaxed mb-6">
                            We believe that the transition to renewable energy requires more than just hardware—it demands intelligent software that maximizes every kilowatt-hour while minimizing environmental impact.
                        </p>
                        <p className="text-gray-400 leading-relaxed">
                            SolarOS combines real-time satellite data, physics-based simulation, and multi-objective optimization to help solar operators make smarter decisions about maintenance, cleaning, and resource allocation. Our mission is to make clean energy not just cleaner, but smarter.
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

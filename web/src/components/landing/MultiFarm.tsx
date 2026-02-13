"use client";

import { motion } from "framer-motion";
import Image from "next/image";

export function MultiFarm() {
    return (
        <section className="py-24 bg-black border-t border-white/5 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-emerald-900/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center relative z-10">

                {/* Left Content */}
                <div className="text-left">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="font-serif text-4xl md:text-5xl text-white mb-6"
                    >
                        Optimized Across Portfolios, Not Panels
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-gray-400 mb-10 leading-relaxed"
                    >
                        Allocates limited water and budget across distributed solar farms to maximize total clean energy gain.
                    </motion.p>
                </div>

                {/* Right Image - Product Card Vibe */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    className="relative rounded-3xl overflow-hidden h-[400px] border border-white/10 group"
                >
                    <Image
                        src="https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80"
                        alt="SolarOS Product"
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-700"
                    />
                    <div className="absolute inset-0 bg-black/60 md:bg-black/40 flex flex-col justify-end p-8">
                        <div className="bg-white/10 backdrop-blur-md p-6 rounded-2xl border border-white/20">
                            <h3 className="text-white text-xl font-bold mb-2">SolarOS EdgeTech Module</h3>
                            <p className="text-gray-300 text-sm">Industrial-grade durability with top-tier performance.</p>
                        </div>
                    </div>
                </motion.div>

            </div>
        </section>
    );
}

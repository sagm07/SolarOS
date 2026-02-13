"use client";

import { motion, useInView } from "framer-motion";
import { Brain, Database, TrendingUp, Target, CheckCircle2, DollarSign, Leaf, Droplets } from "lucide-react";
import { useRef, useState, useEffect } from "react";

const steps = [
    {
        number: "01",
        title: "Data Ingestion",
        description: "Real-time satellite irradiance and weather data from NASA POWER API",
        icon: Database,
        color: "emerald",
        metrics: ["Hourly granularity", "Multi-location support", "30-day forecasts"],
    },
    {
        number: "02",
        title: "Digital Twin Modeling",
        description: "Physics-based simulation of panel degradation and efficiency loss",
        icon: Brain,
        color: "cyan",
        metrics: ["Temperature effects", "Dust accumulation", "Performance curves"],
    },
    {
        number: "03",
        title: "Energy Quantification",
        description: "Precise calculation of recoverable energy from cleaning intervention",
        icon: TrendingUp,
        color: "yellow",
        metrics: ["kWh recovery potential", "ROI analysis", "Degradation impact"],
    },
    {
        number: "04",
        title: "Multi-Objective Optimization",
        description: "Balance financial returns, carbon offset, and water sustainability",
        icon: Target,
        color: "blue",
        metrics: ["Profit maximization", "Carbon reduction", "Water efficiency"],
    },
    {
        number: "05",
        title: "Autonomous Decision",
        description: "AI-powered recommendation with confidence scoring and timing",
        icon: CheckCircle2,
        color: "emerald",
        metrics: ["95% accuracy", "Rain intelligence", "Cost-benefit analysis"],
    },
];

// Energy particle flowing down the pipeline
function EnergyParticle({ delay }: { delay: number }) {
    return (
        <motion.div
            className="absolute left-0 w-1 h-1 bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)]"
            initial={{ top: "-20px", opacity: 0 }}
            animate={{
                top: "calc(100% + 20px)",
                opacity: [0, 1, 1, 0],
            }}
            transition={{
                duration: 8,
                delay,
                repeat: Infinity,
                ease: "linear",
            }}
        />
    );
}

// Mini waveform for Step 01
function MiniWaveform() {
    const pathRef = useRef<SVGPathElement>(null);

    useEffect(() => {
        if (!pathRef.current) return;
        const animate = () => {
            if (pathRef.current) {
                const currentOffset = parseFloat(pathRef.current.style.strokeDashoffset || "0");
                pathRef.current.style.strokeDashoffset = `${currentOffset - 1}`;
            }
            requestAnimationFrame(animate);
        };
        animate();
    }, []);

    return (
        <svg className="w-full h-20" viewBox="0 0 200 40">
            <path
                ref={pathRef}
                d="M 0 20 Q 25 10, 50 20 T 100 20 T 150 20 T 200 20"
                fill="none"
                stroke="url(#waveGradient)"
                strokeWidth="2"
                style={{ strokeDasharray: "200", strokeDashoffset: "0" }}
            />
            <defs>
                <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                    <stop offset="50%" stopColor="#10b981" stopOpacity="1" />
                    <stop offset="100%" stopColor="#10b981" stopOpacity="0.3" />
                </linearGradient>
            </defs>
        </svg>
    );
}

// Heatmap visual for Step 02
function MiniHeatmap() {
    return (
        <div className="relative w-full h-24 rounded-lg overflow-hidden bg-gradient-to-b from-orange-500/20 via-yellow-500/10 to-transparent border border-orange-500/20">
            {/* Dust particles */}
            {[...Array(4)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-gray-400 rounded-full"
                    style={{ left: `${20 + i * 20}%`, bottom: "10%" }}
                    animate={{ y: [-10, -40], opacity: [0, 1, 0] }}
                    transition={{ duration: 3, repeat: Infinity, delay: i * 0.7 }}
                />
            ))}
            {/* Temperature */}
            <motion.div
                className="absolute top-2 right-2 px-2 py-1 bg-orange-500/30 border border-orange-500/40 rounded text-xs text-orange-400 font-mono"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity }}
            >
                28.5°C
            </motion.div>
        </div>
    );
}

// Energy bars for Step 03
function EnergyBars() {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true });

    return (
        <div ref={ref} className="space-y-3">
            <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Clean</span>
                    <span className="text-emerald-400">100 kWh</span>
                </div>
                <div className="h-8 bg-black/40 rounded-lg overflow-hidden border border-white/10">
                    <motion.div
                        className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                        initial={{ scaleX: 0 }}
                        animate={isInView ? { scaleX: 1 } : {}}
                        transition={{ duration: 1, delay: 0.2 }}
                        style={{ transformOrigin: "left" }}
                    />
                </div>
            </div>
            <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Degraded</span>
                    <span className="text-orange-400">75 kWh</span>
                </div>
                <div className="h-8 bg-black/40 rounded-lg overflow-hidden border border-white/10">
                    <motion.div
                        className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                        initial={{ scaleX: 0 }}
                        animate={isInView ? { scaleX: 0.75 } : {}}
                        transition={{ duration: 1, delay: 0.4 }}
                        style={{ transformOrigin: "left" }}
                    />
                </div>
            </div>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ delay: 0.7 }}
                className="flex items-center justify-center gap-2 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/30"
            >
                <TrendingUp className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-yellow-400 font-semibold">25 kWh Recoverable</span>
            </motion.div>
        </div>
    );
}

// Circular gauge component
function CircularGauge({ value, icon: Icon, color, delay }: { value: number; icon: any; color: string; delay: number }) {
    const [progress, setProgress] = useState(0);
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true });

    useEffect(() => {
        if (isInView) {
            setTimeout(() => setProgress(value), delay);
        }
    }, [isInView, value, delay]);

    const circumference = 2 * Math.PI * 20;
    const offset = circumference - (progress / 100) * circumference;

    return (
        <div ref={ref} className="flex flex-col items-center">
            <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="20" stroke="rgba(255,255,255,0.1)" strokeWidth="4" fill="none" />
                <circle
                    cx="32"
                    cy="32"
                    r="20"
                    stroke={color}
                    strokeWidth="4"
                    fill="none"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="transition-all duration-1000"
                    strokeLinecap="round"
                />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
                <Icon className="w-4 h-4" style={{ color }} />
            </div>
            <span className="mt-1 text-xs text-gray-500">{Math.round(progress)}%</span>
        </div>
    );
}

// Mini gauges for Step 04
function MiniGauges() {
    return (
        <div className="flex justify-around items-center py-4">
            <CircularGauge value={85} icon={DollarSign} color="#10b981" delay={200} />
            <CircularGauge value={92} icon={Leaf} color="#06b6d4" delay={400} />
            <CircularGauge value={78} icon={Droplets} color="#3b82f6" delay={600} />
        </div>
    );
}

// Decision badge for Step 05
function DecisionBadge() {
    const [confidence, setConfidence] = useState(0);
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true });

    useEffect(() => {
        if (!isInView) return;
        let start = 0;
        const timer = setInterval(() => {
            start += 2;
            if (start >= 94) {
                setConfidence(94);
                clearInterval(timer);
            } else {
                setConfidence(start);
            }
        }, 20);
        return () => clearInterval(timer);
    }, [isInView]);

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center py-6"
        >
            <div className="inline-block px-8 py-4 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border-2 border-emerald-500/40 shadow-[0_0_40px_rgba(16,185,129,0.3)]">
                <p className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                    CLEAN
                </p>
                <p className="text-sm text-gray-400">Confidence: <span className="text-emerald-400 font-semibold">{confidence}%</span></p>
            </div>
        </motion.div>
    );
}

export function HowItWorks() {
    return (
        <section id="how-it-works" className="relative py-32 bg-black overflow-hidden">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-5" style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, rgba(16,185,129,0.5) 1px, transparent 1px)`,
                backgroundSize: "40px 40px",
            }} />

            {/* Subtle radial glow */}
            <div className="absolute inset-0 bg-gradient-to-b from-black via-emerald-950/5 to-black" />

            <div className="max-w-6xl mx-auto px-6 relative z-10">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-20"
                >
                    <div className="inline-flex items-center gap-2 text-emerald-400 text-xs font-bold tracking-widest uppercase mb-6 px-4 py-2 rounded-full border border-emerald-500/20 bg-emerald-500/5">
                        Intelligence Pipeline
                    </div>
                    <h2 className="font-serif text-5xl md:text-6xl text-white mb-4">
                        How It Works
                    </h2>
                    <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                        Five-stage ML pipeline from data to decision
                    </p>
                </motion.div>

                {/* Pipeline with energy stream */}
                <div className="relative">
                    {/* Animated vertical energy line */}
                    <div className="absolute left-6 top-0 bottom-0 w-[2px] bg-gradient-to-b from-emerald-400/50 via-emerald-400/30 to-transparent" />

                    {/* Energy particles */}
                    <EnergyParticle delay={0} />
                    <EnergyParticle delay={2.7} />
                    <EnergyParticle delay={5.3} />

                    {/* Steps */}
                    <div className="space-y-6">
                        {steps.map((step, index) => {
                            const Icon = step.icon;

                            return (
                                <motion.div
                                    key={step.number}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true, margin: "-100px" }}
                                    transition={{ duration: 0.6, delay: index * 0.1 }}
                                >
                                    <div className="group relative bg-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8 hover:bg-white/[0.04] hover:-translate-y-1 transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10">
                                        {/* Radial glow layer */}
                                        <div className="absolute inset-0 bg-gradient-radial from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl" />

                                        {/* Step number badge */}
                                        <div className="absolute -left-3 top-8 w-12 h-12 rounded-xl bg-gradient-to-br from-black to-gray-900 border border-emerald-500/30 flex items-center justify-center font-mono text-sm font-bold text-emerald-400 shadow-lg shadow-emerald-500/20">
                                            {step.number}
                                        </div>

                                        <div className="grid md:grid-cols-[1fr,300px] gap-8 pl-6">
                                            {/* Left: Content */}
                                            <div>
                                                <div className="flex items-start gap-4 mb-4">
                                                    <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                                        <Icon className="w-6 h-6 text-emerald-400" />
                                                    </div>
                                                    <div>
                                                        <h3 className="text-2xl font-semibold text-white mb-2 group-hover:text-emerald-50 transition-colors">
                                                            {step.title}
                                                        </h3>
                                                        <p className="text-gray-400 text-sm leading-relaxed">
                                                            {step.description}
                                                        </p>
                                                    </div>
                                                </div>

                                                <div className="flex flex-wrap gap-2 pl-16">
                                                    {step.metrics.map((metric, i) => (
                                                        <span
                                                            key={i}
                                                            className="px-3 py-1.5 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-xs text-emerald-400 font-medium"
                                                        >
                                                            {metric}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>

                                            {/* Right: Mini visualization */}
                                            <div className="flex items-center">
                                                {index === 0 && <MiniWaveform />}
                                                {index === 1 && <MiniHeatmap />}
                                                {index === 2 && <EnergyBars />}
                                                {index === 3 && <MiniGauges />}
                                                {index === 4 && <DecisionBadge />}
                                            </div>
                                        </div>

                                        {/* Connector to next step */}
                                        {index < steps.length - 1 && (
                                            <motion.div
                                                className="absolute left-6 top-full w-[2px] h-6 bg-gradient-to-b from-emerald-400/30 to-transparent"
                                                initial={{ scaleY: 0 }}
                                                whileInView={{ scaleY: 1 }}
                                                viewport={{ once: true }}
                                                transition={{ duration: 0.4, delay: index * 0.1 + 0.3 }}
                                                style={{ transformOrigin: "top" }}
                                            />
                                        )}
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>

                {/* Bottom CTA */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="mt-16 text-center"
                >
                    <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20">
                        <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        <p className="text-gray-300 text-sm">
                            End-to-end pipeline executes in <span className="text-emerald-400 font-semibold">under 2 seconds</span>
                        </p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}

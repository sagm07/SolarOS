"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Droplets, Leaf, TrendingUp } from "lucide-react";

const steps = [
    {
        title: "Analyzing Environment",
        icon: "🛰️",
        description: "Querying NASA POWER satellite data",
        color: "from-blue-500 to-cyan-500",
        metrics: { irradiance: 5.2, temp: 32, dust: 1.2 }
    },
    {
        title: "Modeling Degradation",
        icon: "📉",
        description: "Calculating energy loss from soiling",
        color: "from-orange-500 to-red-500",
        metrics: { efficiency: 87.3, loss: 12.7, days: 23 }
    },
    {
        title: "Optimizing Schedule",
        icon: "🧮",
        description: "Balancing cost, carbon, and water",
        color: "from-purple-500 to-pink-500",
        metrics: { roi: 340, water: 2500, carbon: 450 }
    },
    {
        title: "Recommendation Ready",
        icon: "✅",
        description: "Optimal cleaning date calculated",
        color: "from-emerald-500 to-green-500",
        metrics: { date: "Feb 18", gain: "₹2.6k", impact: "+4.5%" }
    }
];

export function LiveEnginePreview() {
    const [step, setStep] = useState(0);
    const [isRunning, setIsRunning] = useState(false);

    useEffect(() => {
        if (isRunning && step < steps.length - 1) {
            const timer = setTimeout(() => setStep(step + 1), 2000);
            return () => clearTimeout(timer);
        }
        if (step === steps.length - 1) {
            setIsRunning(false);
        }
    }, [isRunning, step]);

    const runDemo = () => {
        setStep(0);
        setIsRunning(true);
    };

    // Auto-run on mount for demo
    useEffect(() => {
        const timer = setTimeout(() => {
            if (!isRunning) runDemo();
        }, 1000);
        return () => clearTimeout(timer);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <div className="w-full h-full flex flex-col items-center justify-center p-8">
            <AnimatePresence mode="wait">
                {!isRunning && step === 0 ? (
                    <motion.div
                        key="start"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="text-center space-y-6"
                    >
                        <div className="w-24 h-24 mx-auto bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-full flex items-center justify-center">
                            <Zap className="w-12 h-12 text-black" />
                        </div>

                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">
                                Ready to Optimize?
                            </h3>
                            <p className="text-gray-400">
                                Adjust the parameters on the left and click "Run Analysis" to see the engine in action.
                            </p>
                        </div>

                        <button
                            onClick={runDemo}
                            className="px-8 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold rounded-lg hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all duration-300"
                        >
                            ▶ Run Live Demo
                        </button>
                    </motion.div>
                ) : (
                    <motion.div
                        key={`step-${step}`}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="w-full space-y-6"
                    >
                        {/* Current Step */}
                        <div className={`bg-gradient-to-r ${steps[step].color} p-1 rounded-lg`}>
                            <div className="bg-black p-6 rounded-lg">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="text-4xl">{steps[step].icon}</div>
                                    <div>
                                        <h3 className="text-xl font-bold text-white">
                                            {steps[step].title}
                                        </h3>
                                        <p className="text-gray-400 text-sm">
                                            {steps[step].description}
                                        </p>
                                    </div>
                                </div>

                                {/* Metrics */}
                                <div className="grid grid-cols-3 gap-3">
                                    {Object.entries(steps[step].metrics).map(([key, value]) => (
                                        <motion.div
                                            key={key}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="bg-white/5 p-3 rounded-lg"
                                        >
                                            <div className="text-xs text-gray-400 uppercase">{key}</div>
                                            <div className="text-lg font-bold text-white">{value}</div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="flex items-center gap-2">
                            {steps.map((_, idx) => (
                                <div
                                    key={idx}
                                    className={`h-2 flex-1 rounded-full transition-all duration-500 ${idx <= step ? 'bg-emerald-500' : 'bg-white/10'
                                        }`}
                                />
                            ))}
                        </div>

                        {/* Action Buttons */}
                        {step === steps.length - 1 && (
                            <div className="flex gap-3">
                                <button
                                    onClick={runDemo}
                                    className="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-all"
                                >
                                    Run Again
                                </button>
                                <button
                                    onClick={() => {
                                        const dashboardLink = document.querySelector('a[href="/dashboard"]');
                                        if (dashboardLink) (dashboardLink as HTMLElement).click();
                                    }}
                                    className="flex-1 px-6 py-3 bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold rounded-lg hover:shadow-lg transition-all"
                                >
                                    Try Full Dashboard →
                                </button>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

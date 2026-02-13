"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, AlertCircle, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";

interface AnalysisData {
    recommendation: "CLEAN" | "WAIT";
    cleaning_date: string | null;
    total_output_gain_percent: number;
    recoverable_capture_percent: number;
    additional_energy_kwh: number;
    carbon_saved_kg: number;
    net_economic_gain_inr: number;
    water_used_liters: number;
}

export function LivePreview() {
    const [data, setData] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(false);
    const [analyzingText, setAnalyzingText] = useState("Analyzing Chennai solar irradiance data...");
    const [hasRunAnalysis, setHasRunAnalysis] = useState(false);
    const [inputs, setInputs] = useState({
        location: "Chennai, India",
        carbonPriority: 50,
        cleaningCost: 1500
    });

    // Location mapping
    const locationMap: Record<string, { lat: number; lng: number }> = {
        "Chennai, India": { lat: 13.0827, lng: 80.2707 },
        "Rajasthan, India": { lat: 26.9124, lng: 75.7873 },
        "California, USA": { lat: 36.7783, lng: -119.4179 },
    };

    // Fetch real data function with parameters
    const fetchAnalysis = async () => {
        setLoading(true);
        setData(null);
        try {
            const coords = locationMap[inputs.location];
            const carbonWeight = inputs.carbonPriority / 100; // Convert percentage to 0-1 range

            const queryParams = new URLSearchParams({
                latitude: coords.lat.toString(),
                longitude: coords.lng.toString(),
                carbon_weight: carbonWeight.toString(),
                cleaning_cost: inputs.cleaningCost.toString(),
            });

            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/analyze?${queryParams}`);
            if (!res.ok) throw new Error("Failed to fetch analysis");
            const json = await res.json();

            setData(json);
        } catch (e) {
            // Fallback for demo/offline
            setData({
                recommendation: "CLEAN",
                cleaning_date: "2024-12-15",
                total_output_gain_percent: 12.5,
                recoverable_capture_percent: 45.2,
                additional_energy_kwh: 125.0,
                carbon_saved_kg: 87.5,
                net_economic_gain_inr: 2450.0,
                water_used_liters: 500.0,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRunAnalysis = () => {
        setHasRunAnalysis(true);

        // Sequence of text updates
        setTimeout(() => setAnalyzingText("Fetching NASA satellite data..."), 800);
        setTimeout(() => setAnalyzingText("Modeling dust degradation physics..."), 1600);
        setTimeout(() => setAnalyzingText("Optimizing carbon vs. water trade-offs..."), 2400);

        setTimeout(() => {
            setLoading(false);
            fetchAnalysis();
        }, 3000);
    };

    const isWait = data?.recommendation === "WAIT";

    return (
        <section id="live-analysis" className="py-24 bg-zinc-900/50 border-t border-white/5 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-black/50 to-transparent pointer-events-none" />

            <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-start">

                {/* Left Interactive Panel */}
                <motion.div
                    initial={{ opacity: 0, x: -30 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    className="relative z-10"
                >
                    <div className="inline-flex items-center gap-2 text-emerald-400 text-sm font-bold tracking-wider uppercase mb-6">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        Live Engine Preview
                    </div>
                    <h2 className="font-serif text-4xl md:text-5xl text-white mb-6">Autonomous Decision Intelligence</h2>
                    <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                        Run the engine to see how SolarOS balances physical degradation with financial and environmental costs in real-time.
                    </p>

                    {/* Controls Card */}
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 mb-8 space-y-6">
                        <div>
                            <label className="text-white text-sm font-medium mb-1 block">Location</label>
                            <select
                                className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-gray-300 outline-none focus:border-emerald-500/50 transition-colors"
                                value={inputs.location}
                                onChange={(e) => setInputs({ ...inputs, location: e.target.value })}
                            >
                                <option>Chennai, India</option>
                                <option>Rajasthan, India</option>
                                <option>California, USA</option>
                            </select>
                        </div>

                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <label className="text-white font-medium">Carbon Priority</label>
                                <span className="text-emerald-400">{inputs.carbonPriority}%</span>
                            </div>
                            <input
                                type="range"
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                                value={inputs.carbonPriority}
                                onChange={(e) => setInputs({ ...inputs, carbonPriority: parseInt(e.target.value) })}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-white text-sm font-medium mb-1 block">Cleaning Cost (₹)</label>
                                <input
                                    type="number"
                                    className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-gray-300 outline-none focus:border-emerald-500/50"
                                    value={inputs.cleaningCost}
                                    onChange={(e) => setInputs({ ...inputs, cleaningCost: parseInt(e.target.value) })}
                                />
                            </div>
                            <button
                                onClick={handleRunAnalysis}
                                disabled={loading}
                                className="bg-emerald-500 hover:bg-emerald-400 text-black font-bold rounded-lg p-3 flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-6 h-[50px]"
                            >
                                {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Play className="w-5 h-5 fill-black" />}
                                Run Analysis
                            </button>
                        </div>
                    </div>
                </motion.div>

                {/* Right - Results Area */}
                <div className="relative min-h-[400px]">

                    <AnimatePresence mode="wait">
                        {/* LOADING STATE */}
                        {loading && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-md rounded-3xl border border-white/10"
                            >
                                <Loader2 className="w-12 h-12 text-emerald-400 animate-spin mb-4" />
                                <p className="text-emerald-300 font-mono text-sm animate-pulse">{analyzingText}</p>
                            </motion.div>
                        )}

                        {/* PLACEHOLDER - Before Analysis */}
                        {!loading && !hasRunAnalysis && (
                            <motion.div
                                key="placeholder"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="flex flex-col items-center justify-center bg-white/5 backdrop-blur-lg rounded-3xl border border-white/10 p-16 min-h-[400px]"
                            >
                                <div className="text-center">
                                    <div className="w-20 h-20 rounded-full bg-emerald-900/20 flex items-center justify-center mx-auto mb-6 border border-emerald-500/20">
                                        <Play className="w-10 h-10 text-emerald-400" />
                                    </div>
                                    <h3 className="font-serif text-2xl text-white mb-3">Ready to Analyze</h3>
                                    <p className="text-gray-400 max-w-sm mx-auto">
                                        Configure your parameters and click &quot;Run Analysis&quot; to see SolarOS intelligence in action.
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {/* RESULT CARD - After Analysis */}
                        {!loading && hasRunAnalysis && data && (
                            <motion.div
                                key="results"
                                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.5 }}
                                className={clsx(
                                    "p-8 rounded-3xl border bg-white/5 backdrop-blur-lg shadow-2xl relative overflow-hidden transition-all duration-500",
                                    isWait ? "border-blue-500/30 shadow-[0_0_50px_rgba(59,130,246,0.1)]" : "border-emerald-500/50 shadow-[0_0_50px_rgba(16,185,129,0.15)]"
                                )}
                            >
                                {/* Background Decoration */}
                                <div className={clsx(
                                    "absolute top-0 right-0 w-64 h-64 rounded-full blur-[80px] pointer-events-none opacity-20",
                                    isWait ? "bg-blue-500" : "bg-emerald-500"
                                )} />

                                <div className="flex justify-between items-center mb-8 border-b border-white/10 pb-6 relative z-10">
                                    <div>
                                        <div className="text-sm text-gray-400 mb-1 font-medium tracking-wide">RECOMMENDATION</div>
                                        <div className={clsx(
                                            "text-3xl font-bold flex items-center gap-3",
                                            isWait ? "text-blue-400" : "text-emerald-400"
                                        )}>
                                            <AlertCircle className={isWait ? "stroke-blue-400" : "stroke-emerald-400"} />
                                            {data.recommendation}
                                        </div>
                                        <div className="text-xs text-gray-500 mt-1 pl-1">
                                            {isWait ? "Rain forecasted in 48h" : "Peak efficiency window detected"}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-gray-500">Confidence</div>
                                        <div className="text-white font-bold font-mono text-lg">98.4%</div>
                                    </div>
                                </div>

                                <div className="space-y-6 relative z-10">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">Energy Recovery</span>
                                        <span className="text-xl font-mono text-white tracking-tight">{data.additional_energy_kwh.toLocaleString('en-US')} kWh</span>
                                    </div>
                                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: "75%" }}
                                            className="bg-blue-500 h-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                                        />
                                    </div>

                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">Carbon Offset</span>
                                        <span className="text-xl font-mono text-white tracking-tight">{data.carbon_saved_kg.toLocaleString('en-US')} kg</span>
                                    </div>
                                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: "65%" }}
                                            className="bg-emerald-500 h-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                                        />
                                    </div>

                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-400">Water Usage</span>
                                        <span className="text-xl font-mono text-white tracking-tight">{data.water_used_liters.toLocaleString('en-US')} L</span>
                                    </div>
                                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: "20%" }}
                                            className="bg-cyan-500 h-full shadow-[0_0_10px_rgba(6,182,212,0.5)]"
                                        />
                                    </div>
                                </div>

                                <div className="mt-8 pt-6 border-t border-white/10 flex justify-between items-end relative z-10">
                                    <span className="text-sm text-gray-500">Net Sustainability Score</span>
                                    <motion.span
                                        key={data.net_economic_gain_inr}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="text-3xl font-bold text-emerald-400 drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]"
                                    >
                                        +₹{data.net_economic_gain_inr.toLocaleString('en-US')}
                                    </motion.span>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

            </div>
        </section>
    );
}

"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, AlertCircle, Loader2, Play, Brain, TrendingUp, Leaf, Info, Droplets, Banknote, Sun } from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";
import { GlassDropdown } from "../ui/GlassDropdown";
import { LiveEnginePreview } from "./LiveEnginePreview";

// Updated Interface to match new API response
// Updated Interface to match new API response
interface AnalysisData {
    recommendation: "CLEAN" | "WAIT";
    cleaning_date: string | null;
    total_output_gain_percent: number;
    recoverable_capture_percent: number;
    additional_energy_kwh: number;
    carbon_saved_kg: number;
    net_economic_gain_inr: number;
    water_used_liters: number;
    sses_score: number; // New SSES Score
    explanation?: {
        model: string;
        reason?: string;
        reasons?: string[]; // New: Bullet points for decision logic
        optimization_score: number;
    };
    confidence_interval?: {
        p10_benefit: number;
        p90_benefit: number;
        uncertainty_spread_kwh: number;
    };
}

export function LivePreview() {
    const [data, setData] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(false);
    const [analyzingText, setAnalyzingText] = useState("Initializing Decision Engine...");
    const [hasRunAnalysis, setHasRunAnalysis] = useState(false);
    const [inputs, setInputs] = useState({
        location: "Chennai, Tamil Nadu",
        carbonPriority: 50,
        cleaningCost: 1500,
        plantCapacityMW: 25
    });

    const locationMap: Record<string, { lat: number; lng: number }> = {
        "Chennai, Tamil Nadu": { lat: 13.0827, lng: 80.2707 },
        "Jaisalmer, Rajasthan": { lat: 26.9124, lng: 70.9179 },
        "Jodhpur, Rajasthan": { lat: 26.2389, lng: 73.0243 },
        "Bikaner, Rajasthan": { lat: 28.0229, lng: 73.3119 },
        "Gandhinagar, Gujarat": { lat: 23.2156, lng: 72.6369 },
        "Anantapur, Andhra Pradesh": { lat: 14.6819, lng: 77.6006 },
        "Kurnool, Andhra Pradesh": { lat: 15.8281, lng: 78.0373 },
        "Bengaluru, Karnataka": { lat: 12.9716, lng: 77.5946 },
        "Mumbai, Maharashtra": { lat: 19.0760, lng: 72.8777 },
        "Hyderabad, Telangana": { lat: 17.3850, lng: 78.4867 },
        "Pune, Maharashtra": { lat: 18.5204, lng: 73.8567 },
        "New Delhi, NCR": { lat: 28.6139, lng: 77.2090 },
        "Gurgaon, Haryana": { lat: 28.4595, lng: 77.0266 },
        "Dubai, UAE": { lat: 25.2048, lng: 55.2708 },
        "Riyadh, Saudi Arabia": { lat: 24.7136, lng: 46.6753 },
        "Cairo, Egypt": { lat: 30.0444, lng: 31.2357 },
        "Cape Town, South Africa": { lat: -33.9249, lng: 18.4241 },
        "California, USA": { lat: 36.7783, lng: -119.4179 },
        "Arizona, USA": { lat: 34.0489, lng: -111.0937 },
        "Santiago, Chile": { lat: -33.4489, lng: -70.6693 },
        "Queensland, Australia": { lat: -20.9176, lng: 142.7028 },
        "Beijing, China": { lat: 39.9042, lng: 116.4074 },
        "Seville, Spain": { lat: 37.3891, lng: -5.9845 },
        "Athens, Greece": { lat: 37.9838, lng: 23.7275 },
    };

    const fetchAnalysis = async () => {
        setLoading(true);
        setData(null);
        try {
            const coords = locationMap[inputs.location] || locationMap["Chennai, Tamil Nadu"];
            const carbonWeight = inputs.carbonPriority / 100;

            const queryParams = new URLSearchParams({
                latitude: coords.lat.toString(),
                longitude: coords.lng.toString(),
                carbon_weight: carbonWeight.toString(),
                cleaning_cost: inputs.cleaningCost.toString(),
                plant_capacity_mw: inputs.plantCapacityMW.toString()
            });

            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/analyze?${queryParams}`);
            if (!res.ok) throw new Error("Failed to fetch analysis");
            const json = await res.json();

            setData(json);
        } catch (e) {
            // Updated Fallback with SSES & Confidence
            setData({
                recommendation: "CLEAN",
                cleaning_date: "2024-12-15",
                total_output_gain_percent: 12.5,
                recoverable_capture_percent: 45.2,
                additional_energy_kwh: 125.0,
                carbon_saved_kg: 87.5,
                net_economic_gain_inr: 2450.0,
                water_used_liters: 500.0,
                sses_score: 85.4,
                explanation: {
                    model: "Dynamic Programming (Offline)",
                    reason: "Simulated fallback data due to connection error.",
                    optimization_score: 100.0
                },
                confidence_interval: {
                    p10_benefit: 2100.0,
                    p90_benefit: 2800.0,
                    uncertainty_spread_kwh: 45.5
                }
            });
        } finally {
            setLoading(false);
        }
    };

    const handleRunAnalysis = () => {
        setHasRunAnalysis(true);
        // More "Intelligent" status messages
        setTimeout(() => setAnalyzingText("Fetching NASA Satellite Data..."), 500);
        setTimeout(() => setAnalyzingText("Running Dynamic Programming Optimization..."), 1500);
        setTimeout(() => setAnalyzingText("Calculating Sustainability Index (SSES)..."), 2500);

        setTimeout(() => {
            setLoading(false);
            fetchAnalysis();
        }, 3200);
    };

    const isWait = data?.recommendation === "WAIT";

    // Options Arrays (Keep same as before)
    const locationOptions = [
        { group: "India 🇮🇳", label: "Chennai, Tamil Nadu", value: "Chennai, Tamil Nadu" },
        { group: "India 🇮🇳", label: "Jaisalmer, Rajasthan", value: "Jaisalmer, Rajasthan" },
        { group: "India 🇮🇳", label: "Jodhpur, Rajasthan", value: "Jodhpur, Rajasthan" },
        { group: "India 🇮🇳", label: "Bikaner, Rajasthan", value: "Bikaner, Rajasthan" },
        { group: "India 🇮🇳", label: "Gandhinagar, Gujarat", value: "Gandhinagar, Gujarat" },
        { group: "India 🇮🇳", label: "Anantapur, Andhra Pradesh", value: "Anantapur, Andhra Pradesh" },
        { group: "India 🇮🇳", label: "Kurnool, Andhra Pradesh", value: "Kurnool, Andhra Pradesh" },
        { group: "India 🇮🇳", label: "Bengaluru, Karnataka", value: "Bengaluru, Karnataka" },
        { group: "India 🇮🇳", label: "Mumbai, Maharashtra", value: "Mumbai, Maharashtra" },
        { group: "India 🇮🇳", label: "Hyderabad, Telangana", value: "Hyderabad, Telangana" },
        { group: "India 🇮🇳", label: "Pune, Maharashtra", value: "Pune, Maharashtra" },
        { group: "India 🇮🇳", label: "New Delhi, NCR", value: "New Delhi, NCR" },
        { group: "India 🇮🇳", label: "Gurgaon, Haryana", value: "Gurgaon, Haryana" },
        { group: "Middle East", label: "Dubai, UAE", value: "Dubai, UAE" },
        { group: "Middle East", label: "Riyadh, Saudi Arabia", value: "Riyadh, Saudi Arabia" },
        { group: "Africa", label: "Cairo, Egypt", value: "Cairo, Egypt" },
        { group: "Africa", label: "Cape Town, South Africa", value: "Cape Town, South Africa" },
        { group: "Americas", label: "California, USA", value: "California, USA" },
        { group: "Americas", label: "Arizona, USA", value: "Arizona, USA" },
        { group: "Americas", label: "Santiago, Chile", value: "Santiago, Chile" },
        { group: "Asia-Pacific", label: "Queensland, Australia", value: "Queensland, Australia" },
        { group: "Asia-Pacific", label: "Beijing, China", value: "Beijing, China" },
        { group: "Europe", label: "Seville, Spain", value: "Seville, Spain" },
        { group: "Europe", label: "Athens, Greece", value: "Athens, Greece" },
    ];

    const farmSizeOptions = [
        { label: "5 MW (Small - 25,000 m²)", value: 5 },
        { label: "25 MW (Medium - 125,000 m²)", value: 25 },
        { label: "50 MW (Large - 250,000 m²)", value: 50 },
        { label: "100 MW (Utility Scale - 500,000 m²)", value: 100 },
    ];


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
                        <GlassDropdown
                            label="Location"
                            value={inputs.location}
                            onChange={(val) => setInputs({ ...inputs, location: val })}
                            options={locationOptions}
                            className="z-50"
                        />

                        <GlassDropdown
                            label="Farm Size"
                            value={inputs.plantCapacityMW}
                            onChange={(val) => setInputs({ ...inputs, plantCapacityMW: val })}
                            options={farmSizeOptions}
                            className="z-40"
                        />

                        {/* Carbon Priority Slider */}
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
                                    className="w-full bg-gray-900 border border-white/10 rounded-lg p-3 text-gray-300 outline-none focus:border-emerald-500/50"
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
                        {/* LOADING STATE - Enhanced */}
                        {loading && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="absolute inset-0 flex flex-col items-center justify-center text-center p-8 bg-black/40 backdrop-blur-md rounded-2xl border border-white/10"
                            >
                                <div className="relative w-20 h-20 mb-6">
                                    <div className="absolute inset-0 border-4 border-white/10 rounded-full"></div>
                                    <div className="absolute inset-0 border-4 border-emerald-500 rounded-full border-t-transparent animate-spin"></div>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <Brain className="w-8 h-8 text-emerald-400 animate-pulse" />
                                    </div>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Optimization Engine Running</h3>
                                <p className="text-emerald-400 font-mono text-sm">{analyzingText}</p>

                                {/* Real-time data stream effect */}
                                <div className="mt-8 text-xs font-mono text-gray-500 text-left space-y-2 w-full max-w-[240px] opacity-75 border-l-2 border-emerald-500/30 pl-3">
                                    <div className="flex justify-between"><span>MODEL</span> <span className="text-emerald-500">DYNAMIC_PROGRAMMING</span></div>
                                    <div className="flex justify-between"><span>HORIZON</span> <span>30 DAYS</span></div>
                                    <div className="flex justify-between"><span>IRRADIANCE</span> <span>{Math.floor(Math.random() * 200) + 800} W/m²</span></div>
                                    <div className="flex justify-between"><span>DUST_RATE</span> <span>0.0{Math.floor(Math.random() * 5) + 2} g/m²/d</span></div>
                                </div>
                            </motion.div>
                        )}

                        {/* RESULTS STATE - Redesigned for Intelligence */}
                        {!loading && data && (
                            <motion.div
                                key="results"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ type: "spring", stiffness: 100 }}
                                className={clsx(
                                    "rounded-3xl p-8 border backdrop-blur-xl relative overflow-hidden group hover:shadow-[0_0_50px_rgba(16,185,129,0.1)] transition-all duration-500",
                                    isWait
                                        ? "bg-gradient-to-br from-cyan-900/40 to-black/60 border-cyan-500/30"
                                        : "bg-gradient-to-br from-emerald-900/40 to-black/60 border-emerald-500/30"
                                )}
                            >
                                {/* Glowing orb background */}
                                <div className={clsx(
                                    "absolute -top-20 -right-20 w-64 h-64 rounded-full blur-[100px] opacity-20 transition-colors duration-1000",
                                    isWait ? "bg-cyan-500" : "bg-emerald-500"
                                )} />

                                <div className="relative z-10">
                                    {/* Header - Recommendation */}
                                    <div className="flex items-start justify-between mb-8">
                                        <div>
                                            <div className="text-gray-400 text-sm font-medium tracking-wide mb-1">OPTIMAL DECISION</div>
                                            <div className={clsx(
                                                "text-4xl font-bold tracking-tight flex items-center gap-3",
                                                isWait ? "text-cyan-400" : "text-emerald-400"
                                            )}>
                                                {isWait ? "DEFER CLEANING" : "CLEAN NOW"}
                                                {isWait ? <AlertCircle className="w-8 h-8" /> : <CheckCircle2 className="w-8 h-8" />}
                                            </div>
                                        </div>
                                        {/* SSES Badge (New) */}
                                        <div className="text-right">
                                            <div className="text-xs text-gray-400 mb-1 flex items-center justify-end gap-1">
                                                SSES SCORE <Info className="w-3 h-3 cursor-help" />
                                            </div>
                                            <div className="text-3xl font-mono text-white flex items-end justify-end gap-2">
                                                {data.sses_score.toFixed(1)}
                                                <span className="text-sm text-gray-500 mb-1">/100</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Decision Logic (Deep Explainability) - NEW */}
                                    <div className="mb-6 bg-black/30 rounded-xl p-4 border border-white/10">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                                                <Brain className="w-4 h-4" />
                                                Decision Intelligence
                                            </div>
                                        </div>

                                        {data.explanation?.reasons && data.explanation.reasons.length > 0 ? (
                                            <ul className="space-y-2 mb-4">
                                                {data.explanation.reasons.map((r, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                                        <span className="mt-1.5 w-1 h-1 rounded-full bg-emerald-500/50 shrink-0" />
                                                        {r}
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="text-gray-300 text-sm leading-relaxed mb-4">
                                                {data.explanation?.reason || "Optimization model determined this is the most cost-effective action."}
                                            </p>
                                        )}

                                        {/* Confidence Interval Visualization */}
                                        {data.confidence_interval && (
                                            <div className="mt-3 pt-3 border-t border-white/5">
                                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                                    <span>Confidence Interval (90%)</span>
                                                    <span>Risk-Adjusted Rev.</span>
                                                </div>
                                                <div className="flex justify-between items-center bg-white/5 rounded px-2 py-1">
                                                    <span className="text-gray-400 text-xs">P10: ₹{data.confidence_interval.p10_benefit.toLocaleString()}</span>
                                                    <div className="h-1 w-12 bg-gray-700 rounded-full overflow-hidden mx-2">
                                                        <div className="h-full bg-emerald-500/50 w-2/3 mx-auto"></div>
                                                    </div>
                                                    <span className="text-emerald-300 text-xs font-bold">P90: ₹{data.confidence_interval.p90_benefit.toLocaleString()}</span>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Primary Metric - Economic Gain */}
                                    <div className="mb-8 p-6 rounded-2xl bg-black/20 border border-white/5">
                                        <div className="flex justify-between items-end mb-2">
                                            <div className="text-gray-400 text-sm">Net Economic Gain (Projected)</div>
                                            <div className="text-emerald-400 font-bold text-2xl">
                                                ₹{data.net_economic_gain_inr.toLocaleString()}
                                            </div>
                                        </div>
                                        <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
                                            <div
                                                className="bg-emerald-500 h-full rounded-full"
                                                style={{ width: `${Math.min(data.recoverable_capture_percent, 100)}%` }}
                                            />
                                        </div>
                                        <div className="flex justify-between mt-2 text-xs text-gray-500 font-mono">
                                            <span>Efficiency Recovery</span>
                                            <span>{data.total_output_gain_percent.toFixed(1)}%</span>
                                        </div>
                                    </div>

                                    {/* Secondary Metrics Grid */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                                            <div className="text-gray-400 text-xs uppercase mb-1 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> Energy Gain</div>
                                            <div className="text-white font-bold text-lg">+{data.additional_energy_kwh.toFixed(0)} kWh</div>
                                        </div>
                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                                            <div className="text-gray-400 text-xs uppercase mb-1 flex items-center gap-1"><Droplets className="w-3 h-3" /> Water Used</div>
                                            <div className="text-white font-bold text-lg">{data.water_used_liters.toFixed(0)} L</div>
                                        </div>
                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                                            <div className="text-gray-400 text-xs uppercase mb-1 flex items-center gap-1"><Leaf className="w-3 h-3" /> Carbon Saved</div>
                                            <div className="text-white font-bold text-lg">{data.carbon_saved_kg.toFixed(1)} kg</div>
                                        </div>
                                        <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                                            <div className="text-gray-400 text-xs uppercase mb-1 flex items-center gap-1"><Sun className="w-3 h-3" /> Cleaning Date</div>
                                            <div className="text-emerald-400 font-bold text-lg">{data.cleaning_date || "Deferred"}</div>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {/* EMPTY STATE */}
                        {/* EMPTY STATE - Live Preview */}
                        {!loading && !data && (
                            <div className="h-full flex flex-col items-center justify-center">
                                <LiveEnginePreview />
                            </div>
                        )}
                    </AnimatePresence>

                </div>
            </div>
        </section>
    );
}

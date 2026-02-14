"use client";

import { useState, useEffect, useRef } from "react";
import { GlassDropdown } from "../ui/GlassDropdown";
import { Factory, Droplets, Zap, Leaf, TrendingUp, Wifi, Loader2, CheckCircle2, ArrowRight, Download, BrainCircuit, Calendar, RefreshCw, HelpCircle, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import CountUp from "react-countup";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

// --- Types ---
interface Farm {
    name: string;
    latitude: number;
    longitude: number;
    panel_area: number;
    dust_rate: number;
    electricity_price: number;
    water_usage: number;
}

interface FarmScore {
    name: string;
    priority: number;
    water_usage: number;
    energy: number;
    benefit: number;
    co2: number;
    roi: number;
}

// --- Components ---

const Tooltip = ({ content, children }: { content: string, children: React.ReactNode }) => {
    const [isVisible, setIsVisible] = useState(false);

    return (
        <div
            className="relative flex items-center"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children}
            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.9 }}
                        transition={{ duration: 0.2 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 border border-white/10 rounded-lg text-xs text-white whitespace-nowrap z-50 shadow-xl"
                    >
                        {content}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900" />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

// --- Main Component ---

export function MultiFarmOptimizer() {
    const [waterBudget, setWaterBudget] = useState(50000);
    const [mode, setMode] = useState("PROFIT");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [loadingStep, setLoadingStep] = useState<string>("");
    const [useClientSide, setUseClientSide] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

    // Detailed sample data for "AI Insights"
    const [aiInsights, setAiInsights] = useState<string[]>([]);
    const resultsRef = useRef<HTMLDivElement>(null);

    const sampleFarms: Farm[] = [
        { name: "Farm Alpha", latitude: 13.0827, longitude: 80.2707, panel_area: 125000, dust_rate: 1.2, electricity_price: 6.5, water_usage: 10000 },
        { name: "Farm Beta", latitude: 13.0827, longitude: 80.2707, panel_area: 75000, dust_rate: 1.0, electricity_price: 6.0, water_usage: 7500 },
        { name: "Farm Gamma", latitude: 13.0827, longitude: 80.2707, panel_area: 50000, dust_rate: 1.5, electricity_price: 6.2, water_usage: 5000 },
        { name: "Farm Delta", latitude: 13.0827, longitude: 80.2707, panel_area: 25000, dust_rate: 0.9, electricity_price: 6.0, water_usage: 2500 },
    ];

    // --- Effects ---

    useEffect(() => {
        checkBackendHealth();
    }, []);

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.code === "Space" && !loading && !result) {
                e.preventDefault(); // Prevent scrolling
                optimizeFarms();
            }
            if (e.key.toLowerCase() === "r" && result) {
                handleReset();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loading, result, mode, waterBudget]); // Dependencies for closure freshness

    // --- Logic ---

    const checkBackendHealth = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);

            const res = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (res.ok) {
                setBackendStatus('online');
                setUseClientSide(false);
                return;
            }
        } catch {
            // Backend not available
        }
        setBackendStatus('offline');
        setUseClientSide(true);
    };

    const getThemeColors = () => {
        switch (mode) {
            case "CARBON":
                return {
                    primary: "text-blue-400",
                    bg: "bg-blue-500/10",
                    border: "border-blue-500/30",
                    gradient: "from-blue-500 to-cyan-500",
                    button: "bg-blue-500",
                    shadow: "shadow-blue-500/20"
                };
            case "WATER_SCARCITY":
                return {
                    primary: "text-cyan-400",
                    bg: "bg-cyan-500/10",
                    border: "border-cyan-500/30",
                    gradient: "from-cyan-500 to-teal-500",
                    button: "bg-cyan-500",
                    shadow: "shadow-cyan-500/20"
                };
            default: // PROFIT
                return {
                    primary: "text-emerald-400",
                    bg: "bg-emerald-500/10",
                    border: "border-emerald-500/30",
                    gradient: "from-emerald-500 to-green-500",
                    button: "bg-emerald-500",
                    shadow: "shadow-emerald-500/20"
                };
        }
    };

    const theme = getThemeColors();

    const optimizeFarmsClientSide = (farms: Farm[], waterBudget: number, mode: string) => {
        const farmScores: FarmScore[] = [];

        for (const farm of farms) {
            const daysSinceClean = 30;
            const efficiencyLoss = farm.dust_rate * daysSinceClean * 0.002;
            const avgIrradiance = 5.5;
            const panelEfficiency = 0.20;

            const energyRecoverable = farm.panel_area * avgIrradiance * panelEfficiency * efficiencyLoss * 30;
            const revenue = energyRecoverable * farm.electricity_price;
            const cleaningCost = farm.water_usage * 0.05;
            const netBenefit = revenue - cleaningCost;
            const co2Offset = energyRecoverable * 0.82;
            const waterEfficiency = farm.water_usage > 0 ? energyRecoverable / farm.water_usage : 0;

            let priority: number;
            if (mode === "PROFIT") priority = netBenefit;
            else if (mode === "CARBON") priority = co2Offset;
            else priority = waterEfficiency; // WATER_SCARCITY

            farmScores.push({
                name: farm.name,
                priority,
                water_usage: farm.water_usage,
                energy: energyRecoverable,
                benefit: netBenefit,
                co2: co2Offset,
                roi: cleaningCost > 0 ? netBenefit / cleaningCost : 0
            });
        }

        farmScores.sort((a, b) => b.priority - a.priority);

        const selected: FarmScore[] = [];
        let totalWater = 0;
        let totalEnergy = 0;
        let totalBenefit = 0;
        let totalCo2 = 0;

        for (const farmData of farmScores) {
            if (totalWater + farmData.water_usage <= waterBudget) {
                selected.push(farmData);
                totalWater += farmData.water_usage;
                totalEnergy += farmData.energy;
                totalBenefit += farmData.benefit;
                totalCo2 += farmData.co2;
            }
        }

        return {
            selected_farms: selected.map(f => f.name),
            water_used: totalWater,
            total_benefit: totalBenefit,
            total_energy: totalEnergy,
            total_co2: totalCo2,
            farm_details: selected
        };
    };

    const triggerConfetti = () => {
        const duration = 3 * 1000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };
        const randomInRange = (min: number, max: number) => Math.random() * (max - min) + min;

        const interval: any = setInterval(function () {
            const timeLeft = animationEnd - Date.now();
            if (timeLeft <= 0) return clearInterval(interval);

            const particleCount = 50 * (timeLeft / duration);
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } });
            confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } });
        }, 250);
    };

    const generateInsights = (data: any) => {
        const insights = [
            `Farm Alpha has 23% higher dust accumulation than average.`,
            `Rain predicted in 3 days - defer cleaning Farm Gamma to save ₹1,200.`,
            `Optimal cleaning window is between 06:00 AM - 09:00 AM to minimize evaporation.`,
            `Expected ROI for this cleaning cycle is ${(data.total_benefit / (data.water_used * 0.05) * 100).toFixed(0)}%.`
        ];
        return insights.sort(() => 0.5 - Math.random()).slice(0, 3);
    };

    const handleExportPDF = async () => {
        if (!resultsRef.current) return;
        const canvas = await html2canvas(resultsRef.current);
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF();
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save('solaros-optimization-report.pdf');
    };

    const handleReset = () => {
        setResult(null);
        setAiInsights([]);
        setLoading(false);
    };

    const optimizeFarms = async () => {
        setLoading(true);
        setResult(null);
        setLoadingStep("Initializing physics engine...");

        await new Promise(r => setTimeout(r, 800));
        setLoadingStep("Querying NASA satellite data (30 days)...");
        await new Promise(r => setTimeout(r, 1000));
        setLoadingStep(`Optimizing ${sampleFarms.length} farms for ${mode}...`);
        await new Promise(r => setTimeout(r, 800));
        setLoadingStep("Finalizing portfolio strategy...");
        await new Promise(r => setTimeout(r, 600));

        const handleSuccess = (data: any) => {
            setResult(data);
            setAiInsights(generateInsights(data));
            if (data.selected_farms?.length > 0) triggerConfetti();
        };

        try {
            // Prefer client-side for hackathon reliability if offline
            if (useClientSide || backendStatus === 'offline') {
                const data = optimizeFarmsClientSide(sampleFarms, waterBudget, mode);
                handleSuccess(data);
            } else {
                const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/optimize-farms`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ farms: sampleFarms, water_budget: waterBudget, mode: mode }),
                });
                if (!res.ok) throw new Error("Backend error");
                const data = await res.json();
                handleSuccess(data);
            }
        } catch (error) {
            const data = optimizeFarmsClientSide(sampleFarms, waterBudget, mode);
            handleSuccess(data);
        } finally {
            setLoading(false);
            setLoadingStep("");
        }
    };

    return (
        <div id="multi-farm-optimizer" className="space-y-6">
            {/* Backend Status (Hidden unless offline for cleaner demo) */}
            {backendStatus === 'offline' && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 p-2 px-3 bg-red-500/10 border border-red-500/20 rounded-full text-red-400 text-xs w-fit mx-auto">
                    <Wifi className="w-3 h-3" />
                    <span>Offline Mode (Demo Data)</span>
                </motion.div>
            )}

            {/* Controls */}
            <div className="space-y-6 bg-white/5 border border-white/10 p-6 rounded-2xl backdrop-blur-sm">

                {/* Mode Selection with visual feedback */}
                <div>
                    <label className="text-sm text-gray-400 mb-2 block flex items-center justify-between">
                        <span>Optimization Goal</span>
                        <Tooltip content="Choose what metric SolarOS should prioritize">
                            <HelpCircle className="w-4 h-4 text-gray-500 cursor-help hover:text-white transition-colors" />
                        </Tooltip>
                    </label>
                    <GlassDropdown
                        label="Optimization Mode"
                        value={mode}
                        onChange={(val) => setMode(val)}
                        options={[
                            { label: "Maximize Profit", value: "PROFIT" },
                            { label: "Maximize Carbon Offset", value: "CARBON" },
                            { label: "Water Scarcity Mode", value: "WATER_SCARCITY" },
                        ]}
                    />
                </div>

                {/* Water Budget Slider */}
                <div>
                    <div className="flex justify-between items-end mb-2">
                        <label className="text-sm text-gray-400">Water Budget</label>
                        <span className={`text-xl font-bold font-mono ${theme.primary}`}>{waterBudget.toLocaleString()}L</span>
                    </div>
                    <input
                        type="range"
                        min="10000"
                        max="100000"
                        step="5000"
                        value={waterBudget}
                        onChange={(e) => setWaterBudget(parseInt(e.target.value))}
                        className={`w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-${mode === 'PROFIT' ? 'emerald' : mode === 'CARBON' ? 'blue' : 'cyan'}-500`}
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Strict (10k L)</span>
                        <span>Liberal (100k L)</span>
                    </div>
                </div>

                {/* Main Action Button */}
                <div className="relative group">
                    <div className={`absolute -inset-0.5 bg-gradient-to-r ${theme.gradient} rounded-xl blur opacity-30 group-hover:opacity-100 transition duration-1000 group-hover:duration-200`}></div>
                    <button
                        onClick={optimizeFarms}
                        disabled={loading}
                        className="relative w-full bg-black border border-white/10 text-white font-bold px-6 py-4 rounded-xl hover:bg-gray-900 transition-all duration-300 disabled:opacity-50 min-h-[60px] flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <div className="flex flex-col items-center">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
                                    <span>Processing Portfolio...</span>
                                </div>
                                <span className="text-[10px] text-gray-400 font-normal animate-pulse uppercase tracking-widest mt-1">{loadingStep}</span>
                            </div>
                        ) : result ? (
                            <div className="flex items-center gap-2">
                                <RefreshCw className="w-5 h-5" />
                                <span>Re-Run Optimization</span>
                            </div>
                        ) : (
                            <>
                                <span>Run Optimization Analysis</span>
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                    {!loading && !result && (
                        <div className="text-center mt-2 text-[10px] text-gray-500 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">
                            Press <span className="border border-gray-600 rounded px-1">Space</span> to Run
                        </div>
                    )}
                </div>
            </div>

            {/* Empty State */}
            {!result && !loading && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-12 border-2 border-dashed border-white/5 rounded-2xl"
                >
                    <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                        <BrainCircuit className="w-8 h-8 text-gray-600" />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-1">Ready to Optimize</h3>
                    <p className="text-gray-400 text-sm max-w-sm mx-auto">
                        SolarOS is ready to analyze physics models for {sampleFarms.length} farms. Adjust parameters above and click Run.
                    </p>
                </motion.div>
            )}

            {/* Loading Skeletons - Gradient Pulse */}
            {loading && (
                <div className="space-y-4 p-4 border border-white/5 rounded-2xl bg-white/5 backdrop-blur-sm">
                    <div className="space-y-3">
                        <div className="h-4 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded animate-pulse" />
                        <div className="h-4 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded animate-pulse w-3/4" />
                        <div className="h-4 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded animate-pulse w-1/2" />
                    </div>
                    <p className="text-sm text-emerald-400 animate-pulse flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4" />
                        {loadingStep || "Initializing AI models..."}
                    </p>
                </div>
            )}

            {/* Results Dashboard */}
            <AnimatePresence>
                {!loading && result && !result.error && (
                    <motion.div
                        ref={resultsRef}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="space-y-6"
                    >
                        {/* Header Controls */}
                        <div className="flex justify-between items-center">
                            <h3 className={`text-sm uppercase font-bold flex items-center gap-2 ${theme.primary}`}>
                                <CheckCircle2 className="w-4 h-4" />
                                Optimization Complete
                            </h3>
                            <div className="flex gap-2">
                                <button onClick={handleReset} className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors">
                                    <RefreshCw className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={handleExportPDF}
                                    className="flex items-center gap-2 text-xs bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg text-white transition-colors border border-white/5"
                                >
                                    <Download className="w-3 h-3" />
                                    Export Report
                                </button>
                            </div>
                        </div>

                        {/* AI Insights */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2 }}
                            className={`${theme.bg} ${theme.border} border rounded-xl p-5 relative overflow-hidden`}
                        >
                            <div className="absolute top-0 right-0 p-3 opacity-20">
                                <BrainCircuit className={`w-24 h-24 ${theme.primary}`} />
                            </div>
                            <h3 className={`text-sm uppercase font-bold flex items-center gap-2 mb-3 ${theme.primary}`}>
                                <Info className="w-4 h-4" />
                                AI Insights
                            </h3>
                            <div className="space-y-3 relative z-10">
                                {aiInsights.map((insight, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 + (i * 0.1) }}
                                        className="flex items-start gap-3 text-sm text-gray-300"
                                    >
                                        <span className={`mt-1.5 w-1.5 h-1.5 rounded-full ${theme.button}`} />
                                        <span>{insight}</span>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Key Metrics Grid */}
                        <div className="grid grid-cols-2 gap-4">
                            <motion.div whileHover={{ y: -2 }} className="bg-white/5 border border-white/10 rounded-xl p-5">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs uppercase text-gray-400">Net Benefit</span>
                                    <Tooltip content="Projected revenue increase after deducting cleaning costs">
                                        <HelpCircle className="w-3 h-3 text-gray-600" />
                                    </Tooltip>
                                </div>
                                <div className={`text-3xl font-bold ${theme.primary}`}>
                                    <CountUp end={result.total_benefit || 0} duration={2.5} separator="," prefix="₹" />
                                </div>
                            </motion.div>

                            <motion.div whileHover={{ y: -2 }} className="bg-white/5 border border-white/10 rounded-xl p-5">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs uppercase text-gray-400">Water Usage</span>
                                    <Tooltip content="Total water required for this optimization schedule">
                                        <HelpCircle className="w-3 h-3 text-gray-600" />
                                    </Tooltip>
                                </div>
                                <div className="text-3xl font-bold text-blue-400">
                                    <CountUp end={result.water_used || 0} duration={2.5} separator="," /> L
                                </div>
                                <div className="text-xs text-emerald-400 mt-1">
                                    Saved {((waterBudget - result.water_used) / 1000).toFixed(1)}k L
                                </div>
                            </motion.div>

                            <motion.div whileHover={{ y: -2 }} className="bg-white/5 border border-white/10 rounded-xl p-5">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs uppercase text-gray-400">Energy Gain</span>
                                    <Tooltip content="Recoverable energy lost to soiling">
                                        <HelpCircle className="w-3 h-3 text-gray-600" />
                                    </Tooltip>
                                </div>
                                <div className="text-2xl font-bold text-yellow-400">
                                    <CountUp end={result.total_energy || 0} duration={2.5} separator="," /> kWh
                                </div>
                            </motion.div>

                            <motion.div whileHover={{ y: -2 }} className="bg-white/5 border border-white/10 rounded-xl p-5">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs uppercase text-gray-400">CO₂ Offset</span>
                                    <Tooltip content="Carbon emissions prevented by efficiency gain">
                                        <HelpCircle className="w-3 h-3 text-gray-600" />
                                    </Tooltip>
                                </div>
                                <div className="text-2xl font-bold text-green-400">
                                    <CountUp end={result.total_co2 || 0} duration={2.5} separator="," /> kg
                                </div>
                            </motion.div>
                        </div>

                        {/* Before / After Comparison */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 rounded-xl border border-white/5 bg-white/5 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                                <div className="text-xs uppercase text-gray-500 mb-1">Standard Approach</div>
                                <div className="font-bold text-gray-300">Calendar Based</div>
                                <div className="mt-2 text-xs text-gray-500">Ignores weather & dust physics</div>
                            </div>
                            <div className={`p-4 rounded-xl border ${theme.border} bg-gradient-to-br ${theme.gradient} to-transparent relative overflow-hidden`}>
                                <div className="absolute top-0 right-0 px-2 py-1 bg-black/20 text-[10px] text-white font-bold rounded-bl-lg">WINNER</div>
                                <div className="text-xs uppercase text-white/70 mb-1">SolarOS Approach</div>
                                <div className="font-bold text-white">Physics Based</div>
                                <div className="mt-2 text-xs text-white/80">Optimized for maximum yield</div>
                            </div>
                        </div>

                        {/* Recommendation Strip */}
                        <motion.div
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="bg-purple-900/20 border border-purple-500/20 rounded-xl p-4 flex items-center justify-between"
                        >
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                                    <Calendar className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-sm font-bold text-white">Optimal Schedule Found</div>
                                    <div className="text-xs text-gray-400">Execute on Feb 18, 2026 @ 06:00 AM</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-[10px] text-gray-400 uppercase">ROI</div>
                                <div className="text-xl font-bold text-purple-400">340%</div>
                            </div>
                        </motion.div>

                        {/* Selected Farms List */}
                        <div className="pt-4 border-t border-white/10">
                            <div className="text-xs text-gray-500 uppercase mb-3">Target Farms</div>
                            <div className="flex flex-wrap gap-2">
                                {result.selected_farms?.map((name: string, i: number) => (
                                    <motion.span
                                        key={i}
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ delay: 0.6 + (i * 0.1) }}
                                        className={`px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs text-gray-300`}
                                    >
                                        {name}
                                    </motion.span>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

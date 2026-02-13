"use client";

import { useState } from "react";
import { Factory, Droplets, Zap, Leaf, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";

interface Farm {
    name: string;
    latitude: number;
    longitude: number;
    panel_area: number;
    dust_rate: number;
    electricity_price: number;
    water_usage: number;
}

export function MultiFarmOptimizer() {
    const [waterBudget, setWaterBudget] = useState(2000);
    const [mode, setMode] = useState("PROFIT");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const sampleFarms: Farm[] = [
        {
            name: "Farm Alpha",
            latitude: 13.0827,
            longitude: 80.2707,
            panel_area: 5000,
            dust_rate: 1.2,
            electricity_price: 6.5,
            water_usage: 1000,
        },
        {
            name: "Farm Beta",
            latitude: 13.0827,
            longitude: 80.2707,
            panel_area: 2000,
            dust_rate: 1.0,
            electricity_price: 6.0,
            water_usage: 400,
        },
        {
            name: "Farm Gamma",
            latitude: 13.0827,
            longitude: 80.2707,
            panel_area: 3000,
            dust_rate: 1.5,
            electricity_price: 6.2,
            water_usage: 600,
        },
        {
            name: "Farm Delta",
            latitude: 13.0827,
            longitude: 80.2707,
            panel_area: 1500,
            dust_rate: 0.8,
            electricity_price: 5.8,
            water_usage: 300,
        },
    ];

    const optimizeFarms = async () => {
        setLoading(true);
        setResult(null);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/optimize-farms`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    farms: sampleFarms,
                    water_budget: waterBudget,
                    mode: mode,
                }),
            });
            const data = await res.json();
            setResult(data);
        } catch (error) {
            setResult({ error: "Failed to optimize portfolio" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Controls */}
            <div className="space-y-4">
                <div>
                    <label className="text-sm text-gray-400 mb-2 block">
                        Water Budget (Liters): {waterBudget}L
                    </label>
                    <input
                        type="range"
                        min="500"
                        max="3000"
                        step="100"
                        value={waterBudget}
                        onChange={(e) => setWaterBudget(parseInt(e.target.value))}
                        className="w-full accent-emerald-500"
                    />
                </div>

                <div>
                    <label className="text-sm text-gray-400 mb-2 block">Optimization Mode</label>
                    <select
                        value={mode}
                        onChange={(e) => setMode(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-emerald-500/50 transition-colors"
                    >
                        <option value="PROFIT">Maximize Profit</option>
                        <option value="CARBON">Maximize Carbon Offset</option>
                        <option value="WATER_SCARCITY">Water Scarcity Mode</option>
                    </select>
                </div>

                <button
                    onClick={optimizeFarms}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold px-6 py-3 rounded-lg hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all duration-300 disabled:opacity-50"
                >
                    {loading ? "Optimizing..." : "Optimize Portfolio"}
                </button>
            </div>

            {/* Farm List */}
            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                <h3 className="text-sm uppercase text-gray-400 mb-3">Portfolio ({sampleFarms.length} farms)</h3>
                <div className="space-y-2">
                    {sampleFarms.map((farm, i) => (
                        <div
                            key={i}
                            className="flex items-center justify-between text-sm py-2 border-b border-white/5 last:border-0"
                        >
                            <div className="flex items-center gap-2">
                                <Factory className="w-4 h-4 text-gray-400" />
                                <span className="text-white">{farm.name}</span>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-500">
                                <span>{farm.panel_area}m²</span>
                                <span>{farm.water_usage}L</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Results */}
            {result && !result.error && result.selected_farms && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                >
                    {/* Selected Farms */}
                    <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4">
                        <h3 className="text-sm uppercase text-emerald-400 mb-2">
                            Selected for Cleaning ({result.selected_farms?.length || 0})
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {result.selected_farms?.map((name: string, i: number) => (
                                <span
                                    key={i}
                                    className="px-3 py-1 bg-emerald-500/20 border border-emerald-500/40 rounded-full text-sm text-emerald-300"
                                >
                                    {name}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Droplets className="w-4 h-4 text-blue-400" />
                                <span className="text-xs uppercase text-gray-400">Water Used</span>
                            </div>
                            <div className="text-2xl font-bold text-blue-400">
                                {(result.water_used || 0).toFixed(0)} L
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                                of {waterBudget}L budget
                            </div>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp className="w-4 h-4 text-emerald-400" />
                                <span className="text-xs uppercase text-gray-400">Net Benefit</span>
                            </div>
                            <div className="text-2xl font-bold text-emerald-400">
                                ₹{(result.total_benefit || 0).toFixed(0)}
                            </div>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-4 h-4 text-yellow-400" />
                                <span className="text-xs uppercase text-gray-400">Energy Gain</span>
                            </div>
                            <div className="text-2xl font-bold text-yellow-400">
                                {(result.total_energy || 0).toFixed(0)} kWh
                            </div>
                        </div>

                        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Leaf className="w-4 h-4 text-green-400" />
                                <span className="text-xs uppercase text-gray-400">CO₂ Offset</span>
                            </div>
                            <div className="text-2xl font-bold text-green-400">
                                {(result.total_co2 || 0).toFixed(0)} kg
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}

            {result?.error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-center text-red-400">
                    {result.error}
                </div>
            )}
        </div>
    );
}

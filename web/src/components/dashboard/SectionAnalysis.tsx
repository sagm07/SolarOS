"use client";

import { GlassDropdown } from "../ui/GlassDropdown";
import { useState } from "react";
import { motion } from "framer-motion";
import { Grid3x3, Droplets, Zap, Leaf, DollarSign, CheckCircle2 } from "lucide-react";

interface Section {
    id: string;
    row: number;
    col: number;
    panel_area_m2: number;
    energy_loss_kwh: number;
    energy_loss_percent: number;
    roi_score: number;
    cleaning_cost: number;
}

interface AnalysisResult {
    sections: Section[];
    selected_section_ids: string[];
    water_used: number;
    total_energy_recovered: number;
    total_co2_saved: number;
    total_cost_saved: number;
}

export function SectionAnalysis() {
    const [farmSize, setFarmSize] = useState(25); // MW
    const [gridRows, setGridRows] = useState(5);
    const [gridCols, setGridCols] = useState(5);
    const [waterBudget, setWaterBudget] = useState(25000);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);

    const analyzeSections = async () => {
        setLoading(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/analyze-sections`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    farm_size_mw: farmSize,
                    grid_rows: gridRows,
                    grid_cols: gridCols,
                    water_budget: waterBudget,
                }),
            });

            const data = await res.json();
            setResult(data);
        } catch (error) {
            console.error('Section analysis error:', error);
        } finally {
            setLoading(false);
        }
    };

    const getColorForLoss = (lossPercent: number) => {
        if (lossPercent > 8) return 'bg-red-500/80';
        if (lossPercent > 5) return 'bg-orange-500/80';
        if (lossPercent > 3) return 'bg-yellow-500/80';
        return 'bg-green-500/80';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <Grid3x3 className="w-8 h-8 text-emerald-400" />
                <div>
                    <h2 className="text-2xl font-bold text-white">Section-Level Analysis</h2>
                    <p className="text-sm text-gray-400">Precision panel-grid optimization</p>
                </div>
            </div>

            {/* Controls */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Farm Size */}
                    <div>
                        <GlassDropdown
                            label="Farm Size (MW)"
                            value={farmSize}
                            onChange={(val) => setFarmSize(Number(val))}
                            options={[
                                { label: "5 MW", value: 5 },
                                { label: "25 MW", value: 25 },
                                { label: "50 MW", value: 50 },
                            ]}
                            className="z-50"
                        />
                    </div>

                    {/* Grid Size */}
                    <div>
                        <GlassDropdown
                            label="Grid Size"
                            value={`${gridRows}x${gridCols}`}
                            onChange={(val) => {
                                const [rows, cols] = (val as string).split('x').map(Number);
                                setGridRows(rows);
                                setGridCols(cols);
                            }}
                            options={[
                                { label: "3×3 (9 sections)", value: "3x3" },
                                { label: "5×5 (25 sections)", value: "5x5" },
                                { label: "7×7 (49 sections)", value: "7x7" },
                            ]}
                            className="z-40"
                        />
                    </div>

                    {/* Water Budget */}
                    <div className="md:col-span-2">
                        <label className="text-sm text-gray-400 mb-2 block">
                            Water Budget: {waterBudget.toLocaleString()}L
                        </label>
                        <input
                            type="range"
                            min="10000"
                            max="50000"
                            step="5000"
                            value={waterBudget}
                            onChange={(e) => setWaterBudget(parseInt(e.target.value))}
                            className="w-full accent-emerald-500"
                        />
                    </div>
                </div>

                <button
                    onClick={analyzeSections}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-semibold py-3 rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50"
                >
                    {loading ? 'Analyzing Sections...' : 'Analyze Section Grid'}
                </button>
            </div>

            {/* Results */}
            {result && (
                <div className="space-y-6">
                    {/* Section Grid Heatmap */}
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-4">
                            Farm Grid ({gridRows}×{gridCols})
                        </h3>
                        <div
                            className="grid gap-2"
                            style={{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }}
                        >
                            {result.sections.map((section) => {
                                const isSelected = result.selected_section_ids.includes(section.id);
                                return (
                                    <motion.div
                                        key={section.id}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className={`
                                            aspect-square rounded-lg p-2 relative
                                            ${getColorForLoss(section.energy_loss_percent)}
                                            ${isSelected ? 'ring-4 ring-emerald-400' : ''}
                                            transition-all hover:scale-105 cursor-pointer
                                        `}
                                        title={`${section.id}: ${section.energy_loss_kwh.toFixed(0)} kWh loss, ROI: ${section.roi_score.toFixed(1)}`}
                                    >
                                        <div className="text-xs font-mono text-white/80">{section.id}</div>
                                        <div className="text-lg font-bold text-white mt-1">
                                            {section.energy_loss_kwh.toFixed(0)}
                                        </div>
                                        <div className="text-xs text-white/70">kWh</div>

                                        {isSelected && (
                                            <div className="absolute top-1 right-1">
                                                <CheckCircle2 className="w-5 h-5 text-white" />
                                            </div>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </div>

                        {/* Legend */}
                        <div className="mt-4 flex items-center gap-4 text-sm">
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-green-500/80 rounded"></div>
                                <span className="text-gray-400">&lt;3% loss</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-yellow-500/80 rounded"></div>
                                <span className="text-gray-400">3-5% loss</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-orange-500/80 rounded"></div>
                                <span className="text-gray-400">5-8% loss</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 bg-red-500/80 rounded"></div>
                                <span className="text-gray-400">&gt;8% loss</span>
                            </div>
                        </div>
                    </div>

                    {/* Impact Metrics */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <MetricCard
                            icon={<Droplets />}
                            label="Water Used"
                            value={`${result.water_used.toLocaleString()}L`}
                            subtitle={`of ${waterBudget.toLocaleString()}L`}
                        />
                        <MetricCard
                            icon={<Zap />}
                            label="Energy Recovered"
                            value={`${result.total_energy_recovered.toLocaleString()} kWh`}
                        />
                        <MetricCard
                            icon={<Leaf />}
                            label="CO₂ Offset"
                            value={`${result.total_co2_saved.toLocaleString()} kg`}
                        />
                        <MetricCard
                            icon={<DollarSign />}
                            label="Net Savings"
                            value={`₹${result.total_cost_saved.toLocaleString()}`}
                        />
                    </div>

                    {/* Selected Sections Summary */}
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-3">
                            Cleaning Schedule ({result.selected_section_ids.length} sections)
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {result.selected_section_ids.map((id) => (
                                <div
                                    key={id}
                                    className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm font-mono border border-emerald-500/30"
                                >
                                    {id}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function MetricCard({ icon, label, value, subtitle }: any) {
    return (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2 text-emerald-400">
                {icon}
                <span className="text-sm text-gray-400">{label}</span>
            </div>
            <div className="text-2xl font-bold text-white">{value}</div>
            {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
        </div>
    );
}

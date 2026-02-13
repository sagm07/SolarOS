"use client";

import { useState } from "react";
import { CloudRain, Droplets, Leaf, TrendingDown } from "lucide-react";
import { motion } from "framer-motion";

export function RainIntelligence() {
    const [location, setLocation] = useState("Chennai, Tamil Nadu");
    const [forecast, setForecast] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const locationMap: Record<string, { lat: number; lng: number }> = {
        "Chennai, Tamil Nadu": { lat: 13.0827, lng: 80.2707 },
        "Rajasthan (Jaipur)": { lat: 26.9124, lng: 75.7873 },
        "Gujarat (Ahmedabad)": { lat: 23.0225, lng: 72.5714 },
        "Maharashtra (Mumbai)": { lat: 19.0760, lng: 72.8777 },
        "Karnataka (Bangalore)": { lat: 12.9716, lng: 77.5946 },
        "Delhi NCR": { lat: 28.7041, lng: 77.1025 },
        "Punjab (Ludhiana)": { lat: 30.9010, lng: 75.8573 },
        "Telangana (Hyderabad)": { lat: 17.3850, lng: 78.4867 },
        "Andhra Pradesh (Visakhapatnam)": { lat: 17.6868, lng: 83.2185 },
        "California, USA": { lat: 36.7783, lng: -119.4179 },
    };

    const checkRainForecast = async () => {
        setLoading(true);
        setForecast(null); // Reset forecast
        const coords = locationMap[location];

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const url = `${apiUrl}/rain-forecast?latitude=${coords.lat}&longitude=${coords.lng}&days=7`;

            const res = await fetch(url);

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();

            setForecast(data);
        } catch (error: any) {
            setForecast({ error: `Failed to fetch forecast: ${error.message}` });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Controls */}
            <div className="space-y-4">
                <div>
                    <label className="text-sm text-gray-400 mb-2 block">Location</label>
                    <select
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="w-full bg-black/60 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500/50 transition-colors [&>option]:bg-black [&>option]:text-white [&>option]:py-2"
                        style={{
                            colorScheme: 'dark',
                        }}
                    >
                        <option value="Chennai, Tamil Nadu" className="bg-black text-white py-2">Chennai, Tamil Nadu</option>
                        <option value="Rajasthan (Jaipur)" className="bg-black text-white py-2">Rajasthan (Jaipur)</option>
                        <option value="Gujarat (Ahmedabad)" className="bg-black text-white py-2">Gujarat (Ahmedabad)</option>
                        <option value="Maharashtra (Mumbai)" className="bg-black text-white py-2">Maharashtra (Mumbai)</option>
                        <option value="Karnataka (Bangalore)" className="bg-black text-white py-2">Karnataka (Bangalore)</option>
                        <option value="Delhi NCR" className="bg-black text-white py-2">Delhi NCR</option>
                        <option value="Punjab (Ludhiana)" className="bg-black text-white py-2">Punjab (Ludhiana)</option>
                        <option value="Telangana (Hyderabad)" className="bg-black text-white py-2">Telangana (Hyderabad)</option>
                        <option value="Andhra Pradesh (Visakhapatnam)" className="bg-black text-white py-2">Andhra Pradesh (Visakhapatnam)</option>
                        <option value="California, USA" className="bg-black text-white py-2">California, USA</option>
                    </select>
                </div>

                <button
                    onClick={checkRainForecast}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold px-6 py-3 rounded-lg hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] transition-all duration-300 disabled:opacity-50"
                >
                    {loading ? "Analyzing..." : "Check Rain Forecast"}
                </button>
            </div>

            {/* Results */}
            {forecast && !forecast.error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                >
                    {/* Decision Card */}
                    <div
                        className={`p-6 rounded-xl border-2 ${forecast.should_wait
                            ? "bg-cyan-500/10 border-cyan-500/30"
                            : "bg-emerald-500/10 border-emerald-500/30"
                            }`}
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <CloudRain
                                className={forecast.should_wait ? "text-cyan-400" : "text-emerald-400"}
                            />
                            <span className="font-bold text-lg">
                                {forecast.decision === "WAIT" ? "DEFER CLEANING" : "PROCEED WITH CLEANING"}
                            </span>
                        </div>
                        <p className="text-sm text-gray-300">{forecast.message}</p>
                    </div>

                    {/* Metrics Grid */}
                    {forecast.should_wait && (
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <CloudRain className="w-4 h-4 text-cyan-400" />
                                    <span className="text-xs uppercase text-gray-400">Rain Forecast</span>
                                </div>
                                <div className="text-2xl font-bold text-cyan-400">
                                    {forecast.rain_forecast_mm.toFixed(1)} mm
                                </div>
                            </div>

                            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <TrendingDown className="w-4 h-4 text-emerald-400" />
                                    <span className="text-xs uppercase text-gray-400">Dust Reduction</span>
                                </div>
                                <div className="text-2xl font-bold text-emerald-400">
                                    {(forecast.dust_reduction_estimate * 100).toFixed(0)}%
                                </div>
                            </div>

                            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <Droplets className="w-4 h-4 text-blue-400" />
                                    <span className="text-xs uppercase text-gray-400">Water Saved</span>
                                </div>
                                <div className="text-2xl font-bold text-blue-400">
                                    {forecast.water_saved_liters.toFixed(0)} L
                                </div>
                            </div>

                            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                    <Leaf className="w-4 h-4 text-green-400" />
                                    <span className="text-xs uppercase text-gray-400">Sustainability +</span>
                                </div>
                                <div className="text-2xl font-bold text-green-400">
                                    {forecast.sustainability_boost.toFixed(0)}
                                </div>
                            </div>
                        </div>
                    )}
                </motion.div>
            )}

            {forecast?.error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-center text-red-400">
                    {forecast.error}
                </div>
            )}
        </div>
    );
}

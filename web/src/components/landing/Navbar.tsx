"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Leaf, Moon, Sun } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export function Navbar() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <motion.nav
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4"
        >
            <div className="glass-card rounded-full px-6 py-3 flex items-center gap-8 bg-black/20 backdrop-blur-md border border-white/10">

                {/* Logo */}
                <Link href="/" className="flex items-center gap-2">
                    <div className="p-1.5 rounded-full bg-lime-accent">
                        <Leaf className="w-4 h-4 text-black" />
                    </div>
                    <span className="text-lg font-bold text-white">
                        SolarOS
                    </span>
                </Link>

                {/* Links */}
                <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-200">
                    <Link
                        href="/features"
                        className="relative hover:text-emerald-400 transition-colors group"
                    >
                        Features
                        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                    </Link>
                    <Link
                        href="/how-it-works"
                        className="relative hover:text-emerald-400 transition-colors group"
                    >
                        How it Works
                        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                    </Link>
                    <Link
                        href="/about"
                        className="relative hover:text-emerald-400 transition-colors group"
                    >
                        About
                        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                    </Link>
                    <Link
                        href="/dashboard"
                        className="relative hover:text-emerald-400 transition-colors group"
                    >
                        Dashboard
                        <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                    </Link>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    <motion.button
                        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                        whileHover={{ scale: 1.1, rotate: 15 }}
                        whileTap={{ scale: 0.9 }}
                        className="p-2.5 rounded-full hover:bg-white/10 text-gray-300 transition-all duration-300 relative group"
                    >
                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 opacity-0 group-hover:opacity-100 transition-opacity blur-md" />
                        {mounted ? theme === "dark" ? <Sun className="w-4 h-4 relative z-10" /> : <Moon className="w-4 h-4 relative z-10" /> : <div className="w-4 h-4" />}
                    </motion.button>

                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Link
                            href="#live-analysis"
                            onClick={(e) => {
                                e.preventDefault();
                                document.getElementById('live-analysis')?.scrollIntoView({ behavior: 'smooth' });
                            }}
                            className="relative group bg-gradient-to-r from-emerald-500 to-cyan-500 text-black text-sm font-bold px-6 py-2.5 rounded-full overflow-hidden transition-all duration-300"
                        >
                            <span className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <span className="relative z-10">Get Started</span>
                        </Link>
                    </motion.div>
                </div>

            </div>
        </motion.nav>
    );
}

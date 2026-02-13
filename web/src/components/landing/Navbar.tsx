"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Leaf, Moon, Sun, Menu, X } from "lucide-react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { SolarLogo } from "../ui/SolarLogo";

export function Navbar() {
    const { theme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Close menu when clicking outside
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isMenuOpen]);

    const navLinks = [
        { href: "/features", label: "Features" },
        { href: "/how-it-works", label: "How it Works" },
        { href: "/about", label: "About" },
        { href: "/dashboard", label: "Dashboard" },
    ];

    return (
        <>
            <motion.nav
                initial={{ y: -100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4"
            >
                <div className="glass-card rounded-full px-4 md:px-6 py-3 flex items-center gap-4 md:gap-8 bg-black/20 backdrop-blur-md border border-white/10 w-full max-w-5xl">

                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <SolarLogo size="md" variant="default" />
                    </Link>

                    {/* Desktop Links */}
                    <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-200 flex-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="relative hover:text-emerald-400 transition-colors group"
                            >
                                {link.label}
                                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-emerald-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                            </Link>
                        ))}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 ml-auto">
                        {/* Theme Toggle */}
                        <motion.button
                            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                            whileHover={{ scale: 1.1, rotate: 15 }}
                            whileTap={{ scale: 0.9 }}
                            className="p-2.5 rounded-full hover:bg-white/10 text-gray-300 transition-all duration-300 relative group"
                        >
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 opacity-0 group-hover:opacity-100 transition-opacity blur-md" />
                            {mounted ? theme === "dark" ? <Sun className="w-4 h-4 relative z-10" /> : <Moon className="w-4 h-4 relative z-10" /> : <div className="w-4 h-4" />}
                        </motion.button>

                        {/* Get Started Button - Hidden on mobile */}
                        <motion.div
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="hidden md:block"
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

                        {/* Mobile Menu Button */}
                        <motion.button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            whileTap={{ scale: 0.9 }}
                            className="md:hidden p-2.5 rounded-full hover:bg-white/10 text-gray-300 transition-all duration-300"
                        >
                            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                        </motion.button>
                    </div>

                </div>
            </motion.nav>

            {/* Mobile Menu */}
            <AnimatePresence>
                {isMenuOpen && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsMenuOpen(false)}
                            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 md:hidden"
                        />

                        {/* Menu Panel */}
                        <motion.div
                            initial={{ x: "100%" }}
                            animate={{ x: 0 }}
                            exit={{ x: "100%" }}
                            transition={{ type: "spring", damping: 25, stiffness: 200 }}
                            className="fixed right-0 top-0 bottom-0 w-[280px] bg-black/95 backdrop-blur-xl border-l border-white/10 z-50 md:hidden"
                        >
                            <div className="flex flex-col h-full p-6 pt-24">
                                {/* Navigation Links */}
                                <div className="flex flex-col gap-1">
                                    {navLinks.map((link, index) => (
                                        <motion.div
                                            key={link.href}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <Link
                                                href={link.href}
                                                onClick={() => setIsMenuOpen(false)}
                                                className="block px-4 py-3 text-gray-200 hover:text-emerald-400 hover:bg-white/5 rounded-lg transition-all duration-300 text-lg font-medium"
                                            >
                                                {link.label}
                                            </Link>
                                        </motion.div>
                                    ))}
                                </div>

                                {/* Get Started Button */}
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.4 }}
                                    className="mt-8"
                                >
                                    <Link
                                        href="#live-analysis"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            setIsMenuOpen(false);
                                            document.getElementById('live-analysis')?.scrollIntoView({ behavior: 'smooth' });
                                        }}
                                        className="block text-center bg-gradient-to-r from-emerald-500 to-cyan-500 text-black text-base font-bold px-6 py-3 rounded-full hover:shadow-lg hover:shadow-emerald-500/50 transition-all duration-300"
                                    >
                                        Get Started
                                    </Link>
                                </motion.div>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </>
    );
}

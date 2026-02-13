"use client";

import { Leaf } from "lucide-react";
import Link from "next/link";

export function Footer() {
    return (
        <footer className="py-12 border-t border-white/10 bg-black/20 backdrop-blur-lg">
            <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2">
                    <Leaf className="w-5 h-5 text-emerald-500" />
                    <span className="font-bold text-gray-200">SolarOS</span>
                    <span className="text-gray-500 text-sm ml-2">© 2026</span>
                </div>

                <div className="flex items-center gap-8 text-sm text-gray-400">
                    {["Privacy", "Terms", "Contact", "Docs"].map((link) => (
                        <Link key={link} href="#" className="hover:text-emerald-400 transition-colors">
                            {link}
                        </Link>
                    ))}
                </div>
            </div>
        </footer>
    );
}

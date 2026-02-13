"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check } from "lucide-react";

interface Option {
    value: string | number;
    label: string;
    group?: string;
}

interface GlassDropdownProps {
    value: string | number;
    onChange: (value: any) => void;
    options: Option[];
    label?: string;
    className?: string;
}

export function GlassDropdown({ value, onChange, options, label, className = "" }: GlassDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const selectedOption = options.find(opt => opt.value === value);

    // Group options if needed
    const groups = options.reduce((acc, opt) => {
        const group = opt.group || "default";
        if (!acc[group]) acc[group] = [];
        acc[group].push(opt);
        return acc;
    }, {} as Record<string, Option[]>);

    const hasGroups = Object.keys(groups).length > 1 || (Object.keys(groups).length === 1 && Object.keys(groups)[0] !== "default");

    return (
        <div className={`relative ${className}`} ref={dropdownRef}>
            {label && <label className="text-sm text-gray-400 mb-2 block">{label}</label>}

            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    w-full flex items-center justify-between
                    bg-black/60 backdrop-blur-xl border border-white/10 
                    rounded-lg px-4 py-3 text-white 
                    hover:border-emerald-500/50 hover:shadow-[0_0_15px_rgba(16,185,129,0.2)]
                    transition-all duration-300 group
                `}
            >
                <span className="truncate mr-2 font-medium">
                    {selectedOption?.label || value}
                </span>
                <ChevronDown
                    className={`w-4 h-4 text-emerald-400 transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
                />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="absolute z-50 w-full mt-2 overflow-hidden rounded-xl border border-white/10 bg-black/90 backdrop-blur-2xl shadow-2xl max-h-64 overflow-y-auto custom-scrollbar"
                    >
                        <div className="p-1">
                            {hasGroups ? (
                                Object.entries(groups).map(([group, groupOptions]) => (
                                    <div key={group} className="mb-2 last:mb-0">
                                        <div className="px-3 py-1.5 text-xs font-semibold text-emerald-500/80 uppercase tracking-wider">
                                            {group}
                                        </div>
                                        {groupOptions.map((opt) => (
                                            <DropdownItem
                                                key={opt.value}
                                                option={opt}
                                                isSelected={opt.value === value}
                                                onClick={() => {
                                                    onChange(opt.value);
                                                    setIsOpen(false);
                                                }}
                                            />
                                        ))}
                                    </div>
                                ))
                            ) : (
                                options.map((opt) => (
                                    <DropdownItem
                                        key={opt.value}
                                        option={opt}
                                        isSelected={opt.value === value}
                                        onClick={() => {
                                            onChange(opt.value);
                                            setIsOpen(false);
                                        }}
                                    />
                                ))
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

function DropdownItem({ option, isSelected, onClick }: { option: Option, isSelected: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`
                w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm text-left
                transition-all duration-200
                ${isSelected
                    ? "bg-emerald-500/20 text-white"
                    : "text-gray-300 hover:bg-white/10 hover:text-white"
                }
            `}
        >
            <span className="truncate">{option.label}</span>
            {isSelected && <Check className="w-4 h-4 text-emerald-400 flex-shrink-0 ml-2" />}
        </button>
    );
}

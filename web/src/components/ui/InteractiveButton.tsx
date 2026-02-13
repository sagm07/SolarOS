"use client";

import { motion } from "framer-motion";
import { ReactNode, useState } from "react";
import { clsx } from "clsx";

interface InteractiveButtonProps {
    children: ReactNode;
    onClick?: () => void;
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg";
    className?: string;
    disabled?: boolean;
}

export function InteractiveButton({
    children,
    onClick,
    variant = "primary",
    size = "md",
    className,
    disabled = false,
}: InteractiveButtonProps) {
    const [ripples, setRipples] = useState<{ x: number; y: number; id: number }[]>([]);

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
        if (disabled) return;

        // Create ripple effect
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const newRipple = { x, y, id: Date.now() };
        setRipples((prev) => [...prev, newRipple]);

        // Remove ripple after animation
        setTimeout(() => {
            setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
        }, 600);

        onClick?.();
    };

    const sizeClasses = {
        sm: "px-4 py-2 text-sm",
        md: "px-6 py-3 text-base",
        lg: "px-8 py-4 text-lg",
    };

    const variantClasses = {
        primary:
            "bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_rgba(16,185,129,0.6)]",
        secondary:
            "bg-white/10 backdrop-blur-md border border-white/20 text-white hover:bg-white/15 hover:border-white/30",
        ghost:
            "bg-transparent text-white hover:bg-white/5 border border-transparent hover:border-white/10",
    };

    return (
        <motion.button
            onClick={handleClick}
            disabled={disabled}
            whileHover={{ scale: disabled ? 1 : 1.05 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            className={clsx(
                "relative overflow-hidden rounded-full transition-all duration-300",
                sizeClasses[size],
                variantClasses[variant],
                disabled && "opacity-50 cursor-not-allowed",
                className
            )}
        >
            {/* Gradient overlay on hover */}
            <motion.div
                className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0"
                initial={{ x: "-100%" }}
                whileHover={{ x: "100%" }}
                transition={{ duration: 0.6, ease: "easeInOut" }}
            />

            {/* Ripple effects */}
            {ripples.map((ripple) => (
                <motion.span
                    key={ripple.id}
                    className="absolute bg-white/30 rounded-full pointer-events-none"
                    style={{
                        left: ripple.x,
                        top: ripple.y,
                        width: 0,
                        height: 0,
                    }}
                    initial={{ width: 0, height: 0, opacity: 1 }}
                    animate={{
                        width: 400,
                        height: 400,
                        opacity: 0,
                        x: -200,
                        y: -200,
                    }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                />
            ))}

            {/* Content */}
            <span className="relative z-10 flex items-center justify-center gap-2">
                {children}
            </span>
        </motion.button>
    );
}

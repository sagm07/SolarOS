
import { clsx } from "clsx";

interface SolarLogoProps {
    className?: string; // Additional classes for wrapper
    variant?: "default" | "icon-only" | "text-only" | "vertical";
    size?: "sm" | "md" | "lg" | "xl";
    showSubtitle?: boolean;
}

export function SolarLogo({
    className,
    variant = "default",
    size = "md",
    showSubtitle = true
}: SolarLogoProps) {

    // Size Mappings
    const sizeClasses = {
        sm: "h-8",
        md: "h-12",
        lg: "h-16",
        xl: "h-24"
    };

    const fontSizeClasses = {
        sm: "text-lg",
        md: "text-2xl",
        lg: "text-4xl",
        xl: "text-6xl"
    };

    const subtitleSizeClasses = {
        sm: "text-[8px]",
        md: "text-[10px]",
        lg: "text-xs",
        xl: "text-sm"
    };

    return (
        <div className={clsx("flex items-center gap-3 select-none",
            variant === "vertical" && "flex-col gap-2",
            className
        )}>
            {/* PIXEL SUN ICON */}
            {(variant === "default" || variant === "icon-only" || variant === "vertical") && (
                <div className={clsx("relative aspect-square shrink-0", sizeClasses[size])}>
                    {/* SVG Implementation of Pixel Art Sun */}
                    <svg viewBox="0 0 16 16" className="w-full h-full drop-shadow-[0_0_8px_rgba(250,204,21,0.6)]" fill="none" xmlns="http://www.w3.org/2000/svg">
                        {/* Core (Yellow) */}
                        <path d="M5 5H11V11H5V5Z" fill="#FACC15" />

                        {/* Inner Rays (Orange/Yellow) */}
                        <path d="M5 4H11V5H11V11H12V5H11V4ZM4 5V11H5V5H4ZM5 11H11V12H5V11ZM11 5V11H12V5H11Z" fill="#F59E0B" fillOpacity="0.5" />

                        {/* Outer Rays (Pixel Spikes) */}
                        {/* Top */}
                        <rect x="7" y="1" width="2" height="2" fill="#FACC15" />
                        <rect x="3" y="2" width="1" height="1" fill="#FACC15" />
                        <rect x="12" y="2" width="1" height="1" fill="#FACC15" />

                        {/* Bottom */}
                        <rect x="7" y="13" width="2" height="2" fill="#FACC15" />
                        <rect x="3" y="13" width="1" height="1" fill="#FACC15" />
                        <rect x="12" y="13" width="1" height="1" fill="#FACC15" />

                        {/* Left */}
                        <rect x="1" y="7" width="2" height="2" fill="#FACC15" />
                        <rect x="2" y="3" width="1" height="1" fill="#FACC15" />
                        <rect x="2" y="12" width="1" height="1" fill="#FACC15" />

                        {/* Right */}
                        <rect x="13" y="7" width="2" height="2" fill="#FACC15" />
                        <rect x="13" y="3" width="1" height="1" fill="#FACC15" />
                        <rect x="13" y="12" width="1" height="1" fill="#FACC15" />
                    </svg>
                </div>
            )}

            {/* TEXT */}
            {(variant === "default" || variant === "text-only" || variant === "vertical") && (
                <div className={clsx("flex flex-col font-mono tracking-tight leading-none",
                    variant === "vertical" ? "items-center" : "items-end"
                )}>
                    {/* Main Text: SolarOS */}
                    <div className={clsx("font-bold text-white flex", fontSizeClasses[size])}>
                        <span className="text-white">Solar</span>
                        <span className="text-yellow-400">OS</span>
                    </div>

                    {/* Subtitle: rays into ways */}
                    {showSubtitle && (
                        <div className={clsx("text-yellow-500/80 font-medium tracking-widest lowercase mt-0.5",
                            subtitleSizeClasses[size],
                            variant === "vertical" ? "text-center" : "text-right"
                        )}>
                            rays into ways
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

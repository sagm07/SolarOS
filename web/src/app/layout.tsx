import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";
import { clsx } from "clsx";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const playfair = Playfair_Display({ subsets: ["latin"], variable: "--font-playfair" });

export const metadata: Metadata = {
  title: "SolarOS - The Future of Sustainable Infrastructure",
  description: "AI-powered autonomous decision engine for renewable energy optimization.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={clsx(inter.variable, playfair.variable, "font-sans antialiased selection:bg-emerald-500/30 selection:text-emerald-200")}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

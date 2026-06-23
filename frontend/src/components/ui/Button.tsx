import React from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({ variant = "primary", className, ...props }: ButtonProps) {
  const base = "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none";
  const variants: Record<Variant, string> = {
    primary: "bg-white text-black hover:bg-white/90",
    secondary: "bg-card border border-border text-foreground hover:bg-[#202020] hover:border-[#3a3a3a]",
    ghost: "bg-transparent text-muted hover:text-foreground hover:bg-card",
  };
  return <button className={cn(base, variants[variant], className)} {...props} />;
}

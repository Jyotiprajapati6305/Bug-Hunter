import React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "glass-card p-6 transition-all duration-200 hover:border-[#3a3a3a]",
        className
      )}
      {...props}
    />
  );
}

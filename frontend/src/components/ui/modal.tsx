"use client";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { HTMLAttributes, useEffect } from "react";

interface ModalProps extends HTMLAttributes<HTMLDivElement> {
  open: boolean;
  onClose: () => void;
  title: string;
}

export function Modal({ open, onClose, title, children, className }: ModalProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/60" onClick={onClose} />
      <div className={cn("relative z-10 w-full max-w-lg border border-neutral-200 bg-white p-6 shadow-2xl dark:border-neutral-800 dark:bg-neutral-900", className)}>
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xs font-medium uppercase tracking-widest text-neutral-500">{title}</h2>
          <button onClick={onClose} className="text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

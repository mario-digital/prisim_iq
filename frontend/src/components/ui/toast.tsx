'use client';

import type { FC } from 'react';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info';

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose: () => void;
}

const Toast: FC<ToastProps> = ({ message, type = 'info', duration = 3000, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <Info className="h-5 w-5 text-blue-500" />,
  };

  const styles = {
    success: 'border-green-500/20 bg-green-500/10',
    error: 'border-red-500/20 bg-red-500/10',
    info: 'border-blue-500/20 bg-blue-500/10',
  };

  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 z-50 flex items-center gap-3 rounded-lg border px-4 py-3 shadow-lg backdrop-blur-sm animate-in slide-in-from-bottom-5 fade-in duration-300',
        styles[type]
      )}
      role="alert"
    >
      {icons[type]}
      <p className="text-sm font-medium text-foreground">{message}</p>
      <button
        onClick={onClose}
        className="ml-2 rounded-full p-1 hover:bg-foreground/10 transition-colors"
        aria-label="Close notification"
      >
        <X className="h-4 w-4 text-muted-foreground" />
      </button>
    </div>
  );
};

// Simple toast manager hook
interface ToastState {
  message: string;
  type: ToastType;
  id: number;
}

let toastId = 0;
const listeners: Set<(toast: ToastState | null) => void> = new Set();
let currentToast: ToastState | null = null;

function notify(toast: ToastState | null) {
  currentToast = toast;
  listeners.forEach((listener) => listener(toast));
}

export const toast = {
  success: (message: string) => {
    notify({ message, type: 'success', id: ++toastId });
  },
  error: (message: string) => {
    notify({ message, type: 'error', id: ++toastId });
  },
  info: (message: string) => {
    notify({ message, type: 'info', id: ++toastId });
  },
};

export const ToastContainer: FC = () => {
  const [toastState, setToastState] = useState<ToastState | null>(null);

  useEffect(() => {
    listeners.add(setToastState);
    return () => {
      listeners.delete(setToastState);
    };
  }, []);

  if (!toastState) return null;

  return (
    <Toast
      key={toastState.id}
      message={toastState.message}
      type={toastState.type}
      onClose={() => setToastState(null)}
    />
  );
};


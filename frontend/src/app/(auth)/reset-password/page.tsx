"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api-client";
import { Layers, Loader2, Sparkles, CheckCircle2 } from "lucide-react";

function ResetPasswordForm() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("loading");
    setMessage("");

    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      setStatus("error");
      return;
    }

    if (!token) {
      setMessage("Invalid or missing reset token.");
      setStatus("error");
      return;
    }

    try {
      const response = await apiClient.post("/auth/reset-password", { 
        token, 
        new_password: password 
      });
      setMessage(response.message || "Password reset successfully.");
      setStatus("success");
    } catch (err: any) {
      setMessage(err.message || "Failed to reset password. The link may have expired.");
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className="space-y-6 text-center animate-in fade-in zoom-in-95">
        <div className="flex justify-center">
          <CheckCircle2 className="h-12 w-12 text-emerald-500" />
        </div>
        <p className="text-foreground font-medium">{message}</p>
        <Link href="/login" className="block">
          <Button className="w-full h-12 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold shadow-md transition-all">
            Proceed to Login
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {status === "error" && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm p-4 rounded-xl flex items-start gap-3 animate-in fade-in zoom-in-95">
          <span className="flex-1">{message}</span>
        </div>
      )}
      
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="password" className="text-foreground/80 font-semibold ml-1">New Password</Label>
          <Input 
            id="password" 
            type="password" 
            placeholder="••••••••" 
            required 
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-12 px-4 rounded-xl bg-white/50 dark:bg-black/20 border-slate-200 dark:border-white/10 focus-visible:ring-indigo-500 focus-visible:border-indigo-500 transition-all shadow-sm"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-foreground/80 font-semibold ml-1">Confirm New Password</Label>
          <Input 
            id="confirmPassword" 
            type="password" 
            placeholder="••••••••" 
            required 
            minLength={8}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="h-12 px-4 rounded-xl bg-white/50 dark:bg-black/20 border-slate-200 dark:border-white/10 focus-visible:ring-indigo-500 focus-visible:border-indigo-500 transition-all shadow-sm"
          />
        </div>
      </div>

      <Button 
        type="submit" 
        className="w-full h-12 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white font-semibold text-base shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all" 
        disabled={status === "loading" || !token}
      >
        {status === "loading" ? (
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Resetting...</span>
          </div>
        ) : (
          <span>Reset Password</span>
        )}
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-background selection:bg-primary/30">
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-500/20 blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-500/20 blur-[150px] animate-pulse" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 bg-grid bg-[size:40px_40px] opacity-[0.03] dark:opacity-[0.05]" />
      </div>

      <div className="w-full max-w-md px-4 z-10 relative">
        <div className="mb-8 flex flex-col items-center justify-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-violet-500 to-fuchsia-500 text-white shadow-[0_0_30px_rgba(99,102,241,0.5)]">
            <Layers className="h-8 w-8" />
          </div>
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-black tracking-tight text-foreground">
              Create New Password
            </h1>
            <p className="text-muted-foreground font-medium">
              Enter your new secure password
            </p>
          </div>
        </div>

        <div className="backdrop-blur-xl bg-white/60 dark:bg-card/40 border border-white/20 dark:border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.08)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.2)] rounded-3xl p-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-150 fill-mode-both">
          <Suspense fallback={<div className="flex justify-center p-4"><Loader2 className="h-6 w-6 animate-spin text-indigo-500" /></div>}>
            <ResetPasswordForm />
          </Suspense>
        </div>
        
        <div className="mt-8 flex items-center justify-center gap-2 text-sm text-muted-foreground/60 font-medium animate-in fade-in duration-1000 delay-500 fill-mode-both">
          <Sparkles className="h-4 w-4" />
          <span>MCF Content Studio</span>
        </div>
      </div>
    </div>
  );
}

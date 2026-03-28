"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Please enter your email and password.");
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      toast.success("Signed in successfully.");
      router.push("/dashboard");
    } catch {
      toast.error("Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="animate-scale-in">
      <div className="flex items-center justify-center gap-3 mb-8">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent-primary/20">
          <Shield className="w-5 h-5 text-accent-primary" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-text-inverse tracking-tight">
            Velora TPRM
          </h1>
          <p className="text-xs text-text-inverse-muted">
            Third-Party Risk Management
          </p>
        </div>
      </div>

      <Card className="border-0 shadow-2xl">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-xl">Sign in</CardTitle>
          <CardDescription>
            Enter your credentials to access the platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label
                htmlFor="email"
                className="text-sm font-medium text-text-primary"
              >
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                autoFocus
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="password"
                className="text-sm font-medium text-text-primary"
              >
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign in"
              )}
            </Button>
          </form>
          {process.env.NODE_ENV === "development" && (
            <div className="mt-6 p-3 rounded-lg bg-surface-main border border-surface-card-border">
              <p className="text-xs font-medium text-text-muted mb-2">
                Test credentials
              </p>
              <div className="space-y-1">
                <p className="text-xs text-text-muted">
                  <span className="font-medium">Admin:</span>{" "}devam@velora.io / devam123
                </p>
                <p className="text-xs text-text-muted">
                  <span className="font-medium">Manager:</span>{" "}manager@velora.io / manager123
                </p>
                <p className="text-xs text-text-muted">
                  <span className="font-medium">Viewer:</span>{" "}viewer@velora.io / viewer123
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

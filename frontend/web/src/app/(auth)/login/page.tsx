"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Shield,
  Loader2,
  ArrowRight,
  Building2,
  KeyRound,
  Lock,
  Mail,
  Globe,
} from "lucide-react";
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

type LoginStep = "tenant" | "credentials";

const SSO_PROVIDERS = [
  { id: "okta", label: "Okta", icon: Globe },
  { id: "azure", label: "Microsoft Azure AD", icon: Globe },
  { id: "google", label: "Google Workspace", icon: Globe },
] as const;

const TEST_TENANTS = [
  { id: "velora-demo", name: "Velora Demo Corp" },
  { id: "acme-corp", name: "Acme Corporation" },
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [step, setStep] = useState<LoginStep>("tenant");
  const [clientId, setClientId] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [ssoLoading, setSsoLoading] = useState<string | null>(null);

  function handleTenantSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!clientId.trim()) {
      toast.error("Please enter your Client ID.");
      return;
    }

    const matched = TEST_TENANTS.find((t) => t.id === clientId.trim().toLowerCase());
    if (matched) {
      setTenantName(matched.name);
    } else {
      setTenantName(clientId.trim());
    }
    setStep("credentials");
  }

  async function handleLogin(e: React.FormEvent) {
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

  async function handleSso(providerId: string) {
    setSsoLoading(providerId);
    toast.info(`Redirecting to ${providerId} SSO...`);
    // In production, this redirects to /auth/sso/{provider}?tenant_id={clientId}
    setTimeout(() => {
      setSsoLoading(null);
      toast.error("SSO is configured in your admin settings. Contact your administrator.");
    }, 2000);
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-[480px] xl:w-[560px] flex-col justify-between bg-gradient-to-br from-navy-700 via-navy-800 to-navy-950 p-12 relative overflow-hidden">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-accent-primary/5 blur-3xl" />
          <div className="absolute bottom-0 -left-24 w-80 h-80 rounded-full bg-accent-info/5 blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full border border-white/[0.03]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full border border-white/[0.03]" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-accent-primary/20 animate-glow">
              <Shield className="w-6 h-6 text-accent-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                Velora TPRM
              </h1>
              <p className="text-xs text-white/50">
                Third-Party Risk Management
              </p>
            </div>
          </div>

          <div className="space-y-6">
            <h2 className="text-3xl xl:text-4xl font-bold text-white leading-tight tracking-tight">
              Manage vendor risk
              <br />
              <span className="velora-gradient-text">with intelligence.</span>
            </h2>
            <p className="text-base text-white/60 leading-relaxed max-w-md">
              AI-native platform that unifies vendor assessment, continuous monitoring,
              and compliance — reducing cycle time from weeks to hours.
            </p>
          </div>
        </div>

        <div className="relative z-10 space-y-4">
          <div className="flex items-center gap-4">
            {[
              { value: "10x", label: "Faster assessments" },
              { value: "70%+", label: "AI automation" },
              { value: "8", label: "Frameworks" },
            ].map((stat) => (
              <div key={stat.label} className="flex-1 p-4 rounded-xl bg-white/[0.04] border border-white/[0.06] backdrop-blur-sm">
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-xs text-white/50 mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-white/30">
            Trusted by security teams worldwide
          </p>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-8 bg-surface-main">
        <div className="w-full max-w-[420px] animate-scale-in">
          {/* Mobile logo */}
          <div className="flex items-center justify-center gap-3 mb-8 lg:hidden">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent-primary/10">
              <Shield className="w-5 h-5 text-accent-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-text-primary tracking-tight">
                Velora TPRM
              </h1>
              <p className="text-xs text-text-muted">
                Third-Party Risk Management
              </p>
            </div>
          </div>

          {step === "tenant" && (
            <Card className="border-0 shadow-2xl velora-card-hover">
              <CardHeader className="text-center pb-2">
                <div className="mx-auto mb-3 flex items-center justify-center w-12 h-12 rounded-2xl bg-accent-primary/10">
                  <Building2 className="w-6 h-6 text-accent-primary" />
                </div>
                <CardTitle className="text-xl">Welcome back</CardTitle>
                <CardDescription>
                  Enter your organization&apos;s Client ID to continue
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleTenantSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <label
                      htmlFor="clientId"
                      className="text-sm font-medium text-text-primary"
                    >
                      Client ID
                    </label>
                    <div className="relative">
                      <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                      <Input
                        id="clientId"
                        type="text"
                        placeholder="e.g., acme-corp"
                        value={clientId}
                        onChange={(e) => setClientId(e.target.value)}
                        className="pl-10"
                        autoFocus
                      />
                    </div>
                    <p className="text-xs text-text-muted">
                      Your organization&apos;s unique identifier. Contact your admin if you don&apos;t know it.
                    </p>
                  </div>
                  <Button type="submit" className="w-full group">
                    Continue
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                  </Button>
                </form>

                {process.env.NODE_ENV === "development" && (
                  <div className="mt-6 p-3 rounded-lg bg-surface-main border border-surface-card-border">
                    <p className="text-xs font-medium text-text-muted mb-2">
                      Test Client IDs
                    </p>
                    <div className="space-y-1">
                      {TEST_TENANTS.map((t) => (
                        <button
                          key={t.id}
                          onClick={() => {
                            setClientId(t.id);
                            setTenantName(t.name);
                            setStep("credentials");
                          }}
                          className="flex items-center gap-2 w-full text-left text-xs text-text-muted hover:text-accent-primary transition-colors py-0.5"
                        >
                          <Building2 className="w-3 h-3" />
                          <span className="font-medium">{t.name}</span>
                          <span className="text-text-muted/60">({t.id})</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {step === "credentials" && (
            <div className="space-y-4">
              {/* Tenant badge */}
              <button
                onClick={() => setStep("tenant")}
                className="flex items-center gap-2 text-sm text-text-muted hover:text-text-primary transition-colors group"
              >
                <ArrowRight className="w-3.5 h-3.5 rotate-180 transition-transform group-hover:-translate-x-0.5" />
                <Building2 className="w-3.5 h-3.5" />
                <span className="font-medium">{tenantName}</span>
              </button>

              <Card className="border-0 shadow-2xl">
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-xl">Sign in</CardTitle>
                  <CardDescription>
                    Choose your authentication method
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-5">
                  {/* SSO Options */}
                  <div className="space-y-2">
                    {SSO_PROVIDERS.map((provider) => (
                      <Button
                        key={provider.id}
                        variant="outline"
                        className="w-full justify-start gap-3 h-11"
                        onClick={() => handleSso(provider.id)}
                        disabled={ssoLoading !== null}
                      >
                        {ssoLoading === provider.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <provider.icon className="w-4 h-4 text-text-muted" />
                        )}
                        Continue with {provider.label}
                      </Button>
                    ))}
                  </div>

                  {/* Divider */}
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-surface-card-border" />
                    </div>
                    <div className="relative flex justify-center text-xs">
                      <span className="bg-surface-card px-3 text-text-muted">
                        or sign in with email
                      </span>
                    </div>
                  </div>

                  {/* Email/Password form */}
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                      <label
                        htmlFor="email"
                        className="text-sm font-medium text-text-primary"
                      >
                        Email
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="you@company.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          autoComplete="email"
                          className="pl-10"
                          autoFocus
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <label
                          htmlFor="password"
                          className="text-sm font-medium text-text-primary"
                        >
                          Password
                        </label>
                        <button
                          type="button"
                          className="text-xs text-accent-primary hover:text-accent-hover transition-colors"
                        >
                          Forgot password?
                        </button>
                      </div>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                        <Input
                          id="password"
                          type="password"
                          placeholder="Enter your password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          autoComplete="current-password"
                          className="pl-10"
                        />
                      </div>
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
                    <div className="p-3 rounded-lg bg-surface-main border border-surface-card-border">
                      <p className="text-xs font-medium text-text-muted mb-2">
                        Test credentials
                      </p>
                      <div className="space-y-1">
                        <button
                          onClick={() => {
                            setEmail("admin@velora-demo.com");
                            setPassword("admin123");
                          }}
                          className="flex items-center gap-2 text-xs text-text-muted hover:text-accent-primary transition-colors"
                        >
                          <span className="font-medium">Admin:</span>
                          admin@velora-demo.com / admin123
                        </button>
                        <button
                          onClick={() => {
                            setEmail("analyst@velora-demo.com");
                            setPassword("analyst123");
                          }}
                          className="flex items-center gap-2 text-xs text-text-muted hover:text-accent-primary transition-colors"
                        >
                          <span className="font-medium">Analyst:</span>
                          analyst@velora-demo.com / analyst123
                        </button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <p className="text-center text-xs text-text-muted">
                Protected by enterprise-grade encryption.{" "}
                <button className="text-accent-primary hover:text-accent-hover transition-colors">
                  Privacy Policy
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft, Shield, Sun, Moon, Monitor } from "lucide-react";
import { cn } from "@/lib/utils";
import { navigation } from "@/lib/navigation";
import { useTheme, type Theme } from "@/providers/theme-provider";

const themeOptions: { value: Theme; icon: typeof Sun; label: string }[] = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-surface-sidebar border-r border-navy-800/50 transition-all duration-300 ease-out",
        collapsed ? "w-[68px]" : "w-[260px]"
      )}
    >
      <SidebarHeader collapsed={collapsed} />
      <nav className="flex-1 overflow-y-auto px-3 py-2">
        {navigation.map((section) => (
          <SidebarSection
            key={section.title}
            section={section}
            pathname={pathname}
            collapsed={collapsed}
          />
        ))}
      </nav>
      <ThemeToggle collapsed={collapsed} />
      <SidebarFooter collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
    </aside>
  );
}

function SidebarHeader({ collapsed }: { collapsed: boolean }) {
  return (
    <div className="flex items-center gap-3 px-4 py-5 border-b border-white/[0.06]">
      <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/20 shrink-0">
        <Shield className="w-4.5 h-4.5 text-accent-primary" />
      </div>
      {!collapsed && (
        <div className="animate-fade-in">
          <p className="text-sm font-semibold text-text-inverse tracking-tight">
            Velora TPRM
          </p>
          <p className="text-[11px] text-text-inverse-muted">
            Third-Party Risk
          </p>
        </div>
      )}
    </div>
  );
}

function SidebarSection({
  section,
  pathname,
  collapsed,
}: {
  section: (typeof navigation)[number];
  pathname: string;
  collapsed: boolean;
}) {
  return (
    <div className="mb-2">
      {!collapsed && (
        <p className="px-3 py-2 text-[11px] font-semibold text-text-inverse-muted/60 uppercase tracking-wider">
          {section.title}
        </p>
      )}
      {collapsed && <div className="h-2" />}
      {section.items.map((item) => {
        const isActive =
          pathname === item.href ||
          (item.href !== "/dashboard" && pathname.startsWith(item.href + "/"));
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150",
              isActive
                ? "bg-accent-primary/15 text-text-inverse border-l-2 border-accent-primary ml-0.5"
                : "text-text-inverse-muted hover:bg-white/[0.06] hover:text-text-inverse",
              collapsed && "justify-center px-2 border-l-0 ml-0"
            )}
          >
            <Icon className={cn("w-4 h-4 shrink-0", isActive && "text-accent-primary")} />
            {!collapsed && (
              <span className="animate-fade-in truncate">{item.label}</span>
            )}
          </Link>
        );
      })}
    </div>
  );
}

function ThemeToggle({ collapsed }: { collapsed: boolean }) {
  const { theme, setTheme } = useTheme();

  if (collapsed) {
    const current = themeOptions.find((t) => t.value === theme) || themeOptions[2];
    const CurrentIcon = current.icon;
    const nextIndex = (themeOptions.findIndex((t) => t.value === theme) + 1) % themeOptions.length;

    return (
      <div className="px-3 py-2">
        <button
          onClick={() => setTheme(themeOptions[nextIndex].value)}
          className="flex items-center justify-center w-full rounded-lg px-2 py-2 text-text-inverse-muted hover:text-text-inverse hover:bg-white/[0.06] transition-all duration-150"
          title={`Theme: ${current.label}`}
        >
          <CurrentIcon className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="px-3 py-2">
      <p className="px-3 py-1 text-[11px] font-semibold text-text-inverse-muted/60 uppercase tracking-wider">
        Theme
      </p>
      <div className="flex items-center gap-1 p-1 rounded-lg bg-white/[0.04]">
        {themeOptions.map((option) => {
          const Icon = option.icon;
          const isActive = theme === option.value;

          return (
            <button
              key={option.value}
              onClick={() => setTheme(option.value)}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-all duration-150",
                isActive
                  ? "bg-accent-primary/20 text-accent-primary"
                  : "text-text-inverse-muted hover:text-text-inverse"
              )}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="animate-fade-in">{option.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function SidebarFooter({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="border-t border-white/[0.06] px-3 py-3">
      <button
        onClick={onToggle}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-text-inverse-muted hover:text-text-inverse hover:bg-white/[0.06] transition-all duration-150 w-full",
          collapsed && "justify-center px-2"
        )}
      >
        <ChevronLeft
          className={cn(
            "w-4 h-4 transition-transform duration-200",
            collapsed && "rotate-180"
          )}
        />
        {!collapsed && <span className="animate-fade-in">Collapse</span>}
      </button>
    </div>
  );
}

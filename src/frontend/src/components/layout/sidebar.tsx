"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { navigation } from "@/lib/navigation";

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-surface-sidebar border-r border-navy-800 transition-all duration-200 ease-out",
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
      <SidebarFooter collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
    </aside>
  );
}

function SidebarHeader({ collapsed }: { collapsed: boolean }) {
  return (
    <div className="flex items-center gap-3 px-4 py-5 border-b border-navy-800/50">
      <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/20">
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
        <p className="px-3 py-2 text-[11px] font-semibold text-text-inverse-muted uppercase tracking-wider">
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
                ? "bg-surface-sidebar-active text-text-inverse"
                : "text-text-inverse-muted hover:bg-surface-sidebar-hover hover:text-text-inverse",
              collapsed && "justify-center px-2"
            )}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {!collapsed && (
              <span className="animate-fade-in truncate">{item.label}</span>
            )}
          </Link>
        );
      })}
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
    <div className="border-t border-navy-800/50 px-3 py-3">
      <button
        onClick={onToggle}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-text-inverse-muted hover:text-text-inverse hover:bg-surface-sidebar-hover transition-all duration-150 w-full",
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

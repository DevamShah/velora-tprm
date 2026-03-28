"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Bell, ChevronRight, Command, LogOut, Settings, User, ExternalLink } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useNotifications, useMarkRead, useMarkAllRead } from "@/hooks/use-communications";
import { findBreadcrumbs } from "@/lib/navigation";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface HeaderProps {
  onCommandPaletteOpen: () => void;
}

export function Header({ onCommandPaletteOpen }: HeaderProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const breadcrumbs = findBreadcrumbs(pathname);

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  return (
    <header className="flex items-center justify-between h-14 px-6 bg-surface-header border-b border-surface-card-border">
      <Breadcrumbs items={breadcrumbs} />
      <div className="flex items-center gap-2">
        <SearchButton onClick={onCommandPaletteOpen} />
        <NotificationBell />
        <UserMenu initials={initials} userName={user?.name} onLogout={logout} />
      </div>
    </header>
  );
}

function Breadcrumbs({
  items,
}: {
  items: { label: string; href: string }[];
}) {
  return (
    <nav className="flex items-center gap-1 text-sm">
      <Link
        href="/dashboard"
        className="text-text-muted hover:text-text-primary transition-colors"
      >
        Home
      </Link>
      {items.map((item, index) => (
        <React.Fragment key={item.href}>
          <ChevronRight className="w-3.5 h-3.5 text-text-muted" />
          {index === items.length - 1 ? (
            <span className="font-medium text-text-primary">{item.label}</span>
          ) : (
            <Link
              href={item.href}
              className="text-text-muted hover:text-text-primary transition-colors"
            >
              {item.label}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}

function SearchButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 h-8 px-3 rounded-lg border border-surface-card-border text-text-muted text-sm hover:bg-surface-main transition-colors"
    >
      <Command className="w-3.5 h-3.5" />
      <span className="hidden sm:inline">Search...</span>
      <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded border border-surface-card-border bg-surface-main px-1.5 py-0.5 text-[10px] font-medium text-text-muted">
        <span className="text-xs">&#8984;</span>K
      </kbd>
    </button>
  );
}

function NotificationBell() {
  const router = useRouter();
  const { notifications, unreadCount, refetch } = useNotifications();
  const { markRead } = useMarkRead();
  const { markAllRead } = useMarkAllRead();

  const recentNotifications = notifications.slice(0, 5);

  const handleMarkRead = async (id: string) => {
    try {
      await markRead(id);
      refetch();
    } catch {
      // silent
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllRead();
      refetch();
    } catch {
      // silent
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="relative flex items-center justify-center w-8 h-8 rounded-lg text-text-muted hover:bg-surface-main hover:text-text-primary transition-colors">
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-0.5 -right-0.5 h-4 min-w-[16px] flex items-center justify-center p-0 text-[10px] bg-accent-error text-white border-2 border-white rounded-full">
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <div className="flex items-center justify-between px-3 py-2">
          <DropdownMenuLabel className="p-0 text-sm font-semibold">
            Notifications
          </DropdownMenuLabel>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs px-2"
              onClick={(e) => {
                e.preventDefault();
                handleMarkAllRead();
              }}
            >
              Mark all read
            </Button>
          )}
        </div>
        <DropdownMenuSeparator />
        {recentNotifications.length === 0 ? (
          <div className="py-6 text-center text-xs text-text-muted">
            No notifications
          </div>
        ) : (
          <>
            {recentNotifications.map((notification) => (
              <DropdownMenuItem
                key={notification.id}
                className="flex items-start gap-2 px-3 py-2.5 cursor-pointer"
                onClick={() => {
                  if (!notification.is_read) {
                    handleMarkRead(notification.id);
                  }
                  if (notification.link) {
                    router.push(notification.link);
                  }
                }}
              >
                <div
                  className={cn(
                    "w-1.5 h-1.5 rounded-full mt-1.5 shrink-0",
                    notification.is_read ? "bg-transparent" : "bg-accent-primary"
                  )}
                />
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      "text-xs truncate",
                      notification.is_read
                        ? "text-text-muted"
                        : "text-text-primary font-medium"
                    )}
                  >
                    {notification.title}
                  </p>
                  <p className="text-[10px] text-text-muted mt-0.5 line-clamp-1">
                    {notification.message}
                  </p>
                </div>
              </DropdownMenuItem>
            ))}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              className="justify-center text-xs text-accent-primary cursor-pointer"
              onClick={() => router.push("/communications")}
            >
              View all notifications
              <ExternalLink className="w-3 h-3 ml-1" />
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function UserMenu({
  initials,
  userName,
  onLogout,
}: {
  initials: string;
  userName?: string;
  onLogout: () => void;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex items-center gap-2 rounded-lg p-1 hover:bg-surface-main transition-colors">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="text-xs">{initials}</AvatarFallback>
          </Avatar>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="font-normal">
          <p className="text-sm font-medium text-text-primary">
            {userName || "User"}
          </p>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/admin/settings" className="cursor-pointer">
            <User className="w-4 h-4" />
            Profile
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/admin/settings" className="cursor-pointer">
            <Settings className="w-4 h-4" />
            Settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={onLogout}
          className="text-accent-error focus:text-accent-error cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

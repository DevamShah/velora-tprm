"use client";

import React from "react";
import {
  Bell,
  Mail,
  ScrollText,
  Check,
  CheckCheck,
  Circle,
  ExternalLink,
  MessageSquare,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useNotifications,
  useMarkRead,
  useMarkAllRead,
  useEmailTemplates,
  useCommunicationLogs,
} from "@/hooks/use-communications";
import {
  NOTIFICATION_TYPE_LABELS,
  COMM_CHANNEL_LABELS,
  COMM_STATUS_LABELS,
} from "@/types/communication";
import { cn } from "@/lib/utils";

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

const PRIORITY_STYLES: Record<string, string> = {
  high: "border-l-risk-critical",
  medium: "border-l-amber-500",
  low: "border-l-surface-card-border",
};

const STATUS_STYLES: Record<string, string> = {
  sent: "bg-blue-50 text-blue-700",
  delivered: "bg-green-50 text-green-700",
  failed: "bg-red-50 text-red-700",
  pending: "bg-gray-100 text-gray-600",
};

export default function CommunicationsPage() {
  return (
    <>
      <PageHeader
        title="Communications"
        description="Manage notifications, templates, and communication logs"
      />

      <Tabs defaultValue="notifications">
        <TabsList>
          <TabsTrigger value="notifications">
            <Bell className="h-3.5 w-3.5 mr-1" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="templates">
            <Mail className="h-3.5 w-3.5 mr-1" />
            Email Templates
          </TabsTrigger>
          <TabsTrigger value="logs">
            <ScrollText className="h-3.5 w-3.5 mr-1" />
            Communication Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="notifications" className="mt-4">
          <NotificationsTab />
        </TabsContent>

        <TabsContent value="templates" className="mt-4">
          <EmailTemplatesTab />
        </TabsContent>

        <TabsContent value="logs" className="mt-4">
          <CommunicationLogsTab />
        </TabsContent>
      </Tabs>
    </>
  );
}

/* --- Notifications Tab --- */

function NotificationsTab() {
  const { notifications, unreadCount, isLoading, error, refetch } =
    useNotifications();
  const { markRead } = useMarkRead();
  const { markAllRead, isLoading: isMarkingAll } = useMarkAllRead();

  if (error) {
    toast.error(error);
  }

  const handleMarkRead = async (id: string) => {
    try {
      await markRead(id);
      refetch();
    } catch {
      toast.error("Failed to mark as read");
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllRead();
      toast.success("All notifications marked as read");
      refetch();
    } catch {
      toast.error("Failed to mark all as read");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-3 animate-fade-in">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <Card>
        <CardContent className="p-0">
          <EmptyState
            icon={Bell}
            title="No notifications"
            description="You're all caught up. Notifications will appear here."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {unreadCount > 0 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-muted">
            {unreadCount} unread notification{unreadCount !== 1 ? "s" : ""}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleMarkAllRead}
            disabled={isMarkingAll}
          >
            <CheckCheck className="w-3.5 h-3.5 mr-1" />
            Mark All Read
          </Button>
        </div>
      )}

      <div className="space-y-2">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={cn(
              "flex items-start gap-3 p-4 rounded-xl border-l-4 bg-white border border-surface-card-border transition-colors",
              notification.is_read
                ? "border-l-transparent opacity-70"
                : PRIORITY_STYLES[notification.priority] || "border-l-surface-card-border"
            )}
          >
            <div className="mt-0.5">
              {notification.is_read ? (
                <Check className="w-4 h-4 text-text-muted" />
              ) : (
                <Circle className="w-4 h-4 text-accent-primary fill-accent-primary" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <Badge variant="outline" className="text-[10px]">
                  {NOTIFICATION_TYPE_LABELS[notification.type]}
                </Badge>
                <span className="text-xs text-text-muted">
                  {timeAgo(notification.created_at)}
                </span>
              </div>
              <p
                className={cn(
                  "text-sm",
                  notification.is_read
                    ? "text-text-secondary"
                    : "text-text-primary font-medium"
                )}
              >
                {notification.title}
              </p>
              <p className="text-xs text-text-muted mt-0.5 line-clamp-2">
                {notification.message}
              </p>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {notification.link && (
                <Button variant="ghost" size="icon" className="h-7 w-7" asChild>
                  <a href={notification.link}>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </Button>
              )}
              {!notification.is_read && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => handleMarkRead(notification.id)}
                >
                  <Check className="w-3.5 h-3.5" />
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* --- Email Templates Tab --- */

function EmailTemplatesTab() {
  const { templates, isLoading, error } = useEmailTemplates();

  if (error) {
    toast.error(error);
  }

  if (isLoading) {
    return <TableLoadingSkeleton rows={4} />;
  }

  if (templates.length === 0) {
    return (
      <Card>
        <CardContent className="p-0">
          <EmptyState
            icon={Mail}
            title="No email templates"
            description="Email templates will be configured by your administrator."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead>Template Name</TableHead>
            <TableHead>Subject</TableHead>
            <TableHead className="w-[200px]">Variables</TableHead>
            <TableHead className="w-[80px]">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow key={template.id}>
              <TableCell>
                <span className="font-medium text-text-primary">
                  {template.name}
                </span>
              </TableCell>
              <TableCell className="text-text-secondary text-sm">
                {template.subject}
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {template.variables.slice(0, 3).map((v) => (
                    <Badge
                      key={v}
                      variant="outline"
                      className="text-[10px] font-mono"
                    >
                      {`{{${v}}}`}
                    </Badge>
                  ))}
                  {template.variables.length > 3 && (
                    <Badge variant="secondary" className="text-[10px]">
                      +{template.variables.length - 3}
                    </Badge>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <Badge variant={template.is_active ? "default" : "secondary"}>
                  {template.is_active ? "Active" : "Inactive"}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

/* --- Communication Logs Tab --- */

function CommunicationLogsTab() {
  const { logs, isLoading, error } = useCommunicationLogs();

  if (error) {
    toast.error(error);
  }

  if (isLoading) {
    return <TableLoadingSkeleton rows={5} />;
  }

  if (logs.length === 0) {
    return (
      <Card>
        <CardContent className="p-0">
          <EmptyState
            icon={MessageSquare}
            title="No communication logs"
            description="Communication history will appear here as messages are sent."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-[100px]">Channel</TableHead>
            <TableHead>Recipient</TableHead>
            <TableHead>Subject</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[160px]">Sent</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow key={log.id}>
              <TableCell>
                <Badge variant="outline" className="text-xs">
                  {COMM_CHANNEL_LABELS[log.channel] || log.channel}
                </Badge>
              </TableCell>
              <TableCell className="text-text-primary text-sm font-medium">
                {log.recipient}
              </TableCell>
              <TableCell className="text-text-secondary text-sm">
                {log.subject || "--"}
              </TableCell>
              <TableCell>
                <span
                  className={cn(
                    "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                    STATUS_STYLES[log.status] || "bg-gray-100 text-gray-600"
                  )}
                >
                  {COMM_STATUS_LABELS[log.status] || log.status}
                </span>
              </TableCell>
              <TableCell className="text-text-muted text-sm">
                {formatDate(log.sent_at)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

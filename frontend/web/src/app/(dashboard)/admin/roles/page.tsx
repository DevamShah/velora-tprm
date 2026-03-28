"use client";

import React, { useState } from "react";
import { Lock, Plus, Shield, Users, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-state";
import { useRoles, useCreateRole } from "@/hooks/use-admin";
import { DEFAULT_PERMISSIONS } from "@/types/admin";
import type { CreateRolePayload } from "@/types/admin";
import { cn } from "@/lib/utils";

export default function RolesPage() {
  const { roles, isLoading, error, refetch } = useRoles();
  const { createRole, isLoading: isCreating } = useCreateRole();
  const [createOpen, setCreateOpen] = useState(false);
  const [newRole, setNewRole] = useState<CreateRolePayload>({
    name: "",
    description: "",
    permissions: [],
  });

  if (error) {
    toast.error(error);
  }

  const handleCreate = async () => {
    if (!newRole.name) {
      toast.error("Role name is required");
      return;
    }
    if (newRole.permissions.length === 0) {
      toast.error("Select at least one permission");
      return;
    }
    try {
      await createRole(newRole);
      toast.success("Role created");
      setCreateOpen(false);
      setNewRole({ name: "", description: "", permissions: [] });
      refetch();
    } catch {
      toast.error("Failed to create role");
    }
  };

  const togglePermission = (perm: string) => {
    setNewRole((prev) => ({
      ...prev,
      permissions: prev.permissions.includes(perm)
        ? prev.permissions.filter((p) => p !== perm)
        : [...prev.permissions, perm],
    }));
  };

  if (isLoading) {
    return (
      <>
        <PageHeader
          title="Roles"
          description="Configure role-based access control"
        />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 animate-fade-in">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-40 rounded-xl" />
          ))}
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Roles"
        description="Configure role-based access control"
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Create Role
          </Button>
        }
      />

      {roles.length === 0 ? (
        <EmptyState
          icon={Lock}
          title="No roles configured"
          description="Create roles to manage access control."
          actionLabel="Create Role"
          onAction={() => setCreateOpen(true)}
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {roles.map((role) => (
            <Card key={role.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/10">
                      <Shield className="w-4 h-4 text-accent-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-text-primary">
                        {role.name}
                      </p>
                      {role.is_system && (
                        <Badge
                          variant="secondary"
                          className="text-[10px] mt-0.5"
                        >
                          System
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-text-muted">
                    <Users className="w-3.5 h-3.5" />
                    {role.user_count}
                  </div>
                </div>
                {role.description && (
                  <p className="text-xs text-text-muted mb-3 line-clamp-2">
                    {role.description}
                  </p>
                )}
                <div className="flex flex-wrap gap-1">
                  {role.permissions.slice(0, 4).map((perm) => (
                    <Badge
                      key={perm}
                      variant="outline"
                      className="text-[10px]"
                    >
                      {perm}
                    </Badge>
                  ))}
                  {role.permissions.length > 4 && (
                    <Badge variant="secondary" className="text-[10px]">
                      +{role.permissions.length - 4} more
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Role Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="sm:max-w-lg max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Role</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Role Name
              </label>
              <Input
                placeholder="e.g., Vendor Manager"
                value={newRole.name}
                onChange={(e) =>
                  setNewRole((prev) => ({ ...prev, name: e.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Description (optional)
              </label>
              <Input
                placeholder="What this role is for"
                value={newRole.description || ""}
                onChange={(e) =>
                  setNewRole((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Permissions
              </label>
              <div className="rounded-lg border border-surface-card-border p-3 max-h-48 overflow-y-auto">
                <div className="grid grid-cols-2 gap-2">
                  {DEFAULT_PERMISSIONS.map((perm) => (
                    <label
                      key={perm}
                      className={cn(
                        "flex items-center gap-2 px-2 py-1.5 rounded-md text-xs cursor-pointer transition-colors",
                        newRole.permissions.includes(perm)
                          ? "bg-accent-primary/10 text-accent-primary"
                          : "hover:bg-surface-main text-text-secondary"
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={newRole.permissions.includes(perm)}
                        onChange={() => togglePermission(perm)}
                        className="rounded border-surface-card-border"
                      />
                      {perm}
                    </label>
                  ))}
                </div>
              </div>
              <p className="text-xs text-text-muted">
                {newRole.permissions.length} permission
                {newRole.permissions.length !== 1 ? "s" : ""} selected
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateOpen(false)}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={
                isCreating ||
                !newRole.name ||
                newRole.permissions.length === 0
              }
            >
              {isCreating && (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              )}
              Create Role
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

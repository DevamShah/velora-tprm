"use client";

import React, { useState } from "react";
import {
  Users,
  Plus,
  MoreHorizontal,
  Pencil,
  UserX,
  Shield,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import {
  useUsers,
  useCreateUser,
  useUpdateUser,
  useDeactivateUser,
} from "@/hooks/use-admin";
import { USER_STATUS_LABELS } from "@/types/admin";
import type { AdminUser, CreateUserPayload, UserStatus } from "@/types/admin";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "Never";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const STATUS_STYLES: Record<UserStatus, string> = {
  active: "bg-green-50 text-green-700",
  inactive: "bg-gray-100 text-gray-600",
  invited: "bg-blue-50 text-blue-700",
  suspended: "bg-red-50 text-red-700",
};

export default function UsersPage() {
  const { users, isLoading, error, refetch } = useUsers();
  const { createUser, isLoading: isCreating } = useCreateUser();
  const { updateUser, isLoading: isUpdating } = useUpdateUser();
  const { deactivateUser, isLoading: isDeactivating } = useDeactivateUser();

  const [inviteOpen, setInviteOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<AdminUser | null>(null);
  const [deactivateTarget, setDeactivateTarget] = useState<AdminUser | null>(
    null
  );

  // Invite form state
  const [inviteData, setInviteData] = useState<CreateUserPayload>({
    email: "",
    name: "",
    roles: [],
  });

  // Edit form state
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");

  if (error) {
    toast.error(error);
  }

  const handleInvite = async () => {
    if (!inviteData.email || !inviteData.name) {
      toast.error("Name and email are required");
      return;
    }
    try {
      await createUser(inviteData);
      toast.success("User invited successfully");
      setInviteOpen(false);
      setInviteData({ email: "", name: "", roles: [] });
      refetch();
    } catch {
      toast.error("Failed to invite user");
    }
  };

  const handleEdit = async () => {
    if (!editTarget) return;
    try {
      await updateUser(editTarget.id, { name: editName, email: editEmail });
      toast.success("User updated");
      setEditTarget(null);
      refetch();
    } catch {
      toast.error("Failed to update user");
    }
  };

  const handleDeactivate = async () => {
    if (!deactivateTarget) return;
    try {
      await deactivateUser(deactivateTarget.id);
      toast.success("User deactivated");
      setDeactivateTarget(null);
      refetch();
    } catch {
      toast.error("Failed to deactivate user");
    }
  };

  const openEdit = (user: AdminUser) => {
    setEditName(user.name);
    setEditEmail(user.email);
    setEditTarget(user);
  };

  return (
    <>
      <PageHeader
        title="Users"
        description="Manage platform users and invitations"
        actions={
          <Button onClick={() => setInviteOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Invite User
          </Button>
        }
      />

      <div className="space-y-4">
        {isLoading ? (
          <TableLoadingSkeleton rows={5} />
        ) : users.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No additional users"
            description="Invite team members to collaborate on risk management."
            actionLabel="Invite User"
            onAction={() => setInviteOpen(true)}
          />
        ) : (
          <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead className="w-[150px]">Roles</TableHead>
                  <TableHead className="w-[100px]">Status</TableHead>
                  <TableHead className="w-[120px]">Last Login</TableHead>
                  <TableHead className="w-[50px]" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <span className="font-medium text-text-primary">
                        {user.name}
                      </span>
                    </TableCell>
                    <TableCell className="text-text-secondary text-sm">
                      {user.email}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map((role) => (
                          <Badge
                            key={role}
                            variant="outline"
                            className="text-[10px]"
                          >
                            <Shield className="w-2.5 h-2.5 mr-0.5" />
                            {role}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                          STATUS_STYLES[user.status]
                        }`}
                      >
                        {USER_STATUS_LABELS[user.status]}
                      </span>
                    </TableCell>
                    <TableCell className="text-text-muted text-sm">
                      {formatDate(user.last_login)}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => openEdit(user)}>
                            <Pencil className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          {user.status === "active" && (
                            <DropdownMenuItem
                              onClick={() => setDeactivateTarget(user)}
                              className="text-accent-error focus:text-accent-error"
                            >
                              <UserX className="h-4 w-4 mr-2" />
                              Deactivate
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Invite User Dialog */}
      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Invite User</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Full Name
              </label>
              <Input
                placeholder="Jane Doe"
                value={inviteData.name}
                onChange={(e) =>
                  setInviteData((prev) => ({ ...prev, name: e.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Email
              </label>
              <Input
                type="email"
                placeholder="jane@company.com"
                value={inviteData.email}
                onChange={(e) =>
                  setInviteData((prev) => ({ ...prev, email: e.target.value }))
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setInviteOpen(false)}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleInvite}
              disabled={isCreating || !inviteData.email || !inviteData.name}
            >
              {isCreating && (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              )}
              Send Invite
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={!!editTarget}
        onOpenChange={(v) => {
          if (!v) setEditTarget(null);
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Full Name
              </label>
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-primary">
                Email
              </label>
              <Input
                type="email"
                value={editEmail}
                onChange={(e) => setEditEmail(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setEditTarget(null)}
              disabled={isUpdating}
            >
              Cancel
            </Button>
            <Button onClick={handleEdit} disabled={isUpdating}>
              {isUpdating && (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              )}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Deactivate Confirmation Dialog */}
      <Dialog
        open={!!deactivateTarget}
        onOpenChange={(v) => {
          if (!v) setDeactivateTarget(null);
        }}
      >
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Deactivate User</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-text-secondary">
            Are you sure you want to deactivate{" "}
            <span className="font-semibold">{deactivateTarget?.name}</span>?
            They will lose access to the platform.
          </p>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeactivateTarget(null)}
              disabled={isDeactivating}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeactivate}
              disabled={isDeactivating}
            >
              {isDeactivating && (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              )}
              Deactivate
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

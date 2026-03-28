"use client";

import React, { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft,
  Pencil,
  Trash2,
  Calculator,
  Globe,
  Building2,
  MapPin,
  Users,
  DollarSign,
  Calendar,
  Shield,
  UserPlus,
  Clock,
  Star,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { PageLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
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
import { Skeleton } from "@/components/ui/skeleton";
import { VendorTierBadge } from "@/components/vendors/vendor-tier-badge";
import { VendorStatusBadge } from "@/components/vendors/vendor-status-badge";
import { VendorRiskScore } from "@/components/vendors/vendor-risk-score";
import { DeleteVendorDialog } from "@/components/vendors/delete-vendor-dialog";
import { EditVendorDialog } from "@/components/vendors/edit-vendor-dialog";
import { AddContactDialog } from "@/components/vendors/add-contact-dialog";
import { useVendor, useCalculateTier, useUpdateContact } from "@/hooks/use-vendors";
import { useVendorScore, useScoreHistory, useCalculateScore } from "@/hooks/use-scoring";
import { ScoreGauge } from "@/components/scoring/score-gauge";
import { DimensionChart } from "@/components/scoring/dimension-chart";
import { ScoreTrend } from "@/components/scoring/score-trend";
import { VendorTimeline } from "@/components/monitoring/vendor-timeline";
import type { VendorContact, CreateContactPayload } from "@/types/vendor";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return "--";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function capitalize(s: string | null): string {
  if (!s) return "--";
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function InfoRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="flex items-start gap-3 py-2">
      <Icon className="h-4 w-4 text-text-muted mt-0.5 shrink-0" />
      <div>
        <p className="text-xs text-text-muted">{label}</p>
        <p className="text-sm text-text-primary">{value}</p>
      </div>
    </div>
  );
}

export default function VendorDetailPage() {
  const router = useRouter();
  const params = useParams();
  const vendorId = params.id as string;

  const { vendor, isLoading, error, refetch } = useVendor(vendorId);
  const { calculateTier, isLoading: calcLoading } = useCalculateTier();
  const { updateContact } = useUpdateContact();

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [contactOpen, setContactOpen] = useState(false);
  const [editContact, setEditContact] = useState<VendorContact | null>(null);

  async function handleCalculateTier() {
    try {
      const res = await calculateTier(vendorId);
      toast.success(`Tier calculated: ${res.tier}`);
      refetch();
    } catch (err) {
      toast.error((err as { message?: string }).message || "Tier calculation failed");
    }
  }

  async function handleEditContact(contactId: string, data: Partial<CreateContactPayload>) {
    await updateContact(vendorId, contactId, data);
    refetch();
  }

  if (isLoading) return <PageLoadingSkeleton />;

  if (error || !vendor) {
    return (
      <EmptyState
        icon={Building2}
        title="Vendor not found"
        description={error || "The requested vendor could not be loaded."}
        actionLabel="Back to Vendors"
        onAction={() => router.push("/vendors")}
      />
    );
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4">
        <Button variant="ghost" size="sm" onClick={() => router.push("/vendors")}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Vendors
        </Button>
      </div>

      <PageHeader
        title={vendor.name}
        description={vendor.domain || vendor.industry || undefined}
        actions={
          <div className="flex items-center gap-2">
            <VendorTierBadge tier={vendor.tier} />
            <VendorStatusBadge status={vendor.status} />
            <Button variant="outline" size="sm" onClick={handleCalculateTier} disabled={calcLoading}>
              <Calculator className="h-4 w-4 mr-1" />
              {calcLoading ? "Calculating..." : "Calculate Tier"}
            </Button>
            <Button variant="outline" size="sm" onClick={() => setEditOpen(true)}>
              <Pencil className="h-4 w-4 mr-1" />
              Edit
            </Button>
            <Button variant="outline" size="sm" onClick={() => setDeleteOpen(true)} className="text-risk-critical hover:text-risk-critical">
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </Button>
          </div>
        }
      />

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="contacts">
            Contacts ({vendor.contacts?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <OverviewTab vendor={vendor} />
        </TabsContent>

        <TabsContent value="contacts">
          <ContactsTab
            contacts={vendor.contacts || []}
            onAddContact={() => { setEditContact(null); setContactOpen(true); }}
            onEditContact={(c) => { setEditContact(c); setContactOpen(true); }}
          />
        </TabsContent>

        <TabsContent value="timeline">
          <Card>
            <CardContent className="pt-6">
              <VendorTimeline vendorId={vendorId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <DeleteVendorDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        vendorId={vendor.id}
        vendorName={vendor.name}
        onDeleted={() => router.push("/vendors")}
      />

      <EditVendorDialog
        open={editOpen}
        onOpenChange={setEditOpen}
        vendor={vendor}
        onSuccess={refetch}
      />

      <AddContactDialog
        open={contactOpen}
        onOpenChange={setContactOpen}
        vendorId={vendor.id}
        onSuccess={refetch}
        editData={editContact}
        onEdit={handleEditContact}
      />
    </>
  );
}

/* --- Overview Tab --- */

function OverviewTab({ vendor }: { vendor: NonNullable<ReturnType<typeof useVendor>["vendor"]> }) {
  return (
    <div className="space-y-6">
      {/* Risk Score Section */}
      <VendorRiskScoreSection vendorId={vendor.id} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              Vendor Summary
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1">
              <InfoRow icon={Globe} label="Domain" value={vendor.domain || "--"} />
              <InfoRow icon={Building2} label="Industry" value={vendor.industry || "--"} />
              <InfoRow icon={MapPin} label="Country" value={vendor.country || "--"} />
              <InfoRow icon={Users} label="Employees" value={vendor.employee_count?.toLocaleString() || "--"} />
              <InfoRow icon={DollarSign} label="Contract Value" value={formatCurrency(vendor.contract_value)} />
              <InfoRow icon={DollarSign} label="Annual Revenue" value={formatCurrency(vendor.annual_revenue)} />
              <InfoRow icon={Calendar} label="Contract Start" value={formatDate(vendor.contract_start_date)} />
              <InfoRow icon={Calendar} label="Contract End" value={formatDate(vendor.contract_end_date)} />
            </div>
            {vendor.description && (
              <div className="mt-4 pt-4 border-t border-surface-card-border">
                <p className="text-xs text-text-muted mb-1">Description</p>
                <p className="text-sm text-text-secondary">{vendor.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Risk Scores
              </h3>
              <div className="space-y-3">
                <VendorRiskScore
                  score={vendor.inherent_risk_score}
                  label="Inherent Risk"
                  showLabel
                  size="md"
                />
                <VendorRiskScore
                  score={vendor.residual_risk_score}
                  label="Residual Risk"
                  showLabel
                  size="md"
                />
                <VendorRiskScore
                  score={vendor.external_rating_score}
                  label="External Rating"
                  showLabel
                  size="md"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Classification
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-text-muted">Data Classification</p>
                  <p className="text-sm text-text-primary mt-0.5">
                    {capitalize(vendor.data_classification)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-text-muted">Business Criticality</p>
                  <p className="text-sm text-text-primary mt-0.5">
                    {capitalize(vendor.business_criticality)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {vendor.tags && vendor.tags.length > 0 && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-3">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {vendor.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {vendor.notes && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-semibold text-text-primary mb-2">
                  Notes
                </h3>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">
                  {vendor.notes}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

/* --- Vendor Risk Score Section --- */

function VendorRiskScoreSection({ vendorId }: { vendorId: string }) {
  const { score, isLoading: scoreLoading, error: scoreError, refetch: refetchScore } = useVendorScore(vendorId);
  const { history, isLoading: historyLoading } = useScoreHistory(vendorId);
  const { calculateScore, isLoading: calcLoading } = useCalculateScore();
  const [calcError, setCalcError] = useState<string | null>(null);

  async function handleRecalculate() {
    setCalcError(null);
    try {
      await calculateScore(vendorId);
      refetchScore();
      toast.success("Risk score recalculated");
    } catch (err) {
      const msg = (err as { message?: string }).message || "Score calculation failed";
      setCalcError(msg);
      toast.error(msg);
    }
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-text-primary">
            Risk Score
          </h3>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRecalculate}
            disabled={calcLoading}
          >
            <Calculator className="h-4 w-4 mr-1" />
            {calcLoading ? "Calculating..." : "Recalculate"}
          </Button>
        </div>

        {calcError && (
          <p className="text-xs text-risk-critical mb-3">{calcError}</p>
        )}

        {scoreLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        ) : scoreError || !score ? (
          <div className="flex flex-col items-center justify-center py-8 text-text-muted text-sm">
            <Shield className="h-5 w-5 mb-2" />
            <p>No risk score calculated yet</p>
            <p className="text-xs mt-0.5">Click &quot;Recalculate&quot; to generate a score</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Score Gauge */}
            <div className="flex flex-col items-center justify-center">
              <ScoreGauge score={score.overall_score} size="lg" />
              <Badge variant="outline" className="mt-2 capitalize text-xs">
                {score.tier} risk
              </Badge>
            </div>

            {/* Dimension Breakdown */}
            <div>
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                Dimension Breakdown
              </p>
              <DimensionChart dimensions={score.dimensions} />
            </div>

            {/* Score Trend */}
            <div>
              <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                Score History
              </p>
              {historyLoading ? (
                <Skeleton className="h-48" />
              ) : (
                <ScoreTrend history={history} />
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/* --- Contacts Tab --- */

function ContactsTab({
  contacts,
  onAddContact,
  onEditContact,
}: {
  contacts: VendorContact[];
  onAddContact: () => void;
  onEditContact: (contact: VendorContact) => void;
}) {
  if (contacts.length === 0) {
    return (
      <EmptyState
        icon={Users}
        title="No contacts"
        description="Add a contact for this vendor."
        actionLabel="Add Contact"
        onAction={onAddContact}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={onAddContact}>
          <UserPlus className="h-4 w-4 mr-1" />
          Add Contact
        </Button>
      </div>
      <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead className="w-[80px]">Primary</TableHead>
              <TableHead className="w-[60px]" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {contacts.map((contact) => (
              <TableRow key={contact.id}>
                <TableCell className="font-medium text-text-primary">
                  {contact.first_name} {contact.last_name}
                </TableCell>
                <TableCell className="text-text-secondary text-sm">
                  {contact.email}
                </TableCell>
                <TableCell className="text-text-secondary text-sm">
                  {contact.role || "--"}
                </TableCell>
                <TableCell>
                  {contact.is_primary && (
                    <Badge variant="default" className="text-xs">
                      <Star className="h-3 w-3 mr-0.5" />
                      Primary
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEditContact(contact)}
                  >
                    <Pencil className="h-3 w-3" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

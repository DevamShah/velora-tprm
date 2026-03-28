import {
  LayoutDashboard,
  Building2,
  ClipboardCheck,
  AlertTriangle,
  Shield,
  FileCheck,
  Activity,
  FileBarChart,
  MessageSquare,
  Users,

  Settings,
  ScrollText,
  Plug,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const navigation: NavSection[] = [
  {
    title: "Overview",
    items: [
      { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    ],
  },
  {
    title: "Risk Management",
    items: [
      { label: "Vendors", href: "/vendors", icon: Building2 },
      { label: "Assessments", href: "/assessments", icon: ClipboardCheck },
      { label: "Review Queue", href: "/assessments/review-queue", icon: ClipboardCheck },
      { label: "Findings", href: "/findings", icon: AlertTriangle },
    ],
  },
  {
    title: "Intelligence",
    items: [
      { label: "Frameworks", href: "/frameworks", icon: Shield },
      { label: "Evidence", href: "/evidence", icon: FileCheck },
      { label: "Monitoring", href: "/monitoring", icon: Activity },
    ],
  },
  {
    title: "Operations",
    items: [
      { label: "Reports", href: "/reports", icon: FileBarChart },
      { label: "Communications", href: "/communications", icon: MessageSquare },
    ],
  },
  {
    title: "Administration",
    items: [
      { label: "Users & Roles", href: "/admin/users", icon: Users },
      { label: "Settings", href: "/admin/settings", icon: Settings },
      { label: "Audit Log", href: "/admin/audit-log", icon: ScrollText },
      { label: "Integrations", href: "/admin/integrations", icon: Plug },
    ],
  },
];

export function findBreadcrumbs(pathname: string): { label: string; href: string }[] {
  const crumbs: { label: string; href: string }[] = [];

  for (const section of navigation) {
    for (const item of section.items) {
      if (pathname === item.href || pathname.startsWith(item.href + "/")) {
        crumbs.push({ label: item.label, href: item.href });
        break;
      }
    }
  }

  if (pathname.includes("/new")) {
    crumbs.push({ label: "New", href: pathname });
  } else if (/\/[a-f0-9-]+$/.test(pathname) || /\/\[.*\]/.test(pathname)) {
    crumbs.push({ label: "Details", href: pathname });
  }

  // Handle admin sub-routes
  if (pathname === "/admin/roles") {
    return [
      { label: "Users & Roles", href: "/admin/users" },
      { label: "Roles", href: "/admin/roles" },
    ];
  }

  return crumbs;
}

export function getPageTitle(pathname: string): string {
  for (const section of navigation) {
    for (const item of section.items) {
      if (pathname === item.href) {
        return item.label;
      }
    }
  }
  return "Velora TPRM";
}

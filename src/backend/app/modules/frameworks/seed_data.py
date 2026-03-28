"""
Seed data definitions for compliance frameworks.

Contains framework metadata, clause hierarchies, cross-mappings,
and default scoring model configuration.
"""

from __future__ import annotations

import uuid
from typing import Dict, List

# Stable namespace for deterministic UUIDs
_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def uid(name: str) -> uuid.UUID:
    """Deterministic UUID from a seed name."""
    return uuid.uuid5(_NS, name)


# -- Framework IDs -------------------------------------------------

SOC2_ID = uid("soc2")
ISO27001_ID = uid("iso27001")
NIST_CSF_ID = uid("nist_csf")
HIPAA_ID = uid("hipaa")


# -- Framework metadata --------------------------------------------

FRAMEWORKS = [
    {
        "id": SOC2_ID,
        "name": "SOC 2 Type II",
        "version": "2022",
        "description": (
            "Service Organization Control 2 — "
            "Trust Services Criteria"
        ),
        "framework_type": "audit",
        "source_url": "https://www.aicpa.org/soc2",
        "status": "active",
    },
    {
        "id": ISO27001_ID,
        "name": "ISO 27001:2022",
        "version": "2022",
        "description": (
            "Information Security Management System — "
            "Annex A Controls"
        ),
        "framework_type": "certification",
        "source_url": "https://www.iso.org/standard/27001",
        "status": "active",
    },
    {
        "id": NIST_CSF_ID,
        "name": "NIST CSF 2.0",
        "version": "2.0",
        "description": (
            "Cybersecurity Framework — "
            "Core Functions and Categories"
        ),
        "framework_type": "framework",
        "source_url": "https://www.nist.gov/cyberframework",
        "status": "active",
    },
    {
        "id": HIPAA_ID,
        "name": "HIPAA",
        "version": "2013",
        "description": (
            "Health Insurance Portability and "
            "Accountability Act — Privacy, Security, "
            "Breach Rules"
        ),
        "framework_type": "regulation",
        "source_url": "https://www.hhs.gov/hipaa",
        "status": "active",
    },
]


# -- Clause expansion helper --------------------------------------

def _expand(
    framework_id: uuid.UUID,
    prefix: str,
    sections: list,
) -> List[dict]:
    """Expand section tuples into clause dicts."""
    clauses: List[dict] = []
    order = 0
    for sec_num, sec_title, children in sections:
        pid = uid(f"{prefix}_{sec_num}")
        clauses.append({
            "id": pid,
            "framework_id": framework_id,
            "parent_clause_id": None,
            "clause_number": sec_num,
            "title": sec_title,
            "description": None,
            "domain_tags": [
                sec_title.lower().split()[0]
            ],
            "depth": 0,
            "order_index": order,
        })
        order += 1
        for cnum, ctitle in children:
            clauses.append({
                "id": uid(f"{prefix}_{cnum}"),
                "framework_id": framework_id,
                "parent_clause_id": pid,
                "clause_number": cnum,
                "title": ctitle,
                "description": f"{sec_title} > {ctitle}",
                "domain_tags": [
                    sec_title.lower().split()[0]
                ],
                "depth": 1,
                "order_index": order,
            })
            order += 1
    return clauses


# -- Clause definitions -------------------------------------------

SOC2_CLAUSES = _expand(SOC2_ID, "soc2", [
    ("CC", "Common Criteria (Security)", [
        ("CC1", "Control Environment"),
        ("CC2", "Communication and Information"),
        ("CC3", "Risk Assessment"),
        ("CC4", "Monitoring Activities"),
        ("CC5", "Control Activities"),
    ]),
    ("A", "Availability", [
        ("A1.1", "System Availability Monitoring"),
        ("A1.2", "Recovery Procedures"),
        ("A1.3", "Business Continuity"),
    ]),
    ("PI", "Processing Integrity", [
        ("PI1.1", "Processing Completeness"),
        ("PI1.2", "Processing Accuracy"),
        ("PI1.3", "Processing Timeliness"),
    ]),
    ("C", "Confidentiality", [
        ("C1.1", "Data Classification"),
        ("C1.2", "Data Disposal"),
        ("C1.3", "Access Restrictions"),
    ]),
    ("P", "Privacy", [
        ("P1.1", "Notice and Consent"),
        ("P1.2", "Collection Limitation"),
        ("P1.3", "Use and Retention"),
        ("P1.4", "Disclosure and Notification"),
    ]),
])

ISO27001_CLAUSES = _expand(ISO27001_ID, "iso27001", [
    ("A.5", "Organizational Controls", [
        ("A.5.1", "Policies for Information Security"),
        ("A.5.2", "Information Security Roles"),
        ("A.5.3", "Segregation of Duties"),
    ]),
    ("A.6", "People Controls", [
        ("A.6.1", "Screening"),
        ("A.6.2", "Terms and Conditions of Employment"),
        ("A.6.3", "Information Security Awareness"),
        ("A.6.4", "Disciplinary Process"),
    ]),
    ("A.7", "Physical Controls", [
        ("A.7.1", "Physical Security Perimeters"),
        ("A.7.2", "Physical Entry"),
        ("A.7.3", "Securing Offices and Facilities"),
    ]),
    ("A.8", "Technological Controls", [
        ("A.8.1", "User Endpoint Devices"),
        ("A.8.2", "Privileged Access Rights"),
        ("A.8.3", "Information Access Restriction"),
        ("A.8.4", "Access to Source Code"),
    ]),
])

NIST_CSF_CLAUSES = _expand(NIST_CSF_ID, "nist_csf", [
    ("GV", "Govern", [
        ("GV.OC", "Organizational Context"),
        ("GV.RM", "Risk Management Strategy"),
        ("GV.SC", "Supply Chain Risk Management"),
    ]),
    ("ID", "Identify", [
        ("ID.AM", "Asset Management"),
        ("ID.RA", "Risk Assessment"),
        ("ID.IM", "Improvement"),
    ]),
    ("PR", "Protect", [
        ("PR.AA", "Identity Management and Access"),
        ("PR.AT", "Awareness and Training"),
        ("PR.DS", "Data Security"),
    ]),
    ("DE", "Detect", [
        ("DE.CM", "Continuous Monitoring"),
        ("DE.AE", "Adverse Event Analysis"),
        ("DE.DP", "Detection Processes"),
    ]),
    ("RS", "Respond", [
        ("RS.MA", "Incident Management"),
        ("RS.AN", "Incident Analysis"),
        ("RS.MI", "Incident Mitigation"),
    ]),
])

HIPAA_CLAUSES = _expand(HIPAA_ID, "hipaa", [
    ("164.5", "Privacy Rule", [
        ("164.502", "Uses and Disclosures"),
        ("164.508", "Authorizations"),
        ("164.510", "Uses Requiring Opportunity"),
        ("164.514", "De-identification"),
    ]),
    ("164.3", "Security Rule", [
        ("164.308", "Administrative Safeguards"),
        ("164.310", "Physical Safeguards"),
        ("164.312", "Technical Safeguards"),
    ]),
    ("164.4", "Breach Notification Rule", [
        ("164.402", "Breach Definitions"),
        ("164.404", "Individual Notification"),
        ("164.406", "Media Notification"),
    ]),
])

ALL_CLAUSES = (
    SOC2_CLAUSES
    + ISO27001_CLAUSES
    + NIST_CSF_CLAUSES
    + HIPAA_CLAUSES
)


# -- Cross-framework mappings -------------------------------------

MAPPINGS = [
    {
        "id": uid("map_cc1_a51"),
        "source_clause_id": uid("soc2_CC1"),
        "target_clause_id": uid("iso27001_A.5.1"),
        "mapping_type": "equivalent",
        "confidence": 0.85,
        "source_type": "olir",
        "verified": True,
        "verified_by": None,
    },
    {
        "id": uid("map_cc2_a52"),
        "source_clause_id": uid("soc2_CC2"),
        "target_clause_id": uid("iso27001_A.5.2"),
        "mapping_type": "partial",
        "confidence": 0.70,
        "source_type": "olir",
        "verified": True,
        "verified_by": None,
    },
    {
        "id": uid("map_cc3_a53"),
        "source_clause_id": uid("soc2_CC3"),
        "target_clause_id": uid("iso27001_A.5.3"),
        "mapping_type": "related",
        "confidence": 0.60,
        "source_type": "ai",
        "verified": False,
        "verified_by": None,
    },
    {
        "id": uid("map_cc5_a82"),
        "source_clause_id": uid("soc2_CC5"),
        "target_clause_id": uid("iso27001_A.8.2"),
        "mapping_type": "partial",
        "confidence": 0.75,
        "source_type": "olir",
        "verified": True,
        "verified_by": None,
    },
]


# -- Default scoring model config ---------------------------------

DEFAULT_MODEL_CONFIG: Dict = {
    "dimensions": [
        {
            "name": "Security Posture",
            "weight": 0.25,
            "description": "Overall security controls maturity",
        },
        {
            "name": "Compliance",
            "weight": 0.20,
            "description": "Regulatory and framework compliance",
        },
        {
            "name": "Data Protection",
            "weight": 0.20,
            "description": "Data handling, encryption, privacy",
        },
        {
            "name": "Operational Risk",
            "weight": 0.20,
            "description": "Business continuity and resilience",
        },
        {
            "name": "Financial Stability",
            "weight": 0.15,
            "description": "Financial health and viability",
        },
    ]
}

DEFAULT_THRESHOLDS: Dict = {
    "critical": 25.0,
    "high": 50.0,
    "medium": 75.0,
    "low": 100.0,
}

DEFAULT_INHERENT_FACTORS: Dict = {
    "data_classification": {
        "restricted": 90,
        "confidential": 70,
        "internal": 40,
        "public": 20,
    },
    "business_criticality": {
        "critical": 20,
        "high": 10,
        "medium": 0,
        "low": -10,
    },
}

# Projekt Cap Table Management (CTM)


> **CTM** = Cap Table Management. Internal tool to replace currenttool for cap table and ESOP management.

---

## 1. Purpose & scope

Replace currenttool with the **simplest defensible** tool that is the **single source of truth** for the cap table and ESOP, leverages our existing **GSuite** stack, and is actually used (currenttool's hidden cost is non-use due to complexity).

**In scope**

- Cap table: source of truth + versioning + safe editing + CSV export + filtering (P2)
- ESOP: pool-level and per-employee status (CFO view only)
- Setup: import from currenttool exports + consistency checks

**Out of scope**

- ESOP holder self-service → employees ask CFO
- The tool is **not** the statutory share register (Aktienregister). It is the **source of truth from which the register is generated** (PDF/export). Common practice at small AGs.

---

## 2. Decision: recommended approach

**Recommended: Google Sheets in a restricted Shared Drive**, using native version history for versioning, protected ranges for safeguards, computed ESOP status, and a reconciliation tab for the currenttool cross-check.

### Why this, not the alternatives

| Option | Verdict | Reason |
|---|---|---|
| **A. Google Sheets (native version history)** | ✅ **Chosen** | Meets stated versioning need (view prior states before restoring), GSuite-native, CFO-editable, 3-4 concurrent editors fine, ~3100 rows trivial |
| B. Sheets + CSV snapshots in private Git | ❌ Over-built | Git was only needed for true diff/branch — you downgraded to timestamped restore. Removes the need. |
| C. CSV/YAML in Git via PR review | ❌ | Not editable by accounting/HR; engineer-only |
| D. Custom web app + DB | ❌ | High maintenance + key-person risk; you'd own security and upkeep forever. Avoid building what you must own (Fadell, *Build*). |

> *Diagnosis before design (Rumelt, Good Strategy/Bad Strategy):* the real problem was **non-use of an over-complex tool**, not a missing feature. The fix is simplicity, not capability.

### What we are trading (inversion — Munger)

| We give up (vs. currenttool) | Mitigation |
|---|---|
| Recognized-system trust in diligence | Keep clean exports + generate formal register from notary/fiduciary |
| Built-in ESOP automation | Replicate with formulas (math is simple date arithmetic) |
| Vendor-managed security | Lock down via Workspace controls (§7) |

---

## 3. Requirements → solution mapping

| # | Requirement | Solution | Prio |
|---|---|---|---|
| 1 | Single source of truth | One workbook, one owner, restricted access | P1 |
| 1 | Stock types, dates, shareholder type | Structured columns + data validation | P1 |
| 1 | Versioning, view + restore prior states | Native version history + named versions | P1 |
| 1 | Easy edits with safeguards | Protected ranges, validation, edit roles | P1 |
| 1 | CSV export | Native (File → Download → CSV) | P1 |
| 1 | View/filter, incl. per group | Filter views; or post-export in sheet | P2 |
| 2 | Pool-level ESOP status | Dashboard tab, `SUMIFS` rollups | P1 |
| 2 | Per-employee ESOP status | Grants tab, computed vesting | P1 |
| 2 | Employee self-service | Dropped → ask CFO | — |
| 3 | Import from currenttool | CSV import | P1 |
| 3 | Consistency checks vs. currenttool | Reconciliation tab (totals diff) | P1 |

---

## 4. Workbook structure

| Tab | Content | Notes |
|---|---|---|
| `CapTable_Core` | ~100 named holders (common + preferred): name, address, class, qty, acquisition date, holder type | The active, frequently-viewed table |
| `CapTable_Crowd` | ~3000 crowd-shareholders (common) | Static block, imported once, rarely changes. Separated to keep core clean. |
| `ESOP_Grants` | One row per grant: employee, grant date, qty, cliff, vesting period, strike, class | Drives all ESOP math |
| `ESOP_Dashboard` | Pool-level rollups | Read-only, formula-driven |
| `Reconciliation` | currenttool totals vs. tool totals | Used at migration + periodically |
| `Reference` | Dropdown lists, classes, holder types | Powers data validation |
| `Changelog` | Manual log of material changes + date + author | Discipline layer on top of version history |

> [Inference] Separating crowd-shareholders is the one design choice the scale forces. Everything else is standard.

---

## 5. Versioning approach

- **Mechanism:** Google Sheets **version history** — every edit timestamped + attributed; prior states **viewable before restore** (matches your Google Docs-style requirement).
- **Discipline:** create a **named version** at each material change (new round, ESOP grant batch, crowd import). Named versions are the "save points" you'll actually navigate to.
- **Backup (optional, low-effort):** scheduled CSV snapshot to a separate Drive folder for an immutable copy. Decide in Phase 3.

> [Unverified] Version-history retention and granularity depend on Workspace tier and may group rapid edits. Confirm against your tier before relying on it as sole history.

---

## 6. Safeguards (against accidental damage)

| Safeguard | Purpose |
|---|---|
| **Protected ranges** on headers, formulas, computed columns | Prevent structural breakage |
| **Data validation** (dropdowns, date/number rules) | Stop malformed entries at source |
| **Edit vs. view roles** within the team | Limit who can change core data |
| **Named versions** before bulk edits | One-click recovery point |
| **Reconciliation totals** always visible | Catch silent errors fast |

> [Unverified] Protected ranges reduce accidental edits; they do not *prevent* all error (an editor with edit rights can still override). Label: a control, not a guarantee.

---

## 7. Confidentiality & GSuite

| Control | Action |
|---|---|
| Storage | Dedicated **restricted Shared Drive**, membership = CFO + accounting + HR only |
| External sharing | **Disabled** on that Shared Drive |
| Authentication | Enforce **2-step verification** for all members (Admin console) |
| Audit | Workspace **audit log** for access/edit trail |
| DLP | [Unverified — tier-dependent] Data Loss Prevention rules if on Business Plus / Enterprise |
| Link hygiene | No "anyone with link"; no export to personal accounts |

> [Unverified] Specific availability of DLP, retention, and audit depth depends on your Workspace edition. Verify edition before finalizing the security design.

---

## 8. ESOP model

**Pool-level status** (Dashboard, computed):

| State | Definition |
|---|---|
| Converted | Exercised → became shares |
| Vested, not converted | Vested but not yet exercised |
| Granted, not vested | Allocated, still vesting |
| Not granted | Remaining pool |

**Per-employee status** (Grants tab, computed):

- Allocated → **vested / not vested** (date arithmetic: grant date, cliff, vesting period)
- Exercised → **settled cash / settled physical / not exercised**

> All ESOP changes are also documented in allocation agreements, so the sheet is a *view*, not the only record. Unwinding an error is cumbersome but bounded.

Formula design is deferred to the implementation phase.

---

## 9. Setup & migration from currenttool

1. **Export** cap table + ESOP from currenttool as CSV.
2. **Import** into the structured tabs (map columns to schema).
3. **Reconcile** in `Reconciliation` tab:
   - Total shares per class (tool vs. currenttool)
   - Total holders / crowd count
   - ESOP pool size + per-holder vested/granted totals
   - Any nonzero diff = investigate before go-live.
4. **Parallel run** for a defined period, then decommission currenttool.

---

## 10. Risks & open questions

| # | Open question | Why it matters |
|---|---|---|
| 1 | Statutory register: who maintains it (notary/fiduciary) and in what format? | Confirms the tool is a *source*, not the legal record |
| 2 | Crowd-shareholders: held **directly** or via **nominee / pooling vehicle**? | Affects register structure + whether 3000 rows are individuals or one block |
| 3 | Number of ESOP holders + vesting schedule (standard vs. per-grant custom)? | Determines formula complexity |
| 4 | Workspace edition (Business Starter/Standard/Plus/Enterprise)? | Gates DLP, audit depth, retention |
| 5 | Who **owns and maintains** the workbook long-term? | Avoids new key-person risk |
| 6 | Beneficial-owner records (>25% holders, Art. 697j ff. OR) — handled where? | [Unverified] Compliance obligation; confirm with counsel |

> [Unverified] All legal/compliance points (statutory register, beneficial ownership, GAFI) require confirmation with your corporate counsel or fiduciary. This briefing does not constitute legal advice.

---

## 11. Roadmap

| Phase | Goal | Output |
|---|---|---|
| **0. Decide & secure** | Confirm approach + open questions §10; set up restricted Shared Drive + access controls | Approved approach, secured workspace |
| **1. Structure** | Build workbook tabs, schema, validation, protected ranges | Empty, locked-down structure |
| **2. Migrate** | Import currenttool exports; reconcile to zero diff | Populated, reconciled source of truth |
| **3. ESOP + safeguards** | Vesting formulas, dashboard, named-version discipline, optional snapshot | Working ESOP view + recovery process |
| **4. Cutover** | Parallel run, then decommission currenttool | currenttool cancelled, CTM live |

---

## 12. Assumptions & decision log

- Entity: **AG**.
- Scale: ~100 named holders (common + preferred) + ~3000 crowd-shareholders (common).
- Cap table changes: **rare**. ESOP changes: **more frequent**, always documented elsewhere.
- Versioning need: **timestamped restore + view-before-restore** (not diff/branch).
- Editors: **3-4** (CFO + accounting + HR).
- currenttool cost: **>5,000 CHF/yr**, under-used due to complexity.
- Tool is the **source of truth**, not the statutory register.

> *Drucker, The Effective Executive:* effectiveness is doing the right things. Here that means a tool the team will actually use, not the most capable one.



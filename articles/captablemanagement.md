
# CTM Tool — Project Briefing (as built)

Internal tool replacing Ledgy for cap table and ESOP management. This version documents the **delivered** architecture. For day-to-day procedures see `CTM_manual.md`.

> **Outcome:** a single Google Sheet, reconciled to Ledgy (371,497 issued shares), with computed ESOP, four-bucket accounting, audit logging, and a 4-eye workflow. Ledgy can be decommissioned.

---

## 1. Why this shape

| Driver | Decision |
|---|---|
| Simplicity + actual use (Ledgy was costly and under-used) | A Google Sheet, not a custom app |
| GSuite-native, low maintenance | Native version history + Apps Script |
| Legal-grade but not the statutory register | Tool is the **source of truth** from which the register is generated |
| Few editors (CFO, Accounting, HR) | Procedural 4-eye + soft controls, not a workflow engine |

The full event-sourced "mini-Ledgy" was deliberately rejected as over-engineering. The tool stores current state and keeps the imported ledger frozen for audit.

---

## 2. Tabs (final)

| Tab | Role | Editable |
|---|---|---|
| `Dashboard` | Cap table + ESOP overview, fully-diluted, checks band | No |
| `CapTable` | One row per holder × agreement (the register source) | Yes |
| `CapTable_View_Core` / `_Crowd` | Read-only `QUERY` views | No |
| `ESOP_Grants` | One row per allocation agreement; vesting + 4 buckets computed | Inputs only |
| `ESOP_Events` | One row per exercise / termination | Yes |
| `ESOP_view` | Per-person ESOP view (debugging/reconciliation) | No |
| `History` | Frozen Ledgy transaction export at migration | No |
| `Changelog` | The "why" + 4-eye sign-off | Yes |
| `Reference` | Dropdown source lists | Rarely |

Convention: **blue = input, grey = computed** (one sanctioned exception, §4).

---

## 3. Cap table model

- **One row per holder × agreement** (model B). A `person_id` is the spine that links a human across SHA, CIA, and ESOP. Dual holders (core + crowd) appear as two rows sharing one `person_id` — no fuzzy name-merging.
- **Three effective classes** via `agreement` × stock type: SHA-common, SHA-preferred, CIA-common. Agreement derived at import: Crowd → CIA, else SHA.
- **Crowd**: ~2,945 individual beneficiaries (one row each), nested in Ledgy under three entities (CH / AT / DE), carried as `crowd_entity`.
- Snapshot, not a ledger: rare discrete edits; round-level history lives in `History`.

---

## 4. ESOP model

Vesting is computed **Linear**, evaluated at a single **valuation-date assumption** (`ESOP_Grants!K3`, normally `=TODAY()`, overridable to simulate). Each grant is split into four buckets that always sum to `granted_qty`:

| Bucket | Meaning |
|---|---|
| `exercised` | Physical exercises → became common shares |
| `vested` | Vested, not exercised |
| `granted_unvested` | Not yet vested (active grants) |
| `returned_to_pool` | Cancelled back to pool: terminated-unvested **+ cash-settled exercises** |

Each grant carries a `row_check` (the four buckets must equal `granted_qty`, none negative). Pool-level and per-row checksums both exist.

**Rules encoded:**

| Case | Handling |
|---|---|
| Termination **before** cliff | vested = 0; whole package → `returned_to_pool` |
| Termination **after** cliff | keeps vested-at-termination; rest → `returned_to_pool` |
| **Physical** exercise | → `exercised`; employee added to `CapTable` (same `person_id`) |
| **Cash** exercise | options consumed, no shares; qty → `returned_to_pool` (Dashboard shows a "thereof settled in cash" sub-line) |
| Non-linear / bespoke (e.g. full forfeiture despite post-cliff exit; employment-% change) | `is_approx = Yes` + overtype `vested_calc` with the agreed figure (the sanctioned grey-cell exception); buckets recompute and the row-check still validates |

Vesting rounds **down** (an option vests only once fully earned).

---

## 5. Views

- **`Dashboard`**: cap table by holder type (issued % and fully-diluted %), ESOP pool status (exercised / vested-not-exercised / granted-not-vested / not-granted, summing to pool size), accuracy flag for non-linear grants, and a checks band.
- **`CapTable_View_Core`**: core holders as individuals, sorted by type then name.
- **`CapTable_View_Crowd`**: all crowd investors, grouped CH → AT → DE then name.
- **`ESOP_view`**: per-person aggregation (granted, exercised, vested, granted_unvested, returned_to_pool), sortable by status then name, with grant-count and status flags for debugging.

---

## 6. Fully-diluted model

Fully-diluted total adds three inputs to issued shares (implemented and tested):

| Component | Definition |
|---|---|
| Issued shares | from `CapTable` |
| **ESOP (3a)** | pool size − exercised (exercised already counted in issued; avoids double-count). Checksummed against pool − exercised |
| **KWK (3b)** — Kunden werben Kunden | input cell |
| **Bond (3c)** | input cell |

`Fully-diluted total = issued + ESOP(3a) + KWK(3b) + Bond(3c)`. The `CapTable_View` percentages reference this FD-total cell.

---

## 7. Versioning, controls, security

| Layer | Mechanism |
|---|---|
| Versioning | Google native version history (view-before-restore); named versions at material changes |
| Audit (mechanical) | Apps Script `onEdit` auto-logs who/when/cell/old→new to `Changelog` |
| Audit (why) | Manual `Changelog` note |
| 4-eye | `prepared_by` ≠ `approved_by` + `approved_date`; named version for material changes |
| Computed cells | Protected ranges (formula-owner only) |
| `History` | Protected, read-only |
| Security | Restricted Shared Drive (3–4 members), external sharing off, 2FA enforced |

[Inference] Controls are proportionate to scale: the Sheet cannot hard-enforce 4-eye, so the discipline is procedural, with the checks band as the safety net.

---

## 8. Migration & reconciliation (record)

- **Sources:** three Ledgy exports — Transactions (event ledger), Cap table Detailed (holdings), Grants by Pool (grant-level statuses).
- **Reading caveat (encoded as a lesson):** one export's malformed stylesheet broke standard readers and silently truncated it; caught by reconciliation, fixed by parsing the raw XML. Reconciliation totals are the completeness tripwire.
- **Cap table:** sum `Common`/`Preferred issued` per holder (nets transfers, includes exercises) → ties exactly to **371,497** issued (143,496 common + 228,001 preferred).
- **ESOP:** grants from Option transactions (with vesting terms); events from Exercise + Termination. Cross-checked against Grants-by-Pool: **55,849** options ever granted, **129** terminated grants — matched both sources. (Cumulative grants exceed the 40,000 pool because returned options were re-granted.)
- **Manual calibrations:** unify one dual holder's `person_id`; verify `is_approx` on non-linear grants; the single cash settlement; special-agreement forfeitures.

---

## 9. Decisions & principles (log)

- Sheet over custom app; source-of-truth over statutory register.
- Model B (holder × agreement) with `person_id` spine.
- Per-entity hybrid storage: snapshot `CapTable` + frozen `History` + computed ESOP.
- Four-bucket ESOP summing to `granted_qty`; Linear vesting; single valuation-date assumption.
- `is_approx` flag + sanctioned `vested_calc` override for bespoke cases (no general override column).
- ROUNDDOWN vesting; cash exercise → pool, not conversion.
- Over-engineering avoided throughout (no Git layer, no event-sourcing, no performance-grant type that doesn't exist).

---

## 10. Maintenance & next

- Decommission Ledgy after a final parallel check.
- Name a clean "known-good" version as the baseline.
- Keep publishing changes via `Changelog` + named versions.
- Re-run the §7 tests in `CTM_manual.md` after any material change.

*Day-to-day procedures, the 4-eye workflow, and the test suite live in `CTM_manual.md`.*




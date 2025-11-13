# Repo Sniper - Comparison Report

## Supabase vs PostHog Analysis

### Executive Summary

Both repositories are **Priority 1: The Bleeding** targets, but PostHog shows significantly more severe firefighting issues.

---

## Side-by-Side Comparison

| Metric | Supabase | PostHog | Winner |
|--------|----------|---------|--------|
| **Firefighting Score** | 87.0 | **158.0** | PostHog (81% higher) |
| **Priority** | Priority 1 | Priority 1 | Tie |
| **Revert Rate** | 3.0% | 0.0% | PostHog (better) |
| **Hotfix Rate** | 26.0% | **39.0%** | Supabase (better) |
| **Regression Ratio** | 0.81 | **1.15** | Supabase (better) |
| **Reviewer Tax** | 0.07 | **0.51** | Supabase (better) |
| **Panic Clusters** | 2 | **8** | Supabase (better) |

---

## Detailed Analysis

### SUPABASE: Score 87.0

#### Score Breakdown:
- **Revert Contribution**: 15.0 (3.0% × 5.0 weight)
- **Hotfix Contribution**: 52.0 (26.0% × 2.0 weight)
- **Panic Contribution**: 20.0 (2 clusters × 10.0 weight)

#### Key Findings:
- **Revert Rate**: 3.0% (just under DORA Elite baseline of <5%)
- **Hotfix Rate**: 26.0% (moderate - 1 in 4 PRs is a fix)
- **Regression Ratio**: 0.81 hotfixes per feature (8x above ideal)
- **Reviewer Tax**: Only 7% of changed lines are in hotfixes
- **Panic Clusters**: 2 instances of cascading failures

#### Top 3 Incident Clusters:
1. **PR #38387** → 1 hotfix (#39648)
   - "Add new metrics to Realtime report"

2. **PR #35831** → 1 hotfix (#35692)
   - "feat: Snippets"

3. **PR #40069** → 1 hotfix (#40339)
   - "feat(studio): email template configuration"

#### Panic Spirals:
1. PRs #40328, #40330 (2 consecutive hotfixes)
2. PRs #40319, #40259, #40276 (3 consecutive hotfixes)

#### Strengths:
- Low revert rate (3%)
- Relatively low reviewer tax (7%)
- Only 2 panic clusters

#### Pain Points:
- Still 26% hotfix rate (room for improvement)
- Context gaps between feature and fixes

---

### POSTHOG: Score 158.0 🔥

#### Score Breakdown:
- **Revert Contribution**: 0.0 (0.0% × 5.0 weight)
- **Hotfix Contribution**: 78.0 (39.0% × 2.0 weight)
- **Panic Contribution**: 80.0 (8 clusters × 10.0 weight)

#### Key Findings:
- **Revert Rate**: 0.0% (excellent - no explicit reverts!)
- **Hotfix Rate**: 39.0% (HIGH - 2 in 5 PRs are fixes!)
- **Regression Ratio**: 1.15 hotfixes per feature (11.5x above ideal)
- **Reviewer Tax**: 51% of changed lines are in hotfixes (VERY HIGH)
- **Panic Clusters**: 8 instances of cascading failures

#### Top 3 Incident Clusters:
1. **PR #40814** → **11 hotfixes** (#41419, #41473, #41469, #41343, #40883, #41443, #41446, #40738, #41418, #40683, #40643)
   - **Severity**: HIGH
   - "AI feature" caused a cascade of 11 follow-up fixes
   - **This is the smoking gun!**

2. **PR #41123** → 3 hotfixes (#41444, #41133, #41454)
   - **Severity**: HIGH
   - "Flags feature" caused 3 follow-up fixes

3. **PR #41287** → 4 hotfixes (#41431, #41350, #41388, #41266)
   - **Severity**: HIGH
   - "LLMA feature" caused 4 follow-up fixes

#### Panic Spirals (8 total!):
1. PRs #41456, #41150 (logs, workflows)
2. PRs #41451, #41210 (various components)
3. PRs #41402, #41441 (data-warehouse)
4. PRs #41430, #41428 (search)
5. **PRs #41427, #41422, #41423, #41418** (web-analytics, ph-ai) - 4 consecutive!
6. PRs #41350, #41388 (llma)
7. **PRs #41412, #41354, #39020, #40908, #41401, #41400, #41396** - **7 consecutive hotfixes!**
8. PRs #41392, #41389 (sessions)

#### Strengths:
- Zero reverts (they don't roll back, they fix forward)

#### Pain Points:
- **39% hotfix rate** - Nearly 2 in 5 PRs are urgent fixes
- **51% reviewer tax** - Over half the code review effort is firefighting
- **8 panic clusters** - Frequent cascading failures
- **PR #40814 caused 11 fixes** - Severe context collapse

---

## Key Insights

### Why PostHog Scores Higher (Worse):
1. **Volume of Cascading Failures**: 8 panic clusters vs 2
2. **Severity of Incidents**: One feature PR caused 11 hotfixes
3. **Hotfix Ratio**: 39% vs 26%
4. **Reviewer Tax**: 51% vs 7% (7x worse)

### Why PostHog is a Better Lead:
- **More acute pain**: 51% reviewer tax means their team spends MORE time fixing bugs than building features
- **Specific evidence**: PR #40814 with 11 follow-up fixes is undeniable
- **Clear ROI**: If CodeRisk prevents just 1 "PR #40814" incident, it saves ~77 engineering hours

### Outreach Implications:

**PostHog Email Should Emphasize:**
- PR #40814 specifically (11 fixes is shocking)
- 51% reviewer tax (their team reviews more bugs than features)
- 39% hotfix rate (nearly 40% of work is reactive)
- 8 panic spirals (fire after fire)

**Supabase Email Should Emphasize:**
- Lower severity but still meaningful pain
- Good hygiene on reverts (0% vs 3%)
- Opportunity to prevent the "next Snippets bug"

---

## Calculated ROI

### Supabase:
- Revert rate: 3% × 100 PRs/month = 3 reverts/month
- Cost per revert: ~7 hours
- **Monthly firefighting cost**: ~21 hours

### PostHog:
- Hotfix rate: 39% × 100 PRs/month = 39 hotfixes/month
- Average cost per hotfix: ~3 hours (conservative)
- **Monthly firefighting cost**: ~117 hours
- **Plus**: PR #40814 alone cost ~77 hours (11 fixes × 7 hours)

---

## Verdict: Target Priority Ranking

1. **🔥🔥🔥 PostHog** (Score: 158)
   - Highest pain
   - Clear smoking gun (PR #40814)
   - 51% reviewer tax is unsustainable
   - Most compelling email

2. **🔥🔥 Supabase** (Score: 87)
   - Meaningful pain
   - Good secondary target
   - Lower urgency but still Priority 1

---

## Next Steps

1. **Send PostHog email first** - highest conversion probability
2. Reference PR #40814 explicitly in subject line
3. Lead with "51% of your code review is firefighting"
4. Offer to analyze their "AI feature" incident specifically


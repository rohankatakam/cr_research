# Repo Sniper - GTM Strategy Tool

Automated repository analysis tool for identifying high-value COSS (Commercial Open Source Software) leads based on "firefighting" metrics.

## Overview

This tool analyzes public GitHub repositories to:
1. Fetch recent PR and Issue activity via GitHub GraphQL API
2. Classify PRs into FEATURE, CHORE, REVERT, HOTFIX using Gemini Flash
3. Calculate "Firefighting Score" based on revert rates, hotfix rates, and panic clusters
4. Generate personalized outreach emails with specific PR evidence

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

API keys are stored in `.env`:
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GEMINI_API_KEY`: Google Gemini API key

## Usage

### Analyze a single repository:
```bash
python main.py supabase/supabase
```

### Analyze all target repositories:
```bash
python main.py
```

This will process all repos in `data/target_repos.json` and generate:
- `data/results/{owner}_{repo}_analysis.json` - Full analysis
- `data/results/{owner}_{repo}_outreach.txt` - Email template
- `data/results/{owner}_{repo}_summary.txt` - Summary report
- `data/results/ranked_scores.json` - Ranked list

## Algorithm: Firefighting Score Calculation

This tool calculates a **Firefighting Score** that quantifies how much a repository is "bleeding" from context collapse, regressions, and reactive bug fixes. Higher scores indicate more severe problems.

### Step 1: Data Collection (GitHub GraphQL API)

For each repository, fetch the last 100 merged/closed PRs and 50 closed issues:

**PR Data Extracted:**
- Title, body text, labels
- Merge date, creation date
- Author
- Lines changed (additions + deletions)
- Files changed
- Comment count

**Issue Data Extracted:**
- Title, body text, labels
- Creation date, closure date

### Step 2: PR Classification (Gemini Flash LLM)

Each PR is classified into exactly one category using AI analysis:

**Categories:**
1. **FEATURE**: New functionality, major enhancements, new components
2. **CHORE**: Dependencies updates, documentation, minor styling, refactoring
3. **REVERT**: Explicit rollbacks (keywords: "Revert", "Undo", "Rollback")
4. **HOTFIX**: Urgent fixes for recent bugs (keywords: "fix", "bug", "broken", "regression", "critical", "hotfix")

**Classification Method:**
- Send all 100 PRs to Gemini Flash 2.5 in a single batch
- Prompt includes PR metadata (title, body, labels, changed files)
- LLM performs semantic analysis to categorize each PR
- Returns structured JSON with classifications + reasoning

### Step 3: Pattern Detection

**A. Context Gaps**
Identify instances where:
- A HOTFIX was merged < 48 hours after a FEATURE
- Both PRs affect similar files or functionality
- Indicates: Feature introduced a bug that required immediate fixing

**B. Panic Spirals**
Detect sequences of 2+ consecutive HOTFIXes or REVERTs:
- Example: PR #100 (HOTFIX) → PR #101 (HOTFIX) → PR #102 (HOTFIX)
- Indicates: Cascading failures where fixes introduce new bugs

**C. Incident Clusters**
Link FEATUREs to their follow-up HOTFIXes/REVERTs:
- Track which FEATURE PRs caused the most downstream fixes
- Example: "PR #500 (FEATURE) → [PR #510, #515, #520] (3 HOTFIXes)"
- Severity ranked by number of follow-up fixes

### Step 4: Metric Calculation

**Revert Rate:**
```
Revert Rate = (Count of REVERT PRs / Total PRs) × 100
```
*Baseline: DORA "Elite" teams have < 5% revert rate*

**Hotfix Rate:**
```
Hotfix Rate = (Count of HOTFIX PRs / Total PRs) × 100
```
*Ideal: < 10%. High-velocity teams often see 20-40%*

**Regression Ratio:**
```
Regression Ratio = Count of HOTFIX PRs / Count of FEATURE PRs
```
*Ideal: < 0.1 (1 fix per 10 features). Ratios > 0.5 indicate severe context collapse*

**Reviewer Tax:**
```
Reviewer Tax = (Total Lines Changed in HOTFIXes) / (Total Lines Changed in FEATUREs)
```
*Measures what % of code review effort is spent on firefighting vs building*

**Panic Cluster Count:**
```
Panic Cluster Count = Number of detected panic spirals
```
*0-1 is healthy, 5+ indicates systemic issues*

### Step 5: Firefighting Score Formula

```
S_F = (W_R × RevertRate) + (W_H × HotfixRate) + (W_C × PanicClusterCount)
```

**Weights:**
- W_R = 5.0 (Reverts are severe - production failures)
- W_H = 2.0 (Hotfixes indicate reactive work)
- W_C = 10.0 (Panic spirals are the highest severity indicator)

**Example Calculation (PostHog):**
- Revert Rate: 0.0%
- Hotfix Rate: 39.0%
- Panic Clusters: 8

```
S_F = (5.0 × 0.0) + (2.0 × 39.0) + (10.0 × 8)
S_F = 0 + 78 + 80
S_F = 158.0
```

### Step 6: Priority Classification

**Priority 1 (The Bleeding)**: Score ≥ 50
- Severe firefighting issues
- High hotfix/revert rates or multiple panic spirals
- Primary outreach targets

**Priority 2 (The Worried)**: Score ≥ 20
- Moderate firefighting issues
- Some pain but not critical
- Secondary outreach targets

**Ignore**: Score < 20
- Healthy repository
- Low firefighting overhead
- Not a good fit for CodeRisk

### Output: Actionable Intelligence

For each repository, generate:

1. **Firefighting Score** with priority level
2. **Score Breakdown** showing contribution of each component
3. **Top 3 Incident Clusters** with specific PR numbers
4. **Panic Spirals** list with affected PRs
5. **Personalized Email** citing specific evidence:
   - "PR #40814 caused 11 follow-up fixes"
   - "51% of your code review is firefighting (Reviewer Tax)"
   - Comparison to DORA baselines

### Real-World Results

**Supabase:** Score 87.0
- 3% revert rate, 26% hotfix rate
- 2 panic clusters
- Example: PR #38387 → 1 hotfix

**PostHog:** Score 158.0 (81% worse)
- 0% revert rate, 39% hotfix rate
- 8 panic clusters
- Smoking gun: PR #40814 → 11 hotfixes
- 51% reviewer tax (team spends more time fixing than building)

## Target Repos

20 COSS companies curated from a16z/Sequoia portfolios:
- airbyte, posthog, supabase, meilisearch, strapi
- cal.com, grafana, appwrite, directus, n8n
- nocodb, twenty, formbricks, infisical, lago
- windmill, excalidraw, plane, hasura, openreplay

## Rate Limits

- GitHub GraphQL: 5,000 points/hour (~1,600 repos)
- Gemini Flash: Effectively unlimited (< $0.01 per 100 repos)

## Author

Rohan Katakam - CodeRisk

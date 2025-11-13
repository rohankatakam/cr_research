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

## Output

### Firefighting Score Formula:
```
S_F = (5.0 × RevertRate) + (2.0 × HotfixRate) + (10.0 × PanicClusterCount)
```

### Priority Levels:
- **Priority 1 (The Bleeding)**: Score ≥ 50
- **Priority 2 (The Worried)**: Score ≥ 20
- **Ignore**: Score < 20

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

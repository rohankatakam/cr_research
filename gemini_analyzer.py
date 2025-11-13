"""Gemini Flash-based analyzer for PR classification and firefighting metrics."""

import json
import google.generativeai as genai
from typing import Dict, List
import config


class GeminiAnalyzer:
    """Analyzer using Gemini Flash for PR/Issue classification."""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)

    def analyze_repository(self, repo_data: Dict) -> Dict:
        """
        Analyze PR and Issue data to calculate firefighting metrics.

        Args:
            repo_data: Dictionary containing PRs and Issues

        Returns:
            Analysis results with classifications and metrics
        """
        owner = repo_data["owner"]
        repo = repo_data["repo"]
        prs = repo_data["pull_requests"]
        issues = repo_data["issues"]

        print(f"\nAnalyzing {owner}/{repo} with Gemini Flash...")

        # Prepare data for LLM
        pr_summaries = []
        for pr in prs:
            pr_summaries.append({
                "number": pr["number"],
                "title": pr["title"],
                "body": pr.get("body", "")[:500] if pr.get("body") else "",  # Limit body length
                "state": pr["state"],
                "merged": pr["merged"],
                "mergedAt": pr.get("mergedAt"),
                "createdAt": pr["createdAt"],
                "additions": pr["additions"],
                "deletions": pr["deletions"],
                "changedFiles": pr["changedFiles"],
                "labels": pr["labels"],
                "author": pr["author"]["login"] if pr["author"] else "unknown"
            })

        issue_summaries = []
        for issue in issues[:50]:  # Limit to 50 issues
            issue_summaries.append({
                "number": issue["number"],
                "title": issue["title"],
                "body": issue.get("body", "")[:300] if issue.get("body") else "",
                "createdAt": issue["createdAt"],
                "closedAt": issue.get("closedAt"),
                "labels": issue["labels"]
            })

        # Create the prompt
        prompt = self._create_analysis_prompt(pr_summaries, issue_summaries)

        # Call Gemini
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            # Sometimes LLM wraps JSON in markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            analysis = json.loads(result_text)

            print(f"Analysis complete!")
            print(f"  Revert Rate: {analysis['metrics']['revert_rate']:.2f}%")
            print(f"  Hotfix Rate: {analysis['metrics']['hotfix_rate']:.2f}%")
            print(f"  Regression Ratio: {analysis['metrics']['regression_ratio']:.2f}")
            print(f"  Panic Clusters: {len(analysis['panic_clusters'])}")

            return analysis

        except Exception as e:
            print(f"Error during Gemini analysis: {e}")
            # Return empty analysis
            return {
                "pr_classifications": [],
                "metrics": {
                    "revert_rate": 0.0,
                    "hotfix_rate": 0.0,
                    "regression_ratio": 0.0,
                    "reviewer_tax": 0.0
                },
                "context_gaps": [],
                "panic_clusters": [],
                "incident_clusters": []
            }

    def _create_analysis_prompt(self, prs: List[Dict], issues: List[Dict]) -> str:
        """Create the Gemini analysis prompt."""
        prompt = f"""You are a DevOps Forensic Analyst. I will provide a JSON log of the last {len(prs)} PRs and {len(issues)} Issues for a repository.

**PR Data:**
{json.dumps(prs, indent=2)}

**Issue Data:**
{json.dumps(issues, indent=2)}

**Task 1: Classify every PR into one of these buckets:**
- `FEATURE`: New functionality, new component, major enhancement
- `CHORE`: Dependencies updates, minor styling, refactoring, documentation, configuration
- `REVERT`: Explicit rollback (look for 'Revert', 'Undo', 'Rollback' in title)
- `HOTFIX`: Urgent fix for a recent bug (look for 'fix', 'bug', 'panic', 'broken', 'regression', 'critical', 'urgent', 'hotfix' in title or labels)

**Task 2: Identify 'Context Gaps':**
- Flag instances where a `HOTFIX` was merged < 48 hours after a `FEATURE` affecting similar files or functionality.
- Identify 'Panic Spirals': 2+ Hotfixes/Reverts in a row (consecutive PRs).

**Task 3: Calculate the Firefighting Metrics:**
1. **Revert Rate**: (Count of `REVERT` PRs / Total PRs) × 100
2. **Hotfix Rate**: (Count of `HOTFIX` PRs / Total PRs) × 100
3. **Regression Ratio**: (Count of `HOTFIX` PRs / Count of `FEATURE` PRs)
4. **Reviewer Tax Estimate**: (Total Lines Changed in Hotfixes) / (Total Lines Changed in Features)

**Task 4: Identify Top 3 Incident Clusters:**
Find the 3 most critical 'Incident Clusters' - these are specific PR numbers that caused the most pain (e.g., a FEATURE that led to multiple HOTFIXEs/REVERTs).

**Output Format:**
Return ONLY a valid JSON object (no other text) with this exact structure:

{{
  "pr_classifications": [
    {{"number": 123, "type": "FEATURE", "reasoning": "Added new dashboard component"}},
    {{"number": 124, "type": "HOTFIX", "reasoning": "Fixed crash from PR #123"}}
  ],
  "metrics": {{
    "revert_rate": 5.2,
    "hotfix_rate": 15.3,
    "regression_ratio": 0.45,
    "reviewer_tax": 0.32
  }},
  "context_gaps": [
    {{"feature_pr": 123, "hotfix_pr": 124, "time_gap_hours": 12}}
  ],
  "panic_clusters": [
    {{"prs": [123, 124, 125], "description": "Dashboard feature caused cascading failures"}}
  ],
  "incident_clusters": [
    {{
      "feature_pr": 123,
      "related_fixes": [124, 125, 126],
      "severity": "high",
      "description": "Dashboard component introduced 3 follow-up fixes"
    }}
  ]
}}

Analyze the data and return the JSON."""

        return prompt

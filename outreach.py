"""Email outreach generator for target repositories."""

from typing import Dict, List


class OutreachGenerator:
    """Generate personalized outreach emails based on analysis."""

    @staticmethod
    def generate_email(repo_data: Dict, analysis: Dict, score: Dict) -> str:
        """
        Generate a personalized outreach email.

        Args:
            repo_data: Repository information
            analysis: Gemini analysis results
            score: Firefighting score results

        Returns:
            Email template as string
        """
        owner = repo_data["owner"]
        repo = repo_data["repo"]

        metrics = score["metrics"]
        incident_clusters = analysis.get("incident_clusters", [])[:3]  # Top 3

        # Build the specific PR references
        pr_examples = []
        if incident_clusters:
            for cluster in incident_clusters[:2]:  # Use top 2 for email
                feature_pr = cluster.get("feature_pr")
                related_fixes = cluster.get("related_fixes", [])
                if feature_pr and related_fixes:
                    pr_examples.append(f"PR #{feature_pr} → Fixes: {', '.join(['#' + str(pr) for pr in related_fixes[:3]])}")

        pr_reference = pr_examples[0] if pr_examples else "recent PRs"

        # Calculate comparison to baseline (DORA Elite is typically <5% revert rate)
        baseline_revert = 5.0
        revert_multiplier = metrics["revert_rate"] / baseline_revert if baseline_revert > 0 else 1.0

        email = f"""Subject: Analysis of reverts in {repo} ({pr_reference})

Hi [Engineering Lead/CTO],

I'm researching "Context Collapse" in fast-growing engineering teams for a thesis I'm publishing.

I ran a forensic analysis on the last 30 days of `{owner}/{repo}`'s activity to measure your Code Lineage Quality Score (CLQS). I noticed a specific pattern in your "firefighting" metrics:

**Key Findings:**

• **Revert Rate:** You're at {metrics['revert_rate']:.1f}%, which is {revert_multiplier:.1f}x higher than the DORA "Elite" baseline (<5%).
• **Hotfix Rate:** {metrics['hotfix_rate']:.1f}% of your recent PRs are urgent fixes for bugs introduced by recent changes.
• **Regression Ratio:** You're merging {metrics['regression_ratio']:.2f} hotfixes for every feature (ideal is <0.1).
"""

        if pr_examples:
            email += f"""
**Specific Incident Patterns:**
"""
            for example in pr_examples[:2]:
                email += f"• {example}\n"

        if analysis.get("panic_clusters"):
            email += f"\n• **\"Panic Spirals\":** {len(analysis['panic_clusters'])} instances of cascading hotfixes detected.\n"

        email += f"""
It looks like the context on those legacy files didn't travel to the new authors, causing regressions that passed code review.

I'm building **CodeRisk** to catch exactly these types of "Context Rot" bugs pre-commit by analyzing:
- Historical ownership patterns
- Change velocity correlations
- Cross-file dependency risks
- Developer context mismatches

I'd love to run a full 2-week audit on your repo (free) to see if we can lower that Revert Rate and save your team review time.

If you're open to it, I can send over the full CLQS report I generated with specific recommendations?

Best,
Rohan Katakam
Founder, CodeRisk

---

**Why this matters:**
Your Firefighting Score is {score['firefighting_score']:.1f} ({score['priority']})

Each revert costs your team:
• ~4 hours of debugging time
• ~2 hours of review/fix time
• ~1 hour of deployment overhead
• Lost velocity and team morale

At {metrics['revert_rate']:.1f}% revert rate on ~100 PRs/month, you're losing ~{int(metrics['revert_rate'])} × 7 hours = ~{int(metrics['revert_rate'] * 7)} engineering hours/month to firefighting.

P.S. - Blog post on "The AI-Accelerated Bottleneck" available at: [Link]
"""

        return email

    @staticmethod
    def generate_summary_report(analysis: Dict, score: Dict) -> str:
        """
        Generate a summary report for internal use.

        Args:
            analysis: Gemini analysis results
            score: Firefighting score results

        Returns:
            Formatted summary report
        """
        metrics = score["metrics"]
        incident_clusters = analysis.get("incident_clusters", [])

        report = f"""
=== FIREFIGHTING SCORE ANALYSIS ===

Overall Score: {score['firefighting_score']:.2f}
Priority: {score['priority']}

--- Score Components ---
Revert Contribution:  {score['components']['revert_contribution']:.2f}
Hotfix Contribution:  {score['components']['hotfix_contribution']:.2f}
Panic Contribution:   {score['components']['panic_contribution']:.2f}

--- Metrics ---
Revert Rate:          {metrics['revert_rate']:.2f}%
Hotfix Rate:          {metrics['hotfix_rate']:.2f}%
Regression Ratio:     {metrics['regression_ratio']:.2f}
Reviewer Tax:         {metrics['reviewer_tax']:.2f}
Panic Clusters:       {metrics['panic_cluster_count']}

--- Top Incident Clusters ---
"""

        for i, cluster in enumerate(incident_clusters[:3], 1):
            report += f"\n{i}. Feature PR #{cluster.get('feature_pr')} → Fixes: {cluster.get('related_fixes', [])}\n"
            report += f"   Severity: {cluster.get('severity', 'unknown')}\n"
            report += f"   {cluster.get('description', 'No description')}\n"

        return report

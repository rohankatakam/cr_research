#!/usr/bin/env python3
"""Main orchestrator for Repo Sniper GTM strategy."""

import json
import sys
from pathlib import Path
from github_client import GitHubClient
from gemini_analyzer import GeminiAnalyzer
from scoring import ScoringEngine
from outreach import OutreachGenerator
import config


def analyze_single_repository(owner: str, repo: str) -> dict:
    """
    Analyze a single repository and generate results.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Complete analysis result
    """
    print(f"\n{'=' * 60}")
    print(f"ANALYZING: {owner}/{repo}")
    print(f"{'=' * 60}")

    # Initialize clients
    github_client = GitHubClient(config.GITHUB_TOKEN)
    gemini_analyzer = GeminiAnalyzer(config.GEMINI_API_KEY)
    scoring_engine = ScoringEngine()
    outreach_gen = OutreachGenerator()

    # Step 1: Fetch GitHub data
    try:
        repo_data = github_client.get_repository_data(owner, repo)
    except Exception as e:
        print(f"ERROR fetching GitHub data: {e}")
        return None

    # Check if we have enough data
    if len(repo_data["pull_requests"]) < config.MIN_PRS_REQUIRED:
        print(f"SKIP: Only {len(repo_data['pull_requests'])} PRs found (minimum {config.MIN_PRS_REQUIRED} required)")
        return None

    # Step 2: Analyze with Gemini
    try:
        analysis = gemini_analyzer.analyze_repository(repo_data)
    except Exception as e:
        print(f"ERROR during Gemini analysis: {e}")
        return None

    # Step 3: Calculate Firefighting Score
    score = scoring_engine.calculate_firefighting_score(analysis)

    print(f"\n{'=' * 60}")
    print(f"RESULTS FOR {owner}/{repo}")
    print(f"{'=' * 60}")
    print(f"Firefighting Score: {score['firefighting_score']}")
    print(f"Priority: {score['priority']}")
    print(f"\nScore Breakdown:")
    print(f"  Revert Contribution: {score['components']['revert_contribution']}")
    print(f"  Hotfix Contribution: {score['components']['hotfix_contribution']}")
    print(f"  Panic Contribution: {score['components']['panic_contribution']}")

    # Step 4: Generate outputs
    email = outreach_gen.generate_email(repo_data, analysis, score)
    summary_report = outreach_gen.generate_summary_report(analysis, score)

    # Prepare result
    result = {
        "owner": owner,
        "repo": repo,
        "full_name": f"{owner}/{repo}",
        "score": score,
        "analysis": analysis,
        "email": email,
        "summary": summary_report
    }

    # Step 5: Save results
    save_results(result)

    return result


def save_results(result: dict):
    """Save analysis results to files."""
    owner = result["owner"]
    repo = result["repo"]
    results_dir = Path("data/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save full JSON
    json_path = results_dir / f"{owner}_{repo}_analysis.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    # Save email template
    email_path = results_dir / f"{owner}_{repo}_outreach.txt"
    with open(email_path, "w") as f:
        f.write(result["email"])

    # Save summary report
    summary_path = results_dir / f"{owner}_{repo}_summary.txt"
    with open(summary_path, "w") as f:
        f.write(result["summary"])

    print(f"\nResults saved to:")
    print(f"  JSON:    {json_path}")
    print(f"  Email:   {email_path}")
    print(f"  Summary: {summary_path}")


def analyze_multiple_repositories(repo_list_path: str = "data/target_repos.json"):
    """
    Analyze multiple repositories from a target list.

    Args:
        repo_list_path: Path to JSON file containing list of repos
    """
    # Load target repos
    try:
        with open(repo_list_path, "r") as f:
            repos = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Target repos file not found at {repo_list_path}")
        print("Please create the file with format: [{\"owner\": \"x\", \"repo\": \"y\"}, ...]")
        return

    print(f"Loaded {len(repos)} target repositories")

    results = []

    # Analyze each repo
    for repo_info in repos:
        owner = repo_info["owner"]
        repo = repo_info["repo"]

        result = analyze_single_repository(owner, repo)
        if result:
            results.append(result)

        print("\n" + "=" * 60 + "\n")

    # Rank results
    if results:
        ranked = ScoringEngine.rank_repositories(results)

        print("\n" + "=" * 60)
        print("RANKED RESULTS (Top to Bottom)")
        print("=" * 60)

        for i, result in enumerate(ranked, 1):
            print(f"\n{i}. {result['full_name']}")
            print(f"   Score: {result['score']['firefighting_score']}")
            print(f"   Priority: {result['score']['priority']}")

        # Save ranked results
        ranked_path = Path("data/results/ranked_scores.json")
        with open(ranked_path, "w") as f:
            json.dump([{
                "rank": i,
                "repo": r["full_name"],
                "score": r["score"]["firefighting_score"],
                "priority": r["score"]["priority"]
            } for i, r in enumerate(ranked, 1)], f, indent=2)

        print(f"\nRanked scores saved to: {ranked_path}")

        # Show top 5 priority targets
        priority_1 = ScoringEngine.get_priority_targets(ranked, min_priority=1)
        if priority_1:
            print(f"\n{'=' * 60}")
            print(f"TOP PRIORITY 1 TARGETS (Send emails to these!)")
            print(f"{'=' * 60}")
            for result in priority_1[:5]:
                print(f"\n• {result['full_name']}")
                print(f"  Score: {result['score']['firefighting_score']}")
                print(f"  Email: data/results/{result['owner']}_{result['repo']}_outreach.txt")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Single repo mode: python main.py owner/repo
        if "/" in sys.argv[1]:
            owner, repo = sys.argv[1].split("/")
            analyze_single_repository(owner, repo)
        else:
            print("Usage: python main.py [owner/repo]")
            print("   or: python main.py (to analyze all repos in data/target_repos.json)")
    else:
        # Batch mode
        analyze_multiple_repositories()


if __name__ == "__main__":
    main()

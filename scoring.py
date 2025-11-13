"""Scoring engine for calculating Firefighting Scores."""

from typing import Dict
import config


class ScoringEngine:
    """Calculate and rank repositories by Firefighting Score."""

    @staticmethod
    def calculate_firefighting_score(analysis: Dict) -> Dict:
        """
        Calculate the Firefighting Score (S_F).

        Formula: S_F = (W_R × RevertRate) + (W_H × HotfixRate) + (W_C × PanicClusterCount)

        Args:
            analysis: Analysis results from Gemini

        Returns:
            Dictionary with score and components
        """
        metrics = analysis.get("metrics", {})
        panic_clusters = analysis.get("panic_clusters", [])

        revert_rate = metrics.get("revert_rate", 0.0)
        hotfix_rate = metrics.get("hotfix_rate", 0.0)
        panic_cluster_count = len(panic_clusters)

        # Calculate weighted score
        score = (
            config.WEIGHT_REVERT * revert_rate +
            config.WEIGHT_HOTFIX * hotfix_rate +
            config.WEIGHT_PANIC_CLUSTER * panic_cluster_count
        )

        # Determine priority level
        if score >= config.PRIORITY_1_THRESHOLD:
            priority = "Priority 1: The Bleeding"
        elif score >= config.PRIORITY_2_THRESHOLD:
            priority = "Priority 2: The Worried"
        else:
            priority = "Ignore: Too Healthy"

        return {
            "firefighting_score": round(score, 2),
            "priority": priority,
            "components": {
                "revert_contribution": round(config.WEIGHT_REVERT * revert_rate, 2),
                "hotfix_contribution": round(config.WEIGHT_HOTFIX * hotfix_rate, 2),
                "panic_contribution": round(config.WEIGHT_PANIC_CLUSTER * panic_cluster_count, 2)
            },
            "metrics": {
                "revert_rate": revert_rate,
                "hotfix_rate": hotfix_rate,
                "regression_ratio": metrics.get("regression_ratio", 0.0),
                "reviewer_tax": metrics.get("reviewer_tax", 0.0),
                "panic_cluster_count": panic_cluster_count
            }
        }

    @staticmethod
    def rank_repositories(results: list) -> list:
        """
        Rank repositories by Firefighting Score.

        Args:
            results: List of analysis results with scores

        Returns:
            Sorted list (highest score first)
        """
        return sorted(results, key=lambda x: x["score"]["firefighting_score"], reverse=True)

    @staticmethod
    def get_priority_targets(results: list, min_priority: int = 1) -> list:
        """
        Filter repositories by priority level.

        Args:
            results: List of analysis results
            min_priority: 1 for Priority 1+, 2 for Priority 2+

        Returns:
            Filtered list
        """
        if min_priority == 1:
            threshold = config.PRIORITY_1_THRESHOLD
        else:
            threshold = config.PRIORITY_2_THRESHOLD

        return [r for r in results if r["score"]["firefighting_score"] >= threshold]

"""GitHub GraphQL API client with rate limiting and pagination."""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config


class GitHubClient:
    """Client for interacting with GitHub's GraphQL API."""

    def __init__(self, token: str):
        self.token = token
        self.url = config.GITHUB_GRAPHQL_URL
        self.headers = {
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json"
        }
        self.rate_limit_remaining = None
        self.rate_limit_reset_at = None

    def _execute_query(self, query: str, variables: Dict) -> Dict:
        """Execute a GraphQL query with error handling."""
        payload = {
            "query": query,
            "variables": variables
        }

        response = requests.post(self.url, json=payload, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"GraphQL query failed: {response.status_code} - {response.text}")

        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")

        # Update rate limit info
        if "data" in data and "rateLimit" in data["data"]:
            rate_limit = data["data"]["rateLimit"]
            self.rate_limit_remaining = rate_limit["remaining"]
            self.rate_limit_reset_at = rate_limit["resetAt"]

            print(f"Rate limit: {self.rate_limit_remaining} points remaining")

            # Check if we need to wait
            if self.rate_limit_remaining < config.GITHUB_RATE_LIMIT_THRESHOLD:
                reset_time = datetime.fromisoformat(self.rate_limit_reset_at.replace("Z", "+00:00"))
                wait_seconds = (reset_time - datetime.now(reset_time.tzinfo)).total_seconds() + 5
                if wait_seconds > 0:
                    print(f"Rate limit low. Waiting {wait_seconds:.0f} seconds...")
                    time.sleep(wait_seconds)

        return data["data"]

    def get_repository_data(self, owner: str, repo: str) -> Dict:
        """
        Fetch PR and Issue data for a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with PRs and Issues data
        """
        print(f"\nFetching data for {owner}/{repo}...")

        # Calculate date for lookback period
        since_date = (datetime.now() - timedelta(days=config.DAYS_LOOKBACK)).isoformat()

        # Fetch PRs (up to 100)
        prs = self._fetch_pull_requests(owner, repo)

        # Fetch Issues (up to 100)
        issues = self._fetch_issues(owner, repo)

        print(f"Fetched {len(prs)} PRs and {len(issues)} issues")

        return {
            "owner": owner,
            "repo": repo,
            "pull_requests": prs,
            "issues": issues
        }

    def _fetch_pull_requests(self, owner: str, repo: str) -> List[Dict]:
        """Fetch merged and closed pull requests."""
        query = """
        query GetPullRequests($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequests(
              first: 100,
              after: $cursor,
              states: [MERGED, CLOSED],
              orderBy: {field: UPDATED_AT, direction: DESC}
            ) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                node {
                  number
                  title
                  body
                  state
                  merged
                  mergedAt
                  createdAt
                  updatedAt
                  closedAt
                  author {
                    login
                  }
                  additions
                  deletions
                  changedFiles
                  baseRefName
                  headRefName
                  labels(first: 10) {
                    edges {
                      node {
                        name
                      }
                    }
                  }
                  comments(first: 1) {
                    totalCount
                  }
                }
              }
            }
          }
          rateLimit {
            limit
            remaining
            resetAt
            cost
          }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "cursor": None
        }

        all_prs = []

        # Fetch first page
        data = self._execute_query(query, variables)
        pr_data = data["repository"]["pullRequests"]

        for edge in pr_data["edges"]:
            pr = edge["node"]
            # Extract labels
            pr["labels"] = [label["node"]["name"] for label in pr["labels"]["edges"]]
            pr["comment_count"] = pr["comments"]["totalCount"]
            del pr["comments"]
            all_prs.append(pr)

        # For now, we only fetch first 100 PRs (one page)
        # Can add pagination loop if needed

        return all_prs

    def _fetch_issues(self, owner: str, repo: str) -> List[Dict]:
        """Fetch closed issues."""
        query = """
        query GetIssues($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            issues(
              first: 100,
              after: $cursor,
              states: [CLOSED],
              orderBy: {field: UPDATED_AT, direction: DESC}
            ) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                node {
                  number
                  title
                  body
                  state
                  createdAt
                  updatedAt
                  closedAt
                  author {
                    login
                  }
                  labels(first: 10) {
                    edges {
                      node {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
          rateLimit {
            limit
            remaining
            resetAt
            cost
          }
        }
        """

        variables = {
            "owner": owner,
            "repo": repo,
            "cursor": None
        }

        all_issues = []

        # Fetch first page
        data = self._execute_query(query, variables)
        issue_data = data["repository"]["issues"]

        for edge in issue_data["edges"]:
            issue = edge["node"]
            # Extract labels
            issue["labels"] = [label["node"]["name"] for label in issue["labels"]["edges"]]
            all_issues.append(issue)

        return all_issues

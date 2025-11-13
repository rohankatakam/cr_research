"""Configuration and constants for Repo Sniper GTM tool."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GitHub GraphQL API
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# Rate Limits
GITHUB_RATE_LIMIT_THRESHOLD = 500  # Stop if remaining points < 500
GITHUB_MAX_PRS_PER_QUERY = 100
GITHUB_MAX_ISSUES_PER_QUERY = 100

# Scoring Weights
WEIGHT_REVERT = 5.0
WEIGHT_HOTFIX = 2.0
WEIGHT_PANIC_CLUSTER = 10.0

# Score Thresholds
PRIORITY_1_THRESHOLD = 50.0  # The Bleeding
PRIORITY_2_THRESHOLD = 20.0  # The Worried

# Gemini Model
GEMINI_MODEL = "gemini-2.5-flash"

# Analysis Parameters
DAYS_LOOKBACK = 30
MIN_PRS_REQUIRED = 20  # Skip repos with fewer than this many PRs

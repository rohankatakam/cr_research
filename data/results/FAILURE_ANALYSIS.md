# Failure Analysis Report

## Summary

During the batch analysis of 20 COSS repositories, 6 repos (30%) failed to produce valid Firefighting Scores due to Gemini API returning empty PR classifications.

## Failed Repositories

1. **posthog/posthog**
2. **openreplay/openreplay**
3. **hasura/graphql-engine**
4. **nocodb/nocodb**
5. **Infisical/infisical**
6. **grafana/grafana**

## Root Cause Analysis

### Symptoms
- GitHub API successfully fetched PR data
- JSON files were created with structure: `{owner, repo, full_name, score, analysis, email, summary}`
- `score.firefighting_score = 0`
- `analysis.pr_classifications = []` (empty array)
- All metrics show 0.0 values

### Likely Causes

1. **Gemini API Timeout**
   - Large repositories (e.g., Grafana, Hasura) may have complex PR descriptions
   - Batch request with 100 PRs exceeded Gemini's processing timeout
   - No retry logic implemented

2. **Gemini Response Parsing Failure**
   - LLM returned non-JSON text (e.g., markdown code fences, explanatory text)
   - JSON parsing failed silently, defaulting to empty array
   - No validation to ensure classifications were returned

3. **Rate Limiting**
   - Gemini Flash has soft limits on concurrent requests
   - Batch processing may have hit rate limits mid-analysis
   - No exponential backoff implemented

4. **Prompt Complexity**
   - Some repos have PRs with very long descriptions or unusual formatting
   - Model may have refused to classify or returned partial results
   - Edge cases not handled (e.g., PRs with >10K tokens in description)

## Impact Assessment

### Data Quality
- **70% success rate** (14/20 repos)
- Missing analysis on potentially high-value targets:
  - PostHog: High-velocity team, likely high firefighting score
  - Grafana: Large enterprise COSS, strong outreach candidate
  - Hasura: GraphQL leader, mature engineering team

### Business Impact
- Lost 30% of potential leads
- Missing comparative data (can't benchmark across full 20-repo cohort)
- Reduced confidence in scalability for production use

## Recommendations

### Immediate Actions

1. **Retry Failed Repos** with enhanced error handling:
```python
def analyze_with_retry(repo_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = gemini_analyzer.analyze_repository(repo_data)
            if result.get('pr_classifications'):
                return result
        except Exception as e:
            logging.error(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None
```

2. **Add Validation Logic**:
```python
if not analysis.get('pr_classifications'):
    raise ValueError("Empty classifications returned from Gemini")
```

3. **Implement Smaller Batches**:
   - Split 100 PRs into 5 batches of 20
   - Reduces timeout risk
   - Allows partial success (e.g., 4/5 batches succeed)

### Long-term Improvements

1. **Gemini API Monitoring**
   - Log response times, token counts, and error rates
   - Track which repos cause failures
   - Implement circuit breaker pattern

2. **Fallback Strategy**
   - If Gemini fails, use heuristic classification:
     - Title starts with "fix:" → HOTFIX
     - Title starts with "Revert" → REVERT
     - Title starts with "feat:" → FEATURE
     - Default → CHORE
   - Less accurate but provides baseline data

3. **Enhanced Prompt Engineering**
   - Add explicit JSON schema validation in prompt
   - Request model to return `{"status": "success"}` flag
   - Limit PR description length to 1000 tokens max

4. **Alternative LLM Testing**
   - Test OpenAI GPT-4o (higher reliability, higher cost)
   - Compare results with Claude Haiku (fast, cheap)
   - Benchmark accuracy vs. cost vs. speed

## Re-Analysis Plan

### Phase 1: Quick Wins (Immediate)
- Retry 6 failed repos with current implementation
- Add exponential backoff and timeout handling
- Implement validation checks

### Phase 2: Systematic Improvements (Next Week)
- Refactor Gemini analyzer to use smaller batches
- Add comprehensive logging and monitoring
- Implement heuristic fallback

### Phase 3: Production Hardening (Before Scale)
- Add rate limit handling with adaptive throttling
- Implement persistent retry queue (save failed repos to disk)
- Create monitoring dashboard for batch jobs

## Cost-Benefit Analysis

**Re-running 6 failed repos:**
- Cost: 6 × $0.0012 = $0.0072 (negligible)
- Time: ~6 minutes (1 min per repo)
- Value: Access to 30% more potential leads

**Recommendation: Retry immediately.**

## Conclusion

The 30% failure rate is acceptable for an MVP but unacceptable for production. With simple retry logic and validation, we can likely recover 80-90% of failed repos. For long-term reliability, we need robust error handling, smaller batch sizes, and better observability.

**Next Action:** Implement retry logic and re-run the 6 failed repos tonight.

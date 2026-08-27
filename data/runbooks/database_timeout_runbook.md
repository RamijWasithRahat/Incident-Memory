# Database Timeout Troubleshooting Runbook

## Summary

Use this runbook when an application reports database connection timeouts, unusually high query latency, or failures acquiring database connections.

## Symptoms

- API requests become slow.
- PostgreSQL connection timeout messages appear.
- Connection pool utilization approaches its maximum.
- Errors increase after deployment or traffic spikes.

## Checks

1. Check active PostgreSQL connections.
2. Check application connection pool utilization.
3. Compare worker concurrency with pool capacity.
4. Review recently deployed database queries.
5. Check for long-running or blocked transactions.

## Root Cause

Common historical causes include connection pool exhaustion, unexpectedly high worker concurrency, blocked transactions, and expensive database queries.

## Resolution

Reduce unnecessary worker concurrency, terminate blocked transactions when appropriate, optimize expensive queries, and adjust database pool capacity based on measured demand.

## Verification

Confirm API latency returns to normal, database timeout errors stop increasing, and connection pool utilization remains below the configured maximum.

## Prevention

Add alerts for connection pool utilization and review database-related deployment configuration before production releases.

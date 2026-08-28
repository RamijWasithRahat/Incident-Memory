# Incident Memory - Manual RAG Generation Evaluation

## Purpose

This checklist evaluates the grounded-generation behavior of Incident Memory.

Retrieval quality is measured automatically using Top-3 Retrieval Success.
These checks evaluate whether the local Qwen model uses retrieved evidence safely.

---

## Check 1 - Historical Root Cause

### Question

What caused INC-012?

### Expected behavior

- The answer should use retrieved INC-012 evidence.
- The answer should identify the historical root cause.
- The answer should contain at least one valid source citation such as `[S1]`.
- The cited source should correspond to INC-012.
- The answer must not introduce unsupported incident facts.

### Result

- [ ] PASS
- [ ] FAIL

### Notes

---

## Check 2 - Historical Solution

### Question

How was payment DB pool exhaustion solved?

### Expected behavior

- The answer should retrieve INC-012 solution evidence.
- The answer should describe the historical resolution.
- The answer should cite the supporting source.
- The answer should not add unsupported remediation steps.

### Result

- [ ] PASS
- [ ] FAIL

### Notes

---

## Check 3 - Similar Current Incident

### Question

Payment service became slow after deployment and logs show database timeout. Have we seen something similar?

### Expected behavior

- INC-012 should appear as relevant evidence.
- The answer may describe the historical connection-pool problem.
- The answer must clearly state that historical similarity does not prove the same current root cause.
- Specific historical claims should have source citations.

### Result

- [ ] PASS
- [ ] FAIL

### Notes

---

## Check 4 - Insufficient Evidence

### Question

What caused a Mars spacecraft navigation failure?

### Expected behavior

- The system should not invent an incident.
- The response should state that there is insufficient historical evidence.
- `insufficient_evidence` should be `true`.
- No fabricated incident ID should appear.

### Result

- [ ] PASS
- [ ] FAIL

### Notes

---

## Check 5 - Runbook Evidence

### Question

What checks should I perform for database timeout problems?

### Expected behavior

- The database timeout runbook should be retrieved.
- The answer should use the `checks` section where relevant.
- The answer should cite the runbook source.
- The answer should not invent checks that are absent from retrieved evidence.

### Result

- [ ] PASS
- [ ] FAIL

### Notes

---

# Final Manual Summary

| Check                           | Result      |
| ------------------------------- | ----------- |
| Historical root cause grounding | PASS / FAIL |
| Historical solution grounding   | PASS / FAIL |
| Similar-incident uncertainty    | PASS / FAIL |
| Insufficient-evidence behavior  | PASS / FAIL |
| Runbook grounding               | PASS / FAIL |

## Overall Notes

Complete this section after manually testing the RAG endpoint.

# Common Failures

## Constitutional Violations (Architecture Test Failures)

| Failure | Symptom | Cause | Resolution |
|---------|---------|-------|------------|
| Domain imports engine | ImportError in domain | Engine import in domain file | Remove import; engine logic belongs in engine |
| Domain mutates state | Frozen dataclass error | Mutation method in domain | Remove mutation; use supersession |
| Engine imports evaluation | ImportError | Evaluation import in proposal | Remove import; use identifiers only |
| Proposal has score field | AttributeError | `confidence:` field in Proposal | Remove field; P-3 violation |
| Evaluation ranks proposals | Test failure | `rank` method in EvaluationSpace | Remove method; E-9 violation |
| Execution has retry logic | Test failure | `retry_count` in ExecutionResult | Remove field; X-12 violation |

---

## Common Implementation Errors

| Error | Detection | Fix |
|-------|-----------|-----|
| Missing `frozen=True` | `test_all_models_frozen` fails | Add `frozen=True` to dataclass |
| Mutation method in domain | `test_no_mutation_methods` fails | Remove method; use supersession |
| Execution imports governance | `test_no_governance_imports` fails | Remove import; use identifiers only |
| Proposal has `decision_id` | `test_no_proposal_imports` fails | Remove field; P-7 violation |
| Evaluation has `approved` field | `test_no_decision_fields` fails | Remove field; E-6 violation |

---

## Traceability Gaps

| Missing Link | Symptom | Fix |
|--------------|---------|-----|
| Proposal missing `problem_id` | Traceability test fails | Add `originating_problem_id` to Proposal |
| Evaluation missing `proposal_id` | Traceability test fails | Add `proposal_id` to Evaluation |
| Governance missing `evaluation_id` | Traceability test fails | Add `evaluation_id` to GovernanceDecision |
| Authorization missing `decision_id` | Traceability test fails | Add `governance_decision_id` |
| Execution missing `token_id` | Traceability test fails | Add `authorization_token_id` |

---

## Dependency Violations

| Violation | Detection | Fix |
|-----------|-----------|-----|
| Domain imports application | `test_domain_purity` fails | Move code to application layer |
| Infrastructure imports engine | `test_infrastructure_isolation` fails | Remove import; use domain contracts |
| Engine imports runtime | `test_no_runtime_imports` fails | Remove import; use domain models only |
| Adapter imports engine | `test_adapter_boundary` fails | Remove import; use contracts only |

---

## Traceability Gaps

| Missing Link | Test | Fix |
|--------------|------|-----|
| ExecutionReceipt → ExecutionResult | `test_traceability_fields_exist` | Add `execution_result_id` to ExecutionReceipt |
| ExecutionResult → ExecutionPlan | `test_traceability_fields_exist` | Add `execution_plan_id` to ExecutionResult |
| ExecutionPlan → AuthorizationToken | `test_traceability_fields_exist` | Add `authorization_token_id` to ExecutionPlan |
| AuthorizationToken → AuthorizationRecord | `test_traceability_fields_exist` | Add `authorization_record_id` to AuthorizationToken |
| AuthorizationRecord → GovernanceDecision | `test_traceability_fields_exist` | Add `governance_decision_id` to AuthorizationRecord |
| GovernanceDecision → Evaluation | `test_traceability_fields_exist` | Add `evaluation_id` to GovernanceDecision |
| Evaluation → Proposal | `test_traceability_fields_exist` | Add `proposal_id` to Evaluation |
| Proposal → Problem | `test_traceability_fields_exist` | Add `originating_problem_id` to Proposal |
| Problem → Observation | `test_traceability_fields_exist` | Add `observation_ids` to ProblemStatement |
| Hypothesis → Observation | `test_traceability_fields_exist` | Add `supporting_observation_ids` to Hypothesis |

---

## Common Test Failures & Fixes

| Test | Common Failure | Fix |
|------|----------------|-----|
| `test_full_brain_graph_is_acyclic` | Cycle detected | Remove backward import |
| `test_no_downward_dependencies` | Upward dependency | Reverse dependency direction |
| `test_domain_imports_only_stdlib` | Domain imports engine | Move code to engine layer |
| `test_no_mutation_methods` | Method starts with mutate/update | Remove method; use supersession |
| `test_no_evaluation_imports` | Governance imports evaluation | Remove import; use IDs only |
| `test_no_proposal_imports` | Governance imports proposal | Remove import; use IDs only |

---

## Quick Debug Checklist

When architecture test fails:

1. **Read the error message** — it identifies the exact constitutional law violated
2. **Find the file** — error shows exact file and line
3. **Check constitutional law** — match test name to law (e.g., `test_no_decision_fields` → E-6)
4. **Fix minimal change** — remove field, remove import, remove method
5. **Re-run test** — verify pass
6. **Run full suite** — ensure no regressions

---

## Emergency Quick Fixes

| Emergency | Quick Fix |
|-----------|-----------|
| Circular dependency | Reverse one dependency; add interface in domain |
| Frozen dataclass mutation | Remove method; create new instance via supersession |
| Missing traceability field | Add UUID field to model; propagate in engine |
| Forbidden import | Remove import; use identifier only (UUID) |
| Duplicate class | Remove legacy file (e.g., evolution_domain) |
| Missing traceability link | Add UUID field; propagate through pipeline |
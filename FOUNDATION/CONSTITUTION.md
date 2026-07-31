# Hermes Constitution

## Preamble

This Constitution establishes the fundamental laws governing the Hermes cognitive architecture. It is the supreme law. No engine, no module, no configuration may violate it. Amendments require explicit constitutional process.

---

## Article I — The Cognitive Pipeline

### Section 1 — Immutable Pipeline Order
The cognitive pipeline is fixed and immutable:
```
Observation → Hypothesis → Problem → Proposal → Evaluation → Governance → Authorization → Execution
```
No stage may be skipped, reordered, merged, or bypassed.

### Section 2 — Stage Responsibility
Each stage has exactly one constitutional responsibility:
- **Observation**: Collect and record raw evidence
- **Hypothesis**: Generate competing explanations
- **Problem**: Formulate structured cognitive gaps
- **Proposal**: Express intent without implementation
- **Evaluation**: Analyze proposals analytically
- **Governance**: Decide constitutional permissibility
- **Authorization**: Grant constitutional permission
- **Execution**: Perform authorized actions only

### Section 3 — Immutable Transitions
Each stage produces exactly one artifact type consumed by exactly one next stage. No stage may produce artifacts for non-adjacent stages.

---

## Article II — Observation Constitution (O-1 through O-6)

| Law | Statement |
|-----|-----------|
| **O-1** | Observation describes facts only. No recommendations. |
| **O-2** | Observation contains no decisions. |
| **O-3** | Observation contains no decisions. |
| **O-4** | Observation cannot mutate observed systems. |
| **O-5** | Evidence and interpretation remain separate. |
| **O-6** | Observation does not create EvolutionProposal objects. |

---

## Article III — Hypothesis Constitution (H-1 through H-8)

| Law | Statement |
|-----|-----------|
| **H-1** | A Hypothesis is not a solution. It explains observations. It never recommends action. |
| **H-2** | Multiple hypotheses may originate from the same observations. Hermes must support competing explanations. |
| **H-3** | A ProblemStatement may reference multiple hypotheses. Problems are derived understanding, not raw evidence. |
| **H-4** | Observations remain immutable regardless of later conclusions. Changing a hypothesis must never modify observations. |
| **H-5** | Problems never contain implementation strategies. Forbidden: replace planner, modify retrieval, execute evolution, improve scoring. Allowed: planning quality degradation, retrieval inconsistency, execution instability. |
| **H-6** | Hypotheses never contain execution information. No mutation, execution, planner instructions, governance, approval, decision. |
| **H-7** | Hypothesis formulation remains independent from Proposal generation. |
| **H-8** | Every ProblemStatement must preserve traceability back to its supporting observations through hypotheses. |

---

## Article IV — Problem Constitution (P-1 through P-12)

| Law | Statement |
|-----|-----------|
| **P-1** | A Problem is a structured cognitive gap, not a solution. |
| **P-2** | A Problem references exactly one HypothesisSpace. |
| **P-3** | A ProblemStatement may reference multiple hypotheses. Problems are derived understanding, not raw evidence. |
| **P-4** | Observations remain immutable regardless of problem formulation. |
| **P-5** | Problems never contain implementation strategies. Forbidden: replace planner, modify retrieval, execute evolution, improve scoring. Allowed: planning quality degradation, retrieval inconsistency, execution instability. |
| **P-6** | Problems never contain execution information. No mutation, execution, planner instructions, governance, approval, decision. |
| **P-7** | Problem formulation remains independent from Proposal generation. |
| **P-8** | Every ProblemStatement must preserve traceability back to its supporting observations through hypotheses. |

---

## Article V — Proposal Constitution (P-1 through P-12)

| Law | Statement |
|-----|-----------|
| **P-1** | A Proposal is an idea, not a decision. It never indicates approval, rejection, acceptance, or recommendation. |
| **P-2** | Proposal expresses intent, not implementation. Good: "Improve retrieval prioritization." Bad: "Modify RetrievalEngine.score_documents()." No code-level details. No implementation strategies. |
| **P-3** | Proposal never evaluates itself. Forbidden: score, confidence, priority, ranking, severity, probability, usefulness. |
| **P-4** | Proposal never mutates Hermes. No execution. No repository mutation. No runtime behavior. |
| **P-5** | Proposal remains completely traceable. Every Proposal preserves references: Observation → Hypothesis Space → Problem Statement → Proposal. Traceability is immutable. |
| **P-6** | Proposal preserves uncertainty. A Proposal represents ONE possible improvement. Never THE improvement. |
| **P-7** | ProposalSpace owns alternatives. Multiple proposals may coexist. ProposalSpace never ranks, removes, filters, merges, or optimizes. |
| **P-8** | Proposal generation is creative. Evaluation is analytical. These are different cognitive responsibilities. No evaluation logic may appear anywhere in Proposal generation. |
| **P-9** | Proposal is unaware of Evaluation. No imports. No fields. No methods referencing Evaluation, Decision, Approval, Execution, Governance. |
| **P-10** | Proposal describes desired outcome. Not implementation mechanism. Good: "Reduce repeated computation." Bad: "Add LRU cache." |
| **P-11** | Proposal categories represent cognitive intent. Examples: Knowledge Improvement, Learning Improvement, Planning Improvement, Retrieval Improvement, Reflection Improvement, Evolution Improvement, Safety Improvement, Reliability Improvement, Performance Improvement, Explainability Improvement. Avoid implementation-oriented categories. |
| **P-12** | Proposal models are immutable domain objects. No mutation methods. No execution methods. No runtime behavior. |

---

## Article VI — Evaluation Constitution (E-1 through E-16)

| Law | Statement |
|-----|-----------|
| **E-1** | Evaluation ≠ Proposal. |
| **E-2** | Evaluation ≠ Decision. |
| **E-3** | Evaluation ≠ Execution. |
| **E-4** | Evaluation never mutates Proposal. |
| **E-5** | Evaluation never creates Proposal. |
| **E-6** | Evaluation preserves uncertainty. No score/confidence/ranking/approval fields. |
| **E-7** | Evaluation records explicit evidence. Every conclusion traces to evidence. |
| **E-8** | Tradeoffs remain explicit. Tradeoff objects with benefit/cost/dimension. |
| **E-9** | Evaluation never ranks. |
| **E-10** | Evaluation never filters. |
| **E-11** | Evaluation never approves. |
| **E-12** | Evaluation is deterministic. Same Proposal + Same Context = Same Evaluation. |
| **E-13** | Comparison ≠ Ranking. |
| **E-14** | Every proposal receives independent evaluation. |
| **E-15** | Evaluation history is immutable — superseded, never mutated. |
| **E-16** | Evaluation conclusions are explainable through evidence. |

---

## Article VII — Governance Constitution (G-1 through G-23)

| Law | Statement |
|-----|-----------|
| **G-1** | Governance consumes Evaluation only. |
| **G-2** | Governance never evaluates. |
| **G-3** | Governance never creates proposals. |
| **G-4** | Governance never executes. |
| **G-5** | Every decision references explicit evidence. |
| **G-6** | Every decision references constitutional policies. |
| **G-7** | Governance is deterministic. |
| **G-8** | Governance may defer decisions. |
| **G-9** | Rejected decisions remain immutable. |
| **G-10** | Every decision is explainable. |
| **G-11** | Governance never mutates Evaluation. |
| **G-12** | Governance never mutates Proposal. |
| **G-13** | One active decision per Evaluation. History preserves superseded decisions. |
| **G-14** | Decision history is immutable. |
| **G-15** | Constitution overrides optimization. |
| **G-16** | Governance never bypasses constitutional policy. |
| **G-17** | Governance never invents evidence. |
| **G-18** | Governance owns decisions only. Execution belongs elsewhere. |
| **G-19** | Governance never performs optimization. |
| **G-20** | Decision and Rationale are separate constitutional objects. |
| **G-21** | Policies are immutable. |
| **G-22** | Identical inputs always produce identical governance outcomes. |
| **G-23** | Governance never creates constitutional rules. It only applies existing ones. |

---

## Article VIII — Authorization Constitution (A-1 through A-16)

| Law | Statement |
|-----|-----------|
| **A-1** | Authorization consumes GovernanceDecision only. |
| **A-2** | Authorization owns permission only. |
| **A-3** | Authorization never evaluates. |
| **A-4** | Authorization never governs. |
| **A-5** | Authorization never executes. |
| **A-6** | Authorization is immutable. |
| **A-7** | Authorization is deterministic. |
| **A-8** | Authorization is superseded, never mutated. |
| **A-9** | Authorization preserves traceability. |
| **A-10** | Authorization never bypasses Governance. |
| **A-11** | Authorization never invents permission. |
| **A-12** | Authorization never authorizes constitutional violations. |
| **A-13** | Authorization never weakens constitutional policy. |
| **A-14** | Authorization lifecycle is independent from execution lifecycle. |
| **A-15** | Execution consumes AuthorizationToken only. |
| **A-16** | Authorization contains no execution metadata. |

---

## Article IX — Execution Constitution (X-1 through X-23)

| Law | Statement |
|-----|-----------|
| **X-1** | Execution consumes AuthorizationToken only. |
| **X-2** | Execution performs only approved work. |
| **X-3** | Execution never reasons. |
| **X-4** | Execution never evaluates. |
| **X-5** | Execution never governs. |
| **X-6** | Execution never authorizes. |
| **X-7** | Same ExecutionPlan + AuthorizationToken must always produce same ExecutionResult. |
| **X-8** | Execution never invents additional work. |
| **X-9** | Execution never expands execution scope. |
| **X-10** | Execution never modifies ExecutionPlan. |
| **X-11** | Execution failures are facts. Never recommendations. |
| **X-12** | Execution never retries autonomously. |
| **X-13** | Execution never performs recovery reasoning. |
| **X-14** | Execution always stops after reporting failure. |
| **X-15** | Execution reports observable facts only. It never manufactures reality. If something was not directly observed, it must not appear in ExecutionResult. |
| **X-16** | ExecutionResult never contains interpretation. |
| **X-17** | ExecutionResult becomes future Observation evidence. |
| **X-18** | Execution is immutable. |
| **X-19** | ExecutionHistory is append-only. |
| **X-20** | Execution owns execution only. No audit ownership. No observation ownership. No governance ownership. |
| **X-21** | ExecutionReceipt is proof, not reasoning. |
| **X-22** | Execution depends only on Authorization and the Domain layer. |
| **X-23** | Execution remains constitutionally minimal. Every field must answer: Is this strictly required to perform an already-authorized action? If not, it does not belong here. |

---

## Article X — Structural Invariants

| Invariant | Statement |
|-----------|-----------|
| **S-1** | Dependency graph is a DAG. No cycles. |
| **S-2** | Runtime is the composition root only. |
| **S-3** | Domain layer imports only stdlib and itself. |
| **S-4** | Infrastructure imports only Domain + stdlib. |
| **S-5** | Engines import only Domain, Infrastructure, other Engines. Never Application, Runtime, Adapter. |
| **S-6** | Application imports Engines, Domain, Adapter DTOs. Never Runtime, Infrastructure concrete. |
| **S-7** | Runtime is composition root only. May import anything for wiring. Contains no business logic. |
| **S-8** | Adapter imports Application (contracts), Domain, stdlib. Never Engines, Runtime, Infrastructure implementations. |
| **S-9** | Adapter boundary — DTOs are boundary contracts, not implementation. |
| **S-10** | Every mutable state has exactly one owner. |

---

## Article XI — Amendment Process

### Section 1 — Amendment Proposal
Any constitutional amendment must:
1. Identify the specific article/section to amend
2. Provide the exact text change
3. Justify why the constitution is insufficient without this change
5. Demonstrate no alternative exists within current constitution

### Section 2 — Amendment Review
Amendments require:
1. Architectural review demonstrating no alternative within current constitution
2. Impact analysis on all 8 pipeline stages
6. Traceability impact assessment
7. Engine contract impact assessment

### Section 3 — Amendment Ratification
Amendments require:
1. Explicit constitutional amendment document
2. Updated architecture tests
3. Updated engine contracts
4. Updated constitutional documentation

### Section 4 — Emergency Provisions
None. The constitution has no emergency suspension clause. If the constitution prevents necessary action, the constitution must be amended first.

---

## Article XII — Supremacy

This Constitution is the supreme law of Hermes. Any engine, module, configuration, or runtime behavior that contradicts it is invalid. No emergency powers. No temporary exceptions. No pragmatic exceptions.

**The Constitution is the architecture. The architecture is the Constitution.**

---

*Ratified: Milestone B.8 — Constitutional Certification*
*Effective: Immediately upon certification*
*Supersedes: All prior architectural understandings*
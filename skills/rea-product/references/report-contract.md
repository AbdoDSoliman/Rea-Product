# Analysis contract (version 1)

`prepare` creates `sources.json`, sampled video evidence, `PRODUCT.md` and an empty `analysis.json`. Complete the analysis as an agent after inspecting the inputs. All narrative values should use the report language.

The top-level analysis has:
- `version`: 1; `name`: product title; `language`: e.g. `ar` or `en`.
- `status`: `draft` until inspection and required sections are done; then `complete`. Complete refers to the analysis, not implementation or proven parity.
- `evidence`: nonempty array of `{id, source, locator, observation}`. IDs unique, e.g. E1. `source` is an input path or direct research URL; `locator` gives frame timestamp, image region, page heading/quote and retrieval date as appropriate. `observation` states only what was inspected. For additional screenshots, link the local artifact in this field.
- `claims`: nonempty array of `{id, statement, status, evidence, verification}`. Unique IDs, e.g. C1. `status`: observed/inferred/proposed/unknown. `evidence`: array of evidence IDs; observed/inferred require at least one. Inferred and unknown require a nonempty `verification` step. Inferred statements should include reasoning and meaningful alternatives.
- `sections`: object with all nine nonempty string values below. Write readable text, lists, contracts or pseudocode. HTML rendering preserves text and line breaks; it does not render embedded HTML or Markdown tables/diagrams. Link a separate diagram artifact if needed.
- `parity_tests`: nonempty array of `{feature, procedure, expected, status, result_evidence}`. `status`: not_run/passed/failed/blocked. Passed/failed require an actual execution artifact or measurement in `result_evidence`; don't mark plans as passed.

## Required sections

1. `overview`: product category, customer, value, differentiator, observed input/output, source coverage, fidelity target.
2. `experience`: end-to-end journey, features, screen or process states, edge cases; evidence IDs inline.
3. `components`: module-level breakdown with responsibilities, interfaces, dependencies, constraints and evidence status.
4. `architecture`: connected proposed architecture and alternatives; explicitly distinguish it from the unverified original internals.
5. `data_and_interfaces`: schemas/API contracts, BOM/physical interfaces or service handoff records, as appropriate. Use domain-relevant content instead of forcing a database onto everything.
6. `core_mechanism`: deepest technical explanation of the distinguishing mechanism, pseudocode/process, hard assumptions and experiments to resolve them.
7. `implementation`: proof-of-concept → MVP → parity milestones, ordered tasks, deliverables, roles, effort ranges and acceptance criteria. Include the parity matrix here and executable tests in `parity_tests`.
8. `resources_and_costs`: build vs buy, people/tools/data/materials, startup and recurring estimates with units, assumptions and dated sources; unknowns explicitly labeled.
9. `risks_and_unknowns`: unresolved facts, contradictory evidence, limits of observed sources, reproduction gaps and prioritized verification experiments.

Do not use placeholder prose to satisfy required fields. If a topic is inapplicable explain why briefly. Reports must be clear when only a single static image was inspected; never invent observed transitions.

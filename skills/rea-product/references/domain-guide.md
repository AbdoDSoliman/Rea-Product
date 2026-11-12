# Domain routes

Read only the applicable route; hybrid products need the connecting interfaces too.

## Software / SaaS / apps

Map screens, user roles, state transitions and error/empty/loading states. Separate interface appearance from actual product behavior. For each capability, specify client event → API/worker → persistent state → returned result. Provide entities with keys/relationships, sample request/response shapes, async jobs and consistency needs. Explain the distinguishing algorithm with pseudocode and realistic edge cases. Inspect public docs/repositories before attributing frameworks. A similar UI does not establish backend equivalence.

## AI products and emerging technology

Identify modality, preprocessing, retrieval/tools, model inference, postprocessing and human intervention. Distinguish wrapper/orchestration, fine-tuning and foundation-model training as competing hypotheses where evidence is weak. Specify an achievable implementation and its data requirements, evaluation dataset, quality metrics, latency, memory/compute, inference cost and failure modes. Record whether claimed demos are independent measurements, vendor claims or observed samples. For research, trace paper → method → implementation → weights/data availability → reproducibility gaps. Do not turn a polished demo into a claim that the technology is solved.

## Physical products / hardware

Decompose enclosure, mechanism, materials, electronics, sensors, actuator, control firmware, power and assembly only as applicable. Separate visible geometry from estimated dimensions and hidden parts. Label BOM entries as observed, candidate or unknown; attach sourcing evidence to exact part claims. Provide a proposed BOM with quantities and price assumptions, fabrication options, assembly order, firmware/control flow, tolerances that must be measured, and bench tests. State when CAD, a teardown, measurements or physical testing is necessary for an exact match. Do not infer safety certification or load/thermal performance from imagery.

## Services / operations

Map customer journey plus behind-the-scenes work: acquisition, intake, qualification, scheduling, fulfillment, QA, support, refunds and repeat use. Specify frontstage/backstage responsibilities, staffing, tools, handoffs, SOPs, queue/capacity assumptions and unit economics. A website only reveals the frontstage; distinguish proposed operations from observed practices. Define measurable acceptance criteria such as turnaround, defect rate and successful handoff, without inventing the original service's metrics.

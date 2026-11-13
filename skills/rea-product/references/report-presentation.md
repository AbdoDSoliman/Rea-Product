# Presenting a deep product teardown

The deliverable must be easy to inspect, not merely valid JSON rendered as a wall
of text. Default to the bundled dark editorial report: product imagery, clear
hierarchy, restrained accent colors, generous spacing and readable Arabic/RTL.
Respect a user's requested style rather than treating this palette as universal.

Use `presentation` in the report contract to author a short decision-led opening.
Choose a useful inspected product frame, not a logo by default. Use evidence-linked
cards for the real journey, module responsibilities, and phased build plan where
those help scanning. Do not hardcode Atlas features, example counts, costs or
milestones into reports for other products. Hardware and services need their own
mechanisms and process steps.

Keep summary text concise. Put complete technical reasoning, contracts, estimates,
qualifications and failures in the canonical nine sections; the renderer exposes
these under full-detail disclosures. Never lose evidence or promote an unknown to
observed while shortening prose. Keep actual test statuses visible and separate
report validation from product parity.

Add explicit `image` paths to evidence entries and link claims to evidence IDs.
Inspect each image used. Do not treat automatic frame extraction as visual review.
The report generator builds a separate evidence gallery with timestamps and source
links. Missing media must not remove the corresponding text or produce a broken
image. URL-only inputs should remain useful without a fabricated hero image.

Before delivery, render and review at desktop and narrow mobile widths. Check RTL,
mixed-direction identifiers and numeric ranges, image crops, long headings,
overflow, section anchors, disclosures, test filtering and print expansion. Keep
interactions keyboard-accessible and respect reduced motion. Use licensed local
fonts or system fallbacks; do not ship a font merely because it is installed.
If browser validation is unavailable, state that limitation rather than claiming
the visual result was inspected.

Use `python3 -m rea_product report <directory>` to regenerate from the analysis.
Implement reusable presentation fixes in `rea_product/rendering.py` and its assets,
rather than leaving them only in one generated HTML file. Keep user-specific
analysis and media out of the repository unless explicitly requested.

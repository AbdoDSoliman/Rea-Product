# Rea-Product

Product/service/technology reconstruction is the main workflow. Read `skills/rea-product/SKILL.md` for user analysis tasks. Use `python3 -m rea_product --help` from this checkout; preparation and report generation use the standard library, with ffmpeg/ffprobe for optional video sampling.

`rea_product/` contains intake/report tooling; the agent performs semantic analysis. `skills/rea-product/` defines the evidence and reconstruction workflow. `rea_video/` retains upstream video capabilities, whose user workflow remains in `skills/rea-video/SKILL.md`. Preserve upstream copyright/license notices.

For product tooling run `python3 -m unittest discover -s tests_product -v`. For changes to upstream analysis rules, also run upstream pytest/evaluation checks documented in `docs/UPSTREAM_AGENTS.md`. Do not overwrite user analysis output or commit credentials.

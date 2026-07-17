# Flight Data AI — Speaker Notes (Final PPT.pdf)

Talking points, not a script — say it in your own words. Rough timing for a ~5 min pitch.

## Slide 1 — Title (20s)
"We're Flight Data AI — 'Chat with flight data.' The idea: make flight choices clear through intelligent clarification, instead of dumping a raw table on the user." Introduce the team and mentor briefly.

## Slide 2 — The problem (30s)
Lead with the tagline: "too much flight information, not enough clear answers." Hit the three pain points with a concrete example each:
- Too many date options — scheduled vs. actual dates get confused.
- Complex flight status — codes like "NOT FINAL" or "CHRMINE" mean nothing to a normal user.
- No full picture — no single place shows a flight's current state end-to-end.

## Slide 3 — Architecture (45–60s)
Walk the 8-stage pipeline left to right, it's the core of the pitch:
1. **Live refresh** — pulls directly from data.gov.il's Ben Gurion flight board (real API, refreshes ~every 15 min), not a static file.
2. **Data health check** (decision gate) — row-count delta + a 20-minute freshness window; if it fails, retry the refresh before doing anything else.
3. **Clarification form** — blocking, in-chat: pick a category, then answer that category's own date/status/filter questions. Nothing is answered until this is done.
4. **Filter & compute** — renames/mirrors columns and applies the chosen filters.
5. **Validator** (decision gate) — independently recounts the same filters straight from the CSV and compares against the calculated answer; mismatch sends it back to the clarification stage.
6. **Design output** — rule-based chart selection (bar/donut/line/KPI/table) from the question's phrasing, no extra model call needed.
7. **Freshness footer** — always appends "data last updated," regardless of category.
8. **Answer delivered** — validated, chart-rendered response.

Emphasize: *every question re-enters at stage 1* — there's no stale-answer path.

## Slide 4 — Critical decision points (30s)
Three things make this trustworthy, not just chatty:
- **Data validation** — refuses to answer on stale or suspicious data.
- **Clarifying questions** — asks before assuming what the user meant.
- **Design output** — matches the chart to the question instead of always defaulting to a wall of text.

## Slide 5 — Live demo (60–90s)
Cue the recorded demo reel here. While it plays, narrate what's happening as it happens: "Watch it check the cache, validate the data, ask which category, and only then render the answer." Let the visuals do the work — don't over-narrate the chart reveals.

## Slide 6 — Challenges & learnings (30–40s)
Be honest about the rough edges — it builds credibility:
- Cache-aware refresh saved unnecessary API calls (matched the source's own 15-min cadence instead of hitting it every time).
- Flight durations are clearly labeled as *estimates* — the dataset doesn't actually link departures to arrivals, so we don't overclaim precision.
- Key lesson: verify data freshness and source limitations *before* optimizing anything downstream.

## Slide 7 — Evals (30s)
Anchor on the headline stat: **100% of answers pass an independent recount before the user ever sees them.** Explain the mechanism briefly — the validator recounts from the CSV with no shared state with the answer path, and any mismatch triggers an automatic retry. Mention it caught real issues during development (invalid dates, stale cached CSV) — proof the guardrail isn't theoretical.

## Slide 8 — Takeaways (30s + close)
Four lessons, quick hits:
1. Start simple and iterate — don't wait for a perfect first version.
2. Think in systems — design the full pipeline, not just one task.
3. Build for accuracy — validation and QA checks aren't optional extras.
4. Use specialized sub-agents — break the workflow into focused pieces that hand off to each other.

Close with "Thank you — questions welcome" and pause; don't rush past it.

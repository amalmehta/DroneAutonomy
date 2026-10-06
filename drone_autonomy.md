PROJECT NAME: drone_autonomy

META-INSTRUCTIONS:

<Read it all before acting. Ask about anything unclear, contradictory or
 underspecified — before starting and mid-build. Ask in the question widget
 (AskUserQuestion): related questions batched, concrete options, your
 recommendation first. Plain text only if the widget isn't available.>

<Don't expand scope. Anything not listed here is a proposal, including changes
 to this file — propose it, don't do it.>

<Prefer doing over describing: run the code, write the files, test it.>

<Always in scope, no proposal needed: when it goes on GitHub, a README that is
 easy to read at a glance — a line on what it is, then clear visuals
 (screenshots, a diagram or a chart), then links. Everything else goes in
 linked files: docs/INSTRUCTIONS.md (setup, run, use),
 docs/SYSTEM-DESIGN.md (see below) and docs/FILE-STRUCTURE.md (what's where). If what you're
 building is an application rather than a script, also a small unobtrusive feedback tab, and a settings
 button or tab (⌘, on the Mac) that gathers its preferences in one place.>

<If what you're building is an application, build it as a Mac app first; the
 website comes after, as its own step.>

<Name things the way a person would say them — "Goal Tracker", not
 goal_tracker — for the app, its windows, titles, files people open, repo
 descriptions and README headings. When you create the GitHub repo, name it
 with no "_" or "-": one word or joined words, e.g. GoalTracker.>

<Always in scope: a system design doc in the codebase, docs/SYSTEM-DESIGN.md,
 kept current as the build changes. Cover the architecture (with a Mermaid
 diagram), each component's job, the main flows, where data lives, the key
 design decisions and their trade-offs, how it's tested, and known limits.>

<Finish by listing every deliverable: path, what it is, how to check it works.>

<Git rules (no Claude attribution, never commit .claude/) are in
 ~/.claude/CLAUDE.md and apply on their own — nothing to repeat here.>

<Keep the changelog at the bottom current.>

CONTEXT:

create a complete drone autonomy using RL suite in simulation and figure out what drone to put the planning perception mapping stack on to test in in real world. create a paper and website

DELIVERABLES:

<What you want at the end: the app, files, links. One per line.>

(filled in by the agent)
- Python suite `drone_autonomy/` with CLI `drone-autonomy` (sim, stack, 7 meta-learning algorithms, baselines)
- Website with flight replay: website/ → https://amalmehta.github.io/DroneAutonomy/
- Drone recommendation and test plan: docs/DRONE-SELECTION.md
- Docs: README.md, docs/INSTRUCTIONS.md, docs/SYSTEM-DESIGN.md, docs/FILE-STRUCTURE.md
- IEEE-format paper (pending results)
- GitHub repo: https://github.com/amalmehta/DroneAutonomy

OPEN QUESTIONS / ASSUMPTIONS:

<Agent fills in: what it guessed, what it decided without asking.>

Asked and answered (2026-10-05):
- Python library + CLI with its own NumPy/Numba simulator, so no Mac app (and no app settings or feedback tab).
- Stack: depth camera → occupancy map → A* → RL local planner, with classical and end-to-end baselines.
- Real drone: indoor, about $1–3k → Holybro X500 V2 + Jetson Orin Nano Super + RealSense D435i (Starling 2 appears unavailable new).
- Paper in IEEE/ICRA format; public repo DroneAutonomy; website on GitHub Pages.
- Meta-learning (added by the user mid-build): MAML, FOMAML, Reptile, ANIL, Meta-SGD, PEARL, RL², in three combinations with classical methods (residual on the controller, meta-tuned gains, meta-RL local planner), adapting to dynamics and disturbances.

Decided without asking:
- Task ranges: payload ×0.85–1.3, one motor down to 75%, drag ×0.5–2, wind ≤ 2.5 m/s, gusts ≤ 0.8 m/s, latency 0–30 ms; OOD beyond each.
- Thrust-to-weight 2.1, motor lag 40 ms and drag 0.3 N·s/m are estimates.
- The local planner outputs velocities tracked by the classical controller, rather than raw thrust + body rates.
- The local planner is trained with a privileged planner (a Dijkstra field on the true map) and evaluated with online mapping.
- Hanging obstacles sit at 1.9 m or higher.
- ANIL is not applicable to gain tuning (no hidden layers). PEARL and RL² are not run on gain tuning.
- Compute: 2 seeds for the tracking problems because the machine is shared and heavily loaded.

CHANGELOG:

- 2026-10-05 — created
- 2026-10-06 — built the simulator, stack, learners, website demo; pushed to GitHub with Pages
- 2026-09-15 — added meta-instruction: built-out applications include a small feedback tab
- 2026-09-15 — added meta-instruction: no "Claude" attribution in commits, PRs, or branches
- 2026-09-16 — added meta-instruction: always include a README when adding to GitHub
- 2026-09-16 — changed meta-instruction: ask clarifying questions in the question widget
- 2026-09-17 — added meta-instructions: Claude never a contributor; never commit .claude/
- 2026-09-26 — compressed the meta-instructions and every field prompt; git rules moved to the global instruction file
- 2026-09-27 — added meta-instruction: applications are built as a Mac app first, then a website
- 2026-09-28 — folded inputs, instructions, constraints, deliverables and done criteria into one free-form CONTEXT
- 2026-09-28 — changed meta-instruction: a README on GitHub always includes a visual
- 2026-09-28 — added meta-instruction: name things like a person would, never snake_case
- 2026-09-28 — changed meta-instruction: README leads with visuals; instructions live in a linked guide
- 2026-09-28 — changed meta-instruction: README is visuals and links; details in docs/INSTRUCTIONS.md and docs/FILE-STRUCTURE.md
- 2026-09-29 — changed meta-instruction: GitHub repo names have no "_" or "-"
- 2026-10-02 — added a DELIVERABLES field after CONTEXT
- 2026-10-02 — added meta-instruction: every project has a system design doc at docs/SYSTEM-DESIGN.md
- 2026-10-05 — added meta-instruction: applications include a settings button or tab

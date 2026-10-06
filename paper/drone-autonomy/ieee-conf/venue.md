# Generic IEEE conference-format preprint

> **Cycle:** not tied to a conference cycle (researcher's choice, 2026-10-06) · **Last checked:** 2026-10-06
> **Sources:** [IEEEtran on CTAN](https://ctan.org/pkg/ieeetran) (the class IEEE's LaTeX template page points to) ·
> class file `IEEEtran.cls` V1.8b (2015/08/26), example `bare_conf.tex`

**Differences from a built-in profile:** none exists for this venue; built from the official class. There is no
call for papers, so page limit and statements are the researcher's choices, set to match common IEEE robotics
conferences (ICRA/IROS convention) so the draft can be retargeted with little change.

## Deadlines
None (preprint).

## Length and layout
| Field | Value | Source |
|---|---|---|
| Page limit | 8 pages including references (self-imposed; ICRA/IROS convention is 6 + 2 extra) | researcher choice |
| Columns | two | `\documentclass[conference]{IEEEtran}` |
| \textwidth, \columnwidth (measured) | 516.0 pt, 252.0 pt; \textheight 672.0 pt | probe on `bare_conf.tex` |
| Body font and size | Times 10 pt | IEEEtran conference default |
| Paper size | US Letter | IEEEtran default |

Tectonic/XeTeX note: `IEEEtran.cls` selects Times (`ptm`) for pdfLaTeX; `\usepackage[T1]{fontenc}` in `main.tex`
removes the body-text fallbacks (26 → 4 warnings; the remaining 4 fire while the class loads, before the
encoding switch, and don't affect typeset text).

## Template
| Field | Value |
|---|---|
| Download URL | https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip |
| Main style file | `IEEEtran.cls` (unmodified, in `template/`) |
| Bibliography style | `IEEEtran.bst`, numeric `\cite{}` |
| Caption placement | figure captions below, table captions above (IEEE convention) |

## Anonymity
Not anonymous: named author (Amal Mehta).

## Required and recommended sections
| Section | Required? | Where | Counts toward limit? |
|---|---|---|---|
| Limitations | recommended | before Conclusion | yes |
| Acknowledgment incl. AI-use disclosure | researcher requested full factual disclosure | after Conclusion | yes |
| Code/data availability | recommended | end of Introduction or Conclusion | yes |

## LLM / AI-use policy
No venue policy applies. IEEE's general author guidance asks that AI-generated content be disclosed in the
acknowledgments, with the AI system identified and the sections where it was used. The researcher chose a full
factual disclosure (see outline).

## Reviewer expectations (convention, robotics venues)
- **convention:** clear system description and figures of the pipeline; simulation results with stated seeds and
  confidence intervals; honest limitations about sim-to-real; comparisons to strong classical baselines.

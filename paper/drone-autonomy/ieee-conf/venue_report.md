# Venue report: generic IEEE conference preprint (IEEEtran)

## 1. Checks (`check_paper.py --page-limit 8 --verify-citations --regenerate`)
| ✅ PASS | LaTeX errors | none |
| ✅ PASS | undefined references/citations | none |
| ✅ PASS | missing files | none |
| ✅ PASS | fonts | no font substitutions |
| ✅ PASS | overfull lines > 5pt | none |
| ✅ PASS | page limit | main text ends on page 7 (limit 8) |
| ✅ PASS | numbers in prose are sourced | all listed in sources.md |
| ✅ PASS | value macros | 82 macros, all defined and listed |
| ✅ PASS | figures have scripts | all figures have a generating script |
| ✅ PASS | figures and values match the data | 9 generated files reproduce exactly from the data |
| ✅ PASS | citations verified | 36/36 verified |
| ⚠️ WARN | open TODOs | main.tex: affiliation |

Compiled PDF: 8 pages with references (last page balanced). Citations: 36/36 verified against
arXiv/Crossref (`citations_verification.md`). One entry (Lee et al. 2010) first pointed at the wrong arXiv
record and was switched to the CDC DOI, then verified.

## 2. Rule changes found at P2
No call for papers applies (generic preprint, the researcher's choice). Built from the official IEEEtran
class (CTAN, V1.8b). The only template-related change is `\RequirePackage[T1]{fontenc}` before the class in
`main.tex` (style file untouched), so XeTeX uses Times shapes instead of falling back.

## 3. Open TODOs and facts still needed
- `\TODO{affiliation}` in `main.tex`.

## 4. Statements
- **Acknowledgment / AI-use disclosure** (in `sections/conclusion.tex`): states that the simulator,
  algorithms, experiments, benchmark, figure/table scripts and text were produced with Claude Code
  (Anthropic) under the author's direction, that citations were checked by script, and that the author
  reviewed the results. Please read and edit it; if you submit to a venue, the submission form's disclosure
  must match.
- **Code availability**: end of the Introduction (GitHub URL).

## 5. Only a human can judge
- Whether the framing ("where does meta-learning help") and the title fit how you want to present the work.
- Claim strength: C3 and C5 are now stated firmly (5 gain seeds with a paired test; 96 unseen-room full-stack flights). C6 was restated after the step-size sweep, the RL² claim dropped, and C7 revised.
- Fig. 1 is a hand-drawn TikZ diagram, a draft to polish; Fig. 3 shows one recorded classical flight.
- Fig. 2 is plotted against adaptation stage with the end-to-end planners moved to Table IV; still dense (11 methods).
- Whether to retarget to a specific venue (IROS 2027, ICRA 2028): page limit and statements would change.

# Pre-Submission Thesis Review Checklist

This checklist is intended for finalizing the thesis draft before sending it to the committee.

---

## 1. Inconsistency
- [ ] Standardize terminology for processes (e.g., "map point culling", "point removal", "MPR") across all chapters.
- [ ] Use a single name for each variable or symbol throughout the document.
- [ ] Ensure that earlier chapters (Background, Related Work) use the same names and notation as the Implementation chapter.

## 2. Changes in Scope
- [ ] Remove all references to multiple observability models.
- [ ] Replace plural phrasing ("models", "approaches") with singular where appropriate.
- [ ] Keep only the KNN observability model description, and remove any unused model sections or references.
- [ ] Verify that contributions, objectives, and research questions align with the reduced scope.

## 3. Mathematical Correctness
- [ ] Verify all variable definitions are consistent and unambiguous.
- [ ] Check each equation for mathematical correctness.
- [ ] Ensure all symbols follow standard usage (no conflicts with well-known symbols from probability/statistics unless explicitly redefined).
- [ ] Confirm units, domains, and ranges are properly stated for all variables.

## 4. Completeness of Results and Analysis
- [ ] Remove placeholder text in Sections 5.1–5.5.
- [ ] If results are incomplete, include preliminary results with notes or a clearly stated analysis plan.
- [ ] Make sure each research question and objective has corresponding results or discussion.

## 5. Consistency of Terminology for Scope and Contributions
- [ ] Avoid phrasing that implies general dynamic object detection or semantic segmentation.
- [ ] Emphasize that the method is for **post-run map pruning across episodes**.
- [ ] Ensure the Contributions section matches the actual delivered work.

## 6. Figure and Algorithm Referencing
- [ ] Reference every figure, table, and algorithm in the text before it appears.
- [ ] Ensure captions explain both what is shown and why it matters to the research.
- [ ] Verify numbering is consistent and sequential.

## 7. Citation Completeness
- [ ] Replace placeholder citations (e.g., `[7] PLACEHOLDER`) with proper references.
- [ ] Add missing references for claims in Sections 3.3 and 3.4.
- [ ] Check citation formatting for consistency.

## 8. Dataset Description Rigor
- [ ] Strengthen the connection between dataset design and evaluation objectives.
- [ ] Explicitly state why each dataset is suitable for testing the hypotheses.
- [ ] Include relevant details (sensor specs, calibration process, ground truth acquisition).

## 9. Uniform Notation for Observations and Variables Across Chapters
- [ ] Use a single notation for probabilities (e.g., `P(S, v)` vs `P(S_v)`) across the thesis.
- [ ] Ensure probability terms have the same conditioning and variable names in all sections.
- [ ] Update Background examples to match Implementation notation.

## 10. Clear End-to-End Experiment Flow
- [ ] Present Experimental Setup as an academic procedure, not as personal implementation notes.
- [ ] Clearly show **input → process → output** for each experiment.
- [ ] Cross-reference Experimental Setup with Results so the reader can follow the progression.

---
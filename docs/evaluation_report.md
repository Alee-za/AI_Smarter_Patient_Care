# Evaluation Report

## Status

The repository includes an executable evaluation on a small **synthetic** sample so that the project can be tested without patient-level data.

**This is not hackathon performance evidence.** Run the same protocol on the organizer-supplied MIMIC-IV Clinical Database Demo v2.2 copy before submission.

## Evaluation question

Can CareLens AI retrieve the correct structured evidence row for a research query while preserving complete source provenance and abstaining when the record does not support the query?

## Synthetic test protocol

Five manually specified queries are matched to expected source IDs. Each query is scoped to a subject. Top-1 retrieval accuracy and provenance completeness are reported.

Run:

```bash
python scripts/evaluate.py
```

## Required final evaluation on organizer data

Report:

| Measure | Result |
|---|---|
| Number of subjects | TO FILL |
| Number of events | TO FILL |
| Source tables | TO FILL |
| Missing event times | TO FILL |
| Duplicate source keys | TO FILL |
| Top-1 structured-fact accuracy | TO FILL |
| Temporal-order accuracy | TO FILL |
| Provenance coverage | TO FILL |
| Unsupported-query abstention accuracy | TO FILL |
| Median retrieval latency | TO FILL |

## Baseline

Compare against the simple keyword-overlap baseline in `ClinicalDataEngine.keyword_search`.

## Leakage

Track 1 is a retrieval task rather than a predictive model. No future event is synthesized into a past event. If a future-event question is introduced later, enforce an explicit index time and filter all evidence after it.

## Error analysis

At least:
- 3 successful retrievals
- 3 incorrect/ambiguous retrievals
- 3 unsupported questions that trigger abstention

For every error, record:
- query
- expected evidence
- retrieved evidence
- why the mismatch happened
- whether the UI clearly exposed the limitation

## Uncertainty

Because the demo has only 100 patients, numerical results should be treated as illustrative. Avoid claims that small differences establish superiority or clinical utility.

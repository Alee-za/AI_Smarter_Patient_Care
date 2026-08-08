# Safety & Data Statement

## Intended use

CareLens AI is a research and education prototype for exploring structured, deidentified hospital data.

## Prohibited use

It must not be used for:
- diagnosis
- treatment selection
- triage
- emergency decisions
- patient-specific medical advice
- clinical workflow automation

## Human-review boundary

A researcher must review the underlying source rows before interpreting any retrieved evidence.

## Provenance

Every patient-level evidence item exposes:
- source table
- source field
- source identifier
- subject identifier
- admission identifier when available
- timestamp

## Data handling

Patient-level data should remain local. The application has no external AI/API call. The sample data are synthetic.

## Failure modes

The system can:
- retrieve semantically weak matches
- miss synonyms
- return ambiguous structured labels
- abstain even when a human would find a relevant row
- inherit source-data quality problems

The product displays these limitations rather than silently correcting the record.

## Responsible AI

AI-generated retrieval scores are visually distinct from source data. The system never presents generated prose as a clinician-authored note.

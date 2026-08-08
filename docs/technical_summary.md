# Technical Summary

## Problem

Hospital data are distributed across relational tables. Researchers can lose temporal context, source provenance, or confidence when manually reconstructing an encounter.

## Target user

Clinical-data researchers, educators, and healthcare data teams. The system is not intended for clinicians making patient-care decisions.

## Primary track

Track 1 — Structured Patient Timeline & Evidence Retrieval.

## Architecture

```text
MIMIC-IV CSVs
     |
     v
Provenance-preserving event adapter
     |
     +--> Timeline view
     |
     +--> Data-quality checks
     |
     v
Local TF-IDF index
     |
     v
Query similarity + threshold
     |
     +--> Evidence cards with provenance
     |
     +--> Abstain when unsupported
```

## Source tables

The adapter supports:
- admissions
- transfers
- diagnoses_icd
- procedures_icd
- labevents
- prescriptions
- icustays
- chartevents

## AI component

TF-IDF + cosine similarity is used for local evidence retrieval. It is deliberately simple, reproducible, and auditable. It does not generate free-text clinical notes.

## Design choices

- Preserve original source files.
- Normalize only into an additional event view.
- Never overwrite source rows.
- Keep subject-level records together during evaluation.
- Show source table, source field, source ID, timestamp, subject ID, and admission ID.
- Use abstention rather than hallucination.

## Limitations

- Small demo dataset.
- Structured labels are not clinician-authored notes.
- Retrieval quality depends on the structured representation.
- TF-IDF does not understand clinical semantics as deeply as specialized language models.
- No clinical effectiveness or safety claim is possible.

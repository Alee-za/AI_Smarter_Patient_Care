# CareLens AI — AI for Smarter Patient Care

**Hackathon track:** Track 1 — Structured Patient Timeline & Evidence Retrieval

CareLens AI is a transparent research prototype for reconstructing a structured hospital/ICU timeline and retrieving source-linked evidence from relational clinical data.

## What makes the prototype submission-ready

- End-to-end Streamlit interface
- Structured event timeline
- Source provenance on every retrieved event
- Local AI retrieval using TF-IDF + cosine similarity
- Explicit abstention for unsupported questions
- Data-quality explorer
- MIMIC-IV Demo v2.2 CSV adapter for common tables
- Reproducible evaluation script
- Unit tests
- Safety, limitations, and data-lineage documentation
- No patient-level data is sent to an external AI service

## Important dataset note

The folder `data/sample/events.csv` is **synthetic** and is included only so the application works immediately after installation. It must **not** be used to claim performance on MIMIC-IV.

For the actual hackathon submission, download/use the organizer-supplied frozen **MIMIC-IV Clinical Database Demo v2.2** copy and place it at:

```text
data/mimic-iv-demo/
├── hosp/
└── icu/
```

The adapter reads common files such as `admissions.csv.gz`, `transfers.csv.gz`, `diagnoses_icd.csv.gz`, `procedures_icd.csv.gz`, `labevents.csv.gz`, `prescriptions.csv.gz`, `icustays.csv.gz`, and `chartevents.csv.gz`.

## Run

### Windows

Double-click `run_app.bat`, or:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app\streamlit_app.py
```

### macOS/Linux

```bash
./run_app.sh
```

Then open the Streamlit URL shown in the terminal.

## Test

```bash
pytest -q
python scripts/evaluate.py
```

## AI method

The system converts structured rows into a provenance-preserving event view. Each event receives a compact textual representation containing only structured fields. A local TF-IDF vectorizer creates sparse representations; cosine similarity ranks evidence for a research question.

A fixed confidence threshold triggers **abstention** when the top match is too weak. This is deliberate: the system is designed to prefer "not supported by this record" over an unsupported generated statement.

### Baseline

The evaluation script also includes a simple keyword-overlap baseline implementation in `src/engine.py`. For the final report, compare the AI retrieval method against that baseline on the organizer data.

## Safety

**Research and educational prototype only. Not for clinical use. Do not use for diagnosis, treatment, triage, or emergency decisions.**

The product:
- does not recommend treatments
- does not rank clinicians or therapies
- does not make causal claims
- does not issue emergency guidance
- keeps AI output visually distinct from source records
- shows table/field/id/time provenance
- never silently modifies source rows
- abstains when evidence is insufficient

## Final submission checklist

Before submitting:
1. Replace the included synthetic sample with the organizer-supplied MIMIC-IV Demo v2.2 data for evaluation.
2. Run `pytest -q`.
3. Run `python scripts/evaluate.py` and record results on the actual frozen dataset.
4. Report patient-grouped evaluation; never split rows from the same subject across train/test.
5. Document exclusions, missingness, latency, retrieval errors, and abstention behavior.
6. Include one honest failure case in the demo.
7. Cite MIMIC-IV Clinical Database Demo v2.2 and comply with its license/attribution terms.
8. Do not upload patient-level rows to an external LLM/API.

## Suggested 3-minute demo

1. Open **Overview** and explain the problem.
2. Select a patient in **Patient Timeline** and show source-linked events.
3. Ask "What laboratory results are available?" in **Evidence Q&A**.
4. Point out that every result has source table, field, ID, subject, encounter, and time.
5. Ask an unsupported question and show **ABSTAINED**.
6. Open **Data Quality** and show missingness/duplicate checks.
7. End with the safety boundary and one limitation: 100-patient demo data cannot establish clinical effectiveness or generalizability.

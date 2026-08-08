# 🩺 CareLens AI

### AI for Smarter Patient Care

> **A transparent AI-powered platform for reconstructing structured patient timelines and retrieving source-verifiable clinical evidence.**

CareLens AI is a research-focused healthcare AI prototype designed to make complex hospital data easier to explore, understand, and verify.

Healthcare records are often distributed across multiple structured tables such as admissions, laboratory results, medications, procedures, ICU observations, diagnoses, and transfers. CareLens AI brings these fragmented records together into a chronological patient timeline while preserving the original source information behind every event.

Instead of generating unsupported medical conclusions, CareLens AI focuses on **evidence retrieval, transparency, provenance, and safe abstention**.

---

## Project Overview

### The Problem

Modern healthcare datasets contain large amounts of information spread across many interconnected tables. Researchers and healthcare data teams may need to manually reconstruct:

* What happened to a patient?
* When did each event occur?
* Which admission did the event belong to?
* Which laboratory results were recorded?
* Which medications or procedures were documented?
* Where did a particular piece of information originate?

This fragmentation makes exploration time-consuming and increases the risk of losing temporal context or source provenance.

### Our Solution

**CareLens AI** converts structured hospital records into a unified, chronological event view and provides AI-assisted evidence retrieval.

The system:

1. Ingests structured clinical data.
2. Preserves source-table and source-field information.
3. Reconstructs patient timelines.
4. Retrieves relevant evidence using local AI-based similarity search.
5. Displays the original source information alongside each result.
6. Abstains when the available evidence is insufficient.
7. Provides data-quality and reproducibility tools.

> **Core principle:** AI should help researchers find evidence — not invent evidence.

---

## Key Features

| Feature                      | Description                                                                |
| ---------------------------- | -------------------------------------------------------------------------- |
|  **Patient Timeline**      | Reconstructs chronological patient and encounter events                    |
|  **AI Evidence Retrieval** | Finds relevant structured evidence using local semantic similarity         |
|  **Source Provenance**     | Every result exposes its originating table, field, ID, and timestamp       |
|  **AI Abstention**         | Refuses unsupported queries instead of producing fabricated answers        |
|  **Data Quality Explorer** | Identifies missing timestamps, missing IDs, duplicates, and table coverage |
|  **Evaluation Framework**  | Includes reproducible retrieval and provenance evaluation                  |
|  **Local Processing**      | Patient-level records are not sent to an external AI API                   |
|  **MIMIC-IV Support**      | Includes an adapter for common MIMIC-IV Demo v2.2 CSV tables               |
|  **Automated Tests**       | Includes unit tests for timeline, retrieval, provenance, and abstention    |

---

## AI Methodology

CareLens AI uses a lightweight, transparent retrieval architecture rather than an opaque generative system.

### Retrieval Pipeline

```text
Clinical CSV Tables
        │
        ▼
┌──────────────────────┐
│ Data Ingestion       │
│ & Normalization      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Event Representation │
│ + Provenance          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ TF-IDF Vectorization │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Cosine Similarity    │
│ Evidence Ranking     │
└──────────┬───────────┘
           │
      ┌────┴─────┐
      ▼          ▼
 Evidence     Abstain
 Retrieved    if weak
```

### Why TF-IDF?

The project intentionally uses a transparent and reproducible retrieval method.

TF-IDF provides:

* Local processing
* No external API dependency
* Fast retrieval
* Reproducible results
* Easy auditing
* Clear similarity scores

This makes it appropriate for a hackathon prototype where **explainability and reproducibility** are important.

### Safe Abstention

A major design principle of CareLens AI is:

> **When the available evidence is not strong enough, the system does not pretend to know the answer.**

A configurable similarity threshold is used to determine whether a query has sufficient supporting evidence.

For example:

```text
User Query
    │
    ▼
Retrieve Evidence
    │
    ▼
Similarity ≥ Threshold?
   /             \
 YES              NO
  │                │
  ▼                ▼
Show Evidence    ABSTAIN
with Sources     "Evidence
                 insufficient"
```

---

## Evidence Provenance

CareLens AI does not simply display an AI-generated answer.

Each retrieved event includes its underlying source information:

```text
Source Table
Source Field
Source ID
Subject ID
Admission ID
Event Timestamp
Event Type
Original Structured Value
```

Example:

```text
2026-01-05 12:00
Laboratory

source_table = labevents
source_field = charttime
source_id    = L1001
subject_id   = 1001
hadm_id      = 20001
```

This allows researchers to trace a result back to the original structured record.

---

## Supported Clinical Data

The MIMIC-IV adapter supports common tables including:

* `admissions`
* `transfers`
* `diagnoses_icd`
* `procedures_icd`
* `labevents`
* `prescriptions`
* `icustays`
* `chartevents`

The system creates an additional normalized event representation while leaving the original source records untouched.

---

## System Architecture

```text
                  ┌──────────────────────┐
                  │     MIMIC-IV Data    │
                  │      CSV Tables      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Data Adapter      │
                  │  & Event Normalizer  │
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       Patient Timeline  Data Quality   Event Index
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │ Local AI Retrieval │
                                  │ TF-IDF + Cosine    │
                                  │ Similarity         │
                                  └─────────┬──────────┘
                                            │
                               ┌────────────┴────────────┐
                               ▼                         ▼
                       Evidence Results              Abstention
                               │
                               ▼
                    Source-Linked UI Results
```

---

## Application Modules

### 1. Overview

Provides:

* Project explanation
* Dataset statistics
* Number of patients
* Number of structured events
* Source-table coverage
* AI methodology
* Data-flow explanation

### 2. Patient Timeline

Users can select a deidentified patient and encounter to view:

* Admission events
* Transfers
* Diagnoses
* Procedures
* Laboratory events
* Medications
* ICU observations

Events are displayed chronologically.

### 3. Evidence Q&A

Researchers can enter questions such as:

```text
What laboratory results are available?
```

or:

```text
Which medications were recorded?
```

The system retrieves relevant structured evidence and displays the corresponding provenance.

### 4. Data Quality Explorer

Provides visibility into:

* Missing event timestamps
* Missing subject IDs
* Duplicate source keys
* Source-table coverage
* Overall dataset statistics

### 5. Evaluation

Provides an executable evaluation framework for:

* Retrieval accuracy
* Provenance completeness
* Abstention behavior
* Baseline comparison

---

## Technology Stack

### Frontend / Interface

* **Streamlit**

### Programming Language

* **Python**

### Data Processing

* **Pandas**
* **NumPy**

### AI / Machine Learning

* **Scikit-learn**
* TF-IDF Vectorization
* Cosine Similarity

### Testing

* **Pytest**

### Dataset

* **MIMIC-IV Clinical Database Demo v2.2**

---

## Project Structure

```text
CareLens_AI/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── __init__.py
│   ├── engine.py
│   └── data_loader.py
│
├── data/
│   └── sample/
│       └── events.csv
│
├── scripts/
│   └── evaluate.py
│
├── tests/
│   └── test_engine.py
│
├── docs/
│   ├── technical_summary.md
│   ├── evaluation_report.md
│   ├── safety_and_data_statement.md
│   ├── demo_script.md
│   ├── submission_checklist.md
│   └── citation.txt
│
├── requirements.txt
├── .gitignore
├── run_app.bat
├── run_app.sh
└── README.md
```

---

## Getting Started

### Prerequisites

Make sure you have:

* Python 3.10+
* Git
* Internet connection for installing dependencies

Check Python:

```bash
python --version
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/carelens-ai-smarter-patient-care.git
```

```bash
cd carelens-ai-smarter-patient-care
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Run:

```bash
streamlit run app/streamlit_app.py
```

The terminal will provide a local URL, typically:

```text
http://localhost:8501
```

Open that address in your browser.

### Windows Shortcut

You can also use:

```text
run_app.bat
```

---

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

The tests cover:

* Patient timeline generation
* Evidence retrieval
* Source provenance
* Abstention behavior
* Data-quality reporting

---

## Running the Evaluation

Run:

```bash
python scripts/evaluate.py
```

The evaluation reports:

* Top-1 retrieval accuracy
* Provenance completeness
* Retrieved evidence IDs
* Abstention behavior

### Important

The repository contains a small **synthetic dataset** so that the application can run immediately after cloning.

The synthetic dataset is **not clinical data** and must not be used to claim clinical performance.

For the actual hackathon evaluation, use the required MIMIC-IV Clinical Database Demo v2.2 dataset.

---

## MIMIC-IV Dataset Setup

Place the permitted MIMIC-IV Demo data in:

```text
data/
└── mimic-iv-demo/
    ├── hosp/
    │   ├── admissions.csv.gz
    │   ├── transfers.csv.gz
    │   ├── diagnoses_icd.csv.gz
    │   ├── procedures_icd.csv.gz
    │   ├── labevents.csv.gz
    │   └── prescriptions.csv.gz
    │
    └── icu/
        ├── icustays.csv.gz
        └── chartevents.csv.gz
```

The dataset itself is intentionally excluded from Git using `.gitignore`.

**Never commit patient-level data to this repository.**

---

## Evaluation Philosophy

CareLens AI is designed around reproducibility rather than inflated performance claims.

Evaluation should consider:

| Metric                   | Purpose                                                       |
| ------------------------ | ------------------------------------------------------------- |
| Top-1 Retrieval Accuracy | Measures whether the correct evidence is ranked first         |
| Provenance Completeness  | Checks whether retrieved evidence can be traced to its source |
| Abstention Accuracy      | Measures whether unsupported queries are correctly rejected   |
| Retrieval Latency        | Measures responsiveness                                       |
| Data Quality             | Measures missingness and duplicate source records             |
| Baseline Comparison      | Compares AI retrieval against simple keyword matching         |

### Avoiding Data Leakage

When evaluating patient-level data:

> **All records belonging to the same patient should remain within the same evaluation partition.**

Rows from the same patient must not be randomly distributed between training and testing when a predictive model is introduced.

---

## Limitations

CareLens AI is a hackathon research prototype.

It has important limitations:

* The current AI retrieval method is lightweight rather than clinically specialized.
* Structured codes may not contain the full clinical context available in narrative notes.
* Similarity scores do not represent clinical certainty.
* Retrieval errors can occur.
* Synonyms and clinical terminology may not always match.
* The MIMIC-IV Demo dataset contains only a small number of patients.
* Results from the demo dataset cannot establish clinical effectiveness.
* The system has not undergone clinical validation.
* The system is not intended for real-world patient-care decisions.

---

## Safety & Responsible AI

### Intended Use

CareLens AI is intended for:

* Healthcare AI research
* Clinical-data education
* Structured data exploration
* Dataset analysis
* Evidence retrieval research
* Hackathon demonstration

### Not Intended For

CareLens AI must **not** be used for:

* Diagnosis
* Treatment decisions
* Medication recommendations
* Patient triage
* Emergency medical decisions
* Patient-specific medical advice
* Automated clinical decision-making

### Privacy

The application is designed so that patient-level records remain local.

There is:

* No external LLM API
* No cloud AI inference
* No automatic patient-data upload
* No patient-data collection
* No modification of original clinical records

---

## Why CareLens AI?

Traditional clinical-data exploration often requires researchers to manually join multiple tables and reconstruct the patient journey.

CareLens AI changes this workflow:

```text
Traditional Workflow

Multiple Tables
      ↓
Manual Joins
      ↓
Manual Timeline Reconstruction
      ↓
Search Through Records
      ↓
Find Source
      ↓
Interpret Data


CareLens AI

Multiple Tables
      ↓
Automated Event Representation
      ↓
Patient Timeline
      ↓
AI Evidence Retrieval
      ↓
Source Provenance
      ↓
Human Verification
```

The goal is not to replace healthcare professionals.

The goal is to make **structured healthcare data easier to explore, trace, and understand.**

---

## Future Roadmap

### Phase 1 — Current Prototype

* [x] Structured event representation
* [x] Patient timeline
* [x] AI evidence retrieval
* [x] Source provenance
* [x] Abstention
* [x] Data-quality explorer
* [x] Evaluation framework
* [x] MIMIC-IV adapter

### Phase 2 — Advanced Retrieval

* [ ] Clinical terminology normalization
* [ ] Hybrid keyword + semantic retrieval
* [ ] Better temporal reasoning
* [ ] Cross-table relationship visualization
* [ ] Advanced retrieval benchmarking

### Phase 3 — Research Extensions

* [ ] Clinically validated retrieval benchmarks
* [ ] Larger approved datasets
* [ ] Human evaluation with clinical-data researchers
* [ ] More robust uncertainty estimation
* [ ] Advanced cohort exploration

> Future extensions would require appropriate ethics, privacy, security, and clinical validation processes.

---

## Dataset & Citation

This project is designed to work with the **MIMIC-IV Clinical Database Demo v2.2**.

The dataset should be obtained through the appropriate PhysioNet access and licensing process.

### Citation

Johnson, A. E. W., Bulgarelli, L., Shen, L., et al.
**MIMIC-IV, a freely accessible electronic health record dataset.**
Scientific Data, 2023.

For the demonstration subset:

Johnson, A. E. W., Bulgarelli, L., Pollard, T., et al.
**MIMIC-IV Clinical Database Demo (version 2.2).**
PhysioNet, 2023.

DOI:

```text
10.13026/dp1f-ex47
```

Please follow the dataset's applicable license, access, and attribution requirements.

---

## Responsible Development

This project was developed as a healthcare AI research prototype with an emphasis on:

* Transparency
* Explainability
* Data provenance
* Human oversight
* Privacy
* Reproducibility
* Safe failure behavior

---

## License

The source code for this hackathon prototype may be distributed under the license selected by the project authors.

**Important:** The MIMIC-IV dataset is separately governed by its own terms and must not be treated as being covered by this repository's software license.

---

## Project

### CareLens AI

**Theme:** AI for Smarter Patient Care
**Track:** Structured Patient Timeline & Evidence Retrieval

> **Find the evidence. Trace the source. Know when to abstain.**

---

<p align="center">

---
### ScreenShots
        
<img width="1600" height="950" alt="01_overview" src="https://github.com/user-attachments/assets/c337a077-b4f7-4f28-a799-0082db0913ad" />

<img width="1600" height="950" alt="02_patient_timeline" src="https://github.com/user-attachments/assets/244aa88a-3613-4c33-b6e7-2168cad68963" />

<img width="1600" height="950" alt="05_evaluation" src="https://github.com/user-attachments/assets/afcd84e3-51c3-4f64-a71b-fbb848315de4" />

<img width="1600" height="950" alt="04_data_quality" src="https://github.com/user-attachments/assets/db122186-1d10-48a1-8d83-461adde588e4" />

<img width="1600" height="950" alt="03_evidence_qa" src="https://github.com/user-attachments/assets/5f8f5b7a-6d8c-47a0-8831-ba8265d7ef3d" />

---

<p align="center">
### 🩺 CareLens AI

**Transparent AI for smarter healthcare data exploration.**

</p>

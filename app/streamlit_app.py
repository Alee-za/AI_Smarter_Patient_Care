
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data_loader import load_sample, load_data
from src.engine import ClinicalDataEngine, quality_report

st.set_page_config(
    page_title="CareLens AI | Smarter Patient Care",
    page_icon="🩺",
    layout="wide",
)

st.markdown("""
<style>
.main .block-container {padding-top: 1.2rem; max-width: 1450px;}
.hero {padding: 1.2rem 1.4rem; border-radius: 18px; border: 1px solid #dbe4f0; background: linear-gradient(135deg,#f7fbff,#eef6ff);}
.badge {display:inline-block; padding:.25rem .65rem; border-radius:999px; background:#e8f1ff; color:#1558a6; font-size:.78rem; font-weight:700;}
.source {font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.82rem;}
.warning {padding:.85rem 1rem; border-radius:12px; background:#fff7e6; border:1px solid #ffd591;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<span class="badge">HACKATHON • TRACK 1</span>
<h1 style="margin:.45rem 0 .2rem 0;">CareLens AI</h1>
<p style="font-size:1.08rem;margin:0;">Transparent structured patient timelines & evidence retrieval.</p>
<p style="margin:.55rem 0 0 0;color:#52616f;">
A research prototype that reconstructs hospital/ICU events, retrieves verifiable structured evidence,
and abstains when the record does not support a query.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning">
<b>Research and educational prototype only.</b> Not for clinical use. Do not use for diagnosis,
treatment, triage, or emergency decisions. AI-generated retrieval is not clinician-authored documentation.
</div>
""", unsafe_allow_html=True)

@st.cache_data
def get_events(mode):
    if mode == "Included sample":
        return load_sample()
    return load_data(mode)

with st.sidebar:
    st.header("Data")
    mode = st.radio("Dataset mode", ["Included sample", "MIMIC-IV folder"])
    if mode == "MIMIC-IV folder":
        data_root = st.text_input("MIMIC-IV Demo root", "data/mimic-iv-demo")
        events = get_events(data_root)
    else:
        events = get_events("Included sample")
    st.caption("The included sample is synthetic and is never used as evidence of clinical performance.")
    st.divider()
    st.header("Navigation")
    page = st.radio("Open", ["Overview", "Patient Timeline", "Evidence Q&A", "Data Quality", "Evaluation"])

engine = ClinicalDataEngine(events)

if page == "Overview":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Patients", events["subject_id"].nunique())
    c2.metric("Structured events", len(events))
    c3.metric("Source tables", events["source_table"].nunique())
    c4.metric("Event types", events["event_type"].nunique())
    st.subheader("How it works")
    st.markdown("""
    1. **Ingest** structured CSV tables without rewriting source rows.
    2. **Normalize into an event view** while retaining table, field, identifier, and timestamp provenance.
    3. **Retrieve evidence locally** using TF-IDF similarity over structured event descriptions.
    4. **Abstain** when evidence similarity is below a declared threshold.
    5. **Expose the original evidence row** next to every retrieved result.
    """)
    st.subheader("Data flow")
    st.code("MIMIC CSV tables → provenance-preserving event view → local TF-IDF retrieval → evidence cards → researcher review")
    st.subheader("Supported MIMIC-IV tables")
    st.write(", ".join(sorted(events["source_table"].unique())))

elif page == "Patient Timeline":
    st.header("Structured Patient Timeline")
    subjects = engine.subjects()
    subject = st.selectbox("Patient (deidentified subject_id)", subjects)
    stays = engine.timeline(subject)["hadm_id"].replace("", "No admission ID").unique().tolist()
    hadm = st.selectbox("Encounter / admission", ["All"] + list(stays))
    timeline = engine.timeline(subject, None if hadm == "All" else hadm)
    st.caption(f"{len(timeline)} source-linked events")
    for _, r in timeline.iterrows():
        with st.container(border=True):
            a,b,c = st.columns([1.1,1.6,4])
            a.markdown(f"**{r['event_time']}**")
            b.markdown(f"**{str(r['event_type']).replace('_',' ').title()}**")
            c.markdown(str(r["text"]))
            st.markdown(
                f"<span class='source'>source_table={r['source_table']} • "
                f"source_field={r['source_field']} • source_id={r['source_id']} • "
                f"subject_id={r['subject_id']} • hadm_id={r['hadm_id']}</span>",
                unsafe_allow_html=True
            )

elif page == "Evidence Q&A":
    st.header("Evidence Retrieval")
    st.write("Ask a research question about the structured record. The system returns source-linked evidence, not clinical advice.")
    subject = st.selectbox("Patient scope", ["All"] + engine.subjects())
    hadms = ["All"]
    if subject != "All":
        hadms += sorted(engine.timeline(subject)["hadm_id"].replace("", "No admission ID").unique().tolist())
    hadm = st.selectbox("Encounter scope", hadms)
    q = st.text_input("Research question", placeholder="e.g., What laboratory results are available?")
    if q:
        results, abstain = engine.search(
            q,
            None if subject == "All" else subject,
            None if hadm == "All" else hadm,
        )
        if abstain:
            st.warning("ABSTAINED: the structured record does not provide sufficiently strong evidence for this query.")
        elif results:
            st.success(f"Retrieved {len(results)} source-linked evidence rows. Review the original fields before drawing conclusions.")
            for i,e in enumerate(results,1):
                with st.container(border=True):
                    st.markdown(f"**Evidence {i} — retrieval score {e.score:.3f}**")
                    st.write(e.text)
                    st.markdown(
                        f"<span class='source'>"
                        f"{e.event_time} | {e.event_type} | "
                        f"{e.source_table}.{e.source_field} | id={e.source_id} | "
                        f"subject_id={e.subject_id} | hadm_id={e.hadm_id}"
                        f"</span>",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No matching structured evidence was found.")

    st.subheader("AI transparency")
    st.write("Method: local TF-IDF retrieval with a fixed abstention threshold (0.13). No patient-level rows are transmitted to an external AI service.")

elif page == "Data Quality":
    st.header("Data Quality Explorer")
    report = quality_report(events)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rows", report["rows"])
    c2.metric("Missing event time", report["missing_event_time"])
    c3.metric("Missing subject ID", report["missing_subject_id"])
    c4.metric("Duplicate source keys", report["duplicate_source_keys"])

    st.subheader("Missingness by field")
    st.dataframe(report["missingness"], use_container_width=True, hide_index=True)
    st.subheader("Source table coverage")
    coverage = events.groupby("source_table").size().reset_index(name="rows").sort_values("rows", ascending=False)
    st.bar_chart(coverage.set_index("source_table"))
    st.subheader("Important boundary")
    st.info("Quality flags are data-quality observations, not clinical findings. The app never silently edits or deletes source records.")

elif page == "Evaluation":
    st.header("Evaluation & Reproducibility")
    st.write("The included test suite evaluates the retrieval engine on the included synthetic sample only. Replace it with the organizer-supplied MIMIC-IV Demo v2.2 data before submitting performance claims.")
    st.code("python scripts/evaluate.py")
    eval_path = Path(__file__).resolve().parents[1] / "docs" / "evaluation_report.md"
    st.markdown(eval_path.read_text(encoding="utf-8"))

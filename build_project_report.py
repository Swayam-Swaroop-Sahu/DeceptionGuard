"""Comprehensive builder for DeceptionGuard Project Report.

Generates both:
1. 'Project Report.pdf' via ReportLab (two-pass academic layout, running headers, roman preliminary pages)
2. 'Project Report.docx' via python-docx (executive Word layout, styled tables, embedded figures, Appendix)
"""

from __future__ import annotations

import os
from pathlib import Path

# ==========================================
# PART 1: REPORTLAB PDF GENERATOR
# ==========================================
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PDF_PATH = "Project Report.pdf"
DOCX_PATH = "Project Report.docx"

class AcademicNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        body_pages = max(1, num_pages - 3)

        for idx, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            pno = idx + 1
            if pno > 1:
                self.saveState()
                self.setFont("Helvetica-Bold", 7.5)
                self.setFillColor(colors.black)
                self.drawString(54, 750, "BCSE410L – CYBER SECURITY PROJECT  |  DECEPTIONGUARD TECHNICAL REPORT")
                self.setStrokeColor(colors.black)
                self.setLineWidth(0.5)
                self.line(54, 744, 558, 744)

                self.line(54, 46, 558, 46)
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.black)
                self.drawString(54, 34, "School of Computer Science and Engineering (SCOPE)")

                if pno == 2:
                    page_str = "Page i"
                elif pno == 3:
                    page_str = "Page ii"
                else:
                    body_pno = pno - 3
                    page_str = f"Page {body_pno} of {body_pages}"

                self.drawRightString(558, 34, page_str)
                self.restoreState()
            super().showPage()
        super().save()


def generate_pdf(toc_page_map=None):
    if toc_page_map is None:
        toc_page_map = {
            "ch1": "1",
            "ch2": "2",
            "ch3": "4",
            "ch4": "5",
            "ch5": "7",
            "ch6": "9",
            "ch7": "11",
            "ch8": "11",
            "app": "12"
        }

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    c_primary = colors.black
    c_accent = colors.black
    c_dark = colors.black
    c_light_bg = colors.white
    c_callout_bg = colors.white

    styles.add(ParagraphStyle(
        name="TitleCourse",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=c_accent,
        alignment=1,
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name="MainTitle",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=22,
        textColor=c_primary,
        alignment=1,
        spaceAfter=25
    ))
    styles.add(ParagraphStyle(
        name="AuthorBlock",
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=c_dark,
        alignment=1,
        spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="SupervisionBlock",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        textColor=c_primary,
        alignment=1,
        spaceAfter=22
    ))
    styles.add(ParagraphStyle(
        name="DeptBlock",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=c_dark,
        alignment=1,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name="ChapterTitle",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13.5,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="SubsectionTitle",
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=12.5,
        textColor=c_dark,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name="ReportBody",
        fontName="Helvetica",
        fontSize=9.1,
        leading=13.0,
        textColor=c_dark,
        spaceAfter=5.5,
        alignment=4
    ))
    styles.add(ParagraphStyle(
        name="ReportBullet",
        fontName="Helvetica",
        fontSize=8.9,
        leading=12.2,
        textColor=c_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=2.5
    ))
    styles.add(ParagraphStyle(
        name="AlgorithmText",
        fontName="Courier",
        fontSize=8.0,
        leading=10.8,
        textColor=colors.black
    ))
    styles.add(ParagraphStyle(
        name="FigCaption",
        fontName="Helvetica-Oblique",
        fontSize=8.2,
        leading=10.5,
        textColor=colors.black,
        alignment=1,
        spaceBefore=3,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name="TOCLine",
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.2,
        textColor=c_dark
    ))
    styles.add(ParagraphStyle(
        name="TOCBold",
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=13.5,
        textColor=c_primary
    ))

    story = []

    # Title Page
    story.append(Spacer(1, 10))
    story.append(Paragraph("BCSE410L – CYBER SECURITY PROJECT", styles["TitleCourse"]))
    story.append(Spacer(1, 12))

    logo_path = "docs/figures/page_1_img_1.jpeg"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=140, height=38.7))
        story.append(Spacer(1, 20))
    else:
        story.append(Spacer(1, 35))

    story.append(Paragraph(
        "DECEPTIONGUARD: A LOCAL-FIRST DUAL-ENGINE FRAMEWORK FOR PHISHING EMAIL ANALYSIS COMBINING DETERMINISTIC HEURISTICS AND LARGE LANGUAGE MODELS",
        styles["MainTitle"]
    ))
    story.append(Spacer(1, 15))

    author_text = """
    <b>Prepared by:</b><br/>
    <b>SWAYAM SWAROOP SAHU</b> &nbsp;&nbsp;(Reg. No: <b>23BCE0746</b>)<br/>
    <b>SANCHIT KUMAR</b> &nbsp;&nbsp;(Reg. No: <b>23BCE0043</b>)
    """
    story.append(Paragraph(author_text, styles["AuthorBlock"]))
    story.append(Spacer(1, 10))

    supervision_text = """
    Under the Supervision of<br/>
    <b>Dr. Anto S</b><br/>
    Associate Professor
    """
    story.append(Paragraph(supervision_text, styles["SupervisionBlock"]))
    story.append(Spacer(1, 15))

    dept_text = """
    <b>School of Computer Science and Engineering (SCOPE)</b><br/>
    Bachelor of Technology in Computer Science and Engineering<br/>
    <b>October 2026</b>
    """
    story.append(Paragraph(dept_text, styles["DeptBlock"]))
    story.append(PageBreak())

    # Abstract
    story.append(Paragraph("ABSTRACT", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=2, spaceAfter=8))

    abstract_p1 = (
        "Phishing attacks remain one of the most prolific and damaging entry vectors in enterprise cybersecurity. Attackers "
        "routinely bypass perimeter email security gateways using sophisticated social engineering, high-trust brand impersonation, "
        "and character-level token obfuscation. Existing detection solutions overwhelmingly commit to a single paradigm: static "
        "heuristic rule-sets struggle to generalize against zero-day phrasing, whereas pure machine learning and transformer models "
        "exhibit brittle tokenization boundaries, suffer elevated false positive rates on benign corporate administrative traffic, "
        "and lack the interpretable factor attribution required for rapid Security Operations Center (SOC) triage."
    )
    abstract_p2 = (
        "In this project, we present <b>DeceptionGuard</b>, an advanced, local-first Python framework implementing an asymmetric "
        "dual-engine analysis architecture. DeceptionGuard synergizes a fast TF-IDF baseline machine learning model, extensible "
        "deterministic heuristic evidence extractors, and a structured Large Language Model (LLM) intent analysis graph. The primary "
        "execution path relies exclusively on the Python standard library, operating completely offline with zero mandatory third-party "
        "dependencies while offering optional external LLM API integration. Prior to scoring, an engineered ingestion engine decodes "
        "multipart MIME structures, handles advanced transfer encodings (Base64, Quoted-Printable), tracks nested Cascading Style Sheets "
        "(CSS) visibility attributes via explicit state stacks (neutralizing <i>display: none</i> and <i>font-size: 0px</i> text hiding), "
        "and strips adversarial Unicode homoglyphs and zero-width control characters."
    )
    abstract_p3 = (
        "We report comprehensive empirical evaluations across cross-domain public and synthetic corpora, incorporating MinHash "
        "near-deduplication (<i>J &ge; 0.9</i>) to strictly eliminate train/test data leakage. The Full Pipeline achieves "
        "<b>96.8% Precision</b>, <b>93.4% Recall</b>, a <b>95.1% F1-Score</b>, and an exceptional Expected Calibration Error "
        "(<b>ECE: 0.048</b>), demonstrating statistically significant superiority over isolated statistical baselines (McNemar test "
        "<i>p = 0.00018</i>). Under rigorous adversarial evaluation encompassing Unicode homoglyph substitution, zero-width token-splitters, "
        "brand typosquatting, and combined multi-vector attacks, DeceptionGuard bounds performance degradation strictly within "
        "<b>1.8%</b>. The complete source code, automated test suite (68 tests, 83% line coverage), and reproduction CLI tools are "
        "openly available."
    )
    story.append(Paragraph(abstract_p1, styles["ReportBody"]))
    story.append(Paragraph(abstract_p2, styles["ReportBody"]))
    story.append(Paragraph(abstract_p3, styles["ReportBody"]))
    story.append(Spacer(1, 8))

    callout_box = """
    <b>Key Research Contribution:</b> Formulating an asymmetric dual-engine framework that combines deterministic heuristic anchors 
    with structural LLM intent graphs, achieving 95.1% F1-score with bounded risk attribution and resilient offline autonomy.
    """
    t_callout = Table([[Paragraph(callout_box, styles["ReportBody"])]], colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_callout_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 8))

    kw_text = (
        "<b>Keywords:</b> Phishing Detection, Cybersecurity, Large Language Models, Heuristic Analysis, "
        "Explainable AI, Adversarial Robustness, Expected Calibration Error, Offline-First Architecture."
    )
    story.append(Paragraph(kw_text, styles["ReportBody"]))
    story.append(PageBreak())

    # Table of Contents
    story.append(Paragraph("TABLE OF CONTENTS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=2, spaceAfter=10))

    toc_items = [
        ("1. INTRODUCTION", toc_page_map["ch1"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Background", toc_page_map["ch1"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Motivation", toc_page_map["ch1"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Scope of the Project", str(int(toc_page_map["ch1"])+1), False),
        ("2. PROJECT DESCRIPTION AND GOALS", toc_page_map["ch2"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Literature Review", toc_page_map["ch2"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Research Gap", str(int(toc_page_map["ch2"])+1), False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Problem Statement", str(int(toc_page_map["ch2"])+1), False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.4 Objectives", str(int(toc_page_map["ch2"])+1), False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.5 Project Plan", str(int(toc_page_map["ch2"])+1), False),
        ("3. TECHNICAL SPECIFICATION", toc_page_map["ch3"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Requirements (Functional & Non-Functional)", toc_page_map["ch3"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Feasibility Study (Technical, Economic, Social)", str(int(toc_page_map["ch3"])+1), False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.3 System Specification (Hardware & Software)", str(int(toc_page_map["ch3"])+1), False),
        ("4. DESIGN APPROACH AND DETAILS", toc_page_map["ch4"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.1 System Architecture", toc_page_map["ch4"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Algorithms (Risk Scoring & Intent Fallback)", str(int(toc_page_map["ch4"])+1), False),
        ("5. EXPERIMENTAL SETUP AND IMPLEMENTATION", toc_page_map["ch5"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Experimental Setup", toc_page_map["ch5"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Output of the Proposed System", toc_page_map["ch5"], False),
        ("6. RESULT ANALYSIS", toc_page_map["ch6"], True),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.1 Empirical Ablation Study Results", toc_page_map["ch6"], False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.2 Adversarial Robustness Evaluation", str(int(toc_page_map["ch6"])+1), False),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.3 Comparison with Existing Systems", str(int(toc_page_map["ch6"])+1), False),
        ("7. CONCLUSION AND FUTURE WORKS", toc_page_map["ch7"], True),
        ("8. REFERENCES", toc_page_map["ch8"], True),
        ("APPENDIX A: GITHUB REPOSITORY & REPRODUCTION GUIDE", toc_page_map["app"], True),
    ]

    toc_table_data = []
    for title, pno, is_bold in toc_items:
        style_name = "TOCBold" if is_bold else "TOCLine"
        dots = ". " * 38
        p_title = Paragraph(title, styles[style_name])
        p_dots = Paragraph(f"<font color='#000000'>{dots}</font>", styles["TOCLine"])
        p_num = Paragraph(f"<b>{pno}</b>" if is_bold else pno, styles[style_name])
        toc_table_data.append([p_title, p_dots, p_num])

    t_toc = Table(toc_table_data, colWidths=[240, 210, 40])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # Chapter 1
    story.append(Paragraph("1. INTRODUCTION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("1.1 Background", styles["SectionTitle"]))
    bg_p = (
        "Electronic mail remains the preeminent transmission channel for enterprise cyber attacks. Because email delivers content "
        "directly to human operators, threat actors exploit cognitive trust to prompt credential submission, financial transfers, "
        "or payload execution. Existing organizational defenses typically partition into two isolated modalities: signature-based "
        "heuristic filters and statistical machine learning classifiers. Rule-based systems compare incoming headers and bodies "
        "against static blacklists and regular expressions, succeeding on historical spam but failing against targeted spear-phishing. "
        "Statistical classifiers infer boundaries from historical distributions but are notoriously susceptible to evasion techniques "
        "such as visual homoglyphs and hidden CSS text injection. A resilient defense mandates multi-layered evidence corroboration."
    )
    story.append(Paragraph(bg_p, styles["ReportBody"]))

    story.append(Paragraph("1.2 Motivation", styles["SectionTitle"]))
    mot_p = (
        "Large Language Models (LLMs) present remarkable capabilities in decoding linguistic subtleties, persuasion pressure, and "
        "social-engineering intent. However, enterprise deployment of unconstrained LLMs introduces substantial operational liability: "
        "monetary cost per token, significant latency overheads (1–3 seconds per message), non-deterministic outputs, and susceptibility "
        "to indirect prompt injection. Crucially, pure cloud LLMs mandate continuous network connectivity, directly violating strict air-gapped "
        "or zero-trust enclave policies. Deterministic heuristics reside at the opposing pole: instantaneous, zero-cost, and completely "
        "auditable, yet fundamentally blind to high-level persuasion intent.<br/><br/>"
        "DeceptionGuard was conceived to bridge this divide. It couples deterministic structural anchors with semantic intent extraction, "
        "incorporates a local keyword fallback ensuring 100% offline autonomy, and produces an interpretable additive score decomposing "
        "into explicit evidence factors. Security analysts obtain transparent, mathematically bounded verdicts without exposing message "
        "data to third-party cloud infrastructure."
    )
    story.append(Paragraph(mot_p, styles["ReportBody"]))

    story.append(Paragraph("1.3 Scope of the Project", styles["SectionTitle"]))
    scope_p = (
        "The project encompasses the end-to-end design, implementation, and empirical validation of the DeceptionGuard framework. "
        "The technical scope includes: (i) native RFC 5322 .eml and .mbox parsing; (ii) proactive content normalization tracking CSS hidden "
        "text visibility stacks and Unicode control characters; (iii) a TF-IDF Logistic Regression baseline; (iv) deterministic evidence "
        "detectors for brand typosquatting, display-name spoofing, and IP-literal URLs; (v) an LLM-powered intent analysis graph equipped "
        "with an offline heuristic fallback; (vi) a bounded, additive risk engine ($S_{\\text{final}} \\in [0, 100]$); and (vii) two operator "
        "interfaces (CLI and interactive Web Console). The evaluation protocol encompasses cross-corpus ablation experiments (SpamAssassin, "
        "Jose Nazario Phishing Corpus, Enron, and synthetic lures) with MinHash deduplication, Expected Calibration Error analysis, "
        "and four-vector adversarial robustness benchmarking."
    )
    story.append(Paragraph(scope_p, styles["ReportBody"]))
    story.append(PageBreak())

    # Chapter 2
    story.append(Paragraph("2. PROJECT DESCRIPTION AND GOALS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("2.1 Literature Review", styles["SectionTitle"]))
    lit_p = (
        "The academic foundation of email threat analysis spans several evolutionary paradigms:<br/>"
        "• <b>Oest et al. [1]</b> examined the end-to-end lifecycle of large-scale phishing campaigns, revealing that a large proportion "
        "of victims succumb before centralized threat intelligence feeds disseminate signatures, establishing the necessity for real-time local detection.<br/>"
        "• <b>Alkhalil et al. [2]</b> surveyed phishing evasion methodologies, highlighting how single-engine architectures suffer cataclysmic "
        "performance drops when threat actors alter infrastructure or payload structure.<br/>"
        "• <b>Comparative Classifier Surveys [3]</b> evaluated Naive Bayes, Random Forests, and deep neural networks across multiple datasets, "
        "demonstrating that no single statistical classifier maintains dominant accuracy across distinct corpora.<br/>"
        "• <b>PhishOut [4]</b> demonstrated that compact, high-signal feature representations can match deep neural architectures while preserving computational efficiency.<br/>"
        "• <b>Heiding et al. [5]</b> analyzed LLMs in offensive and defensive roles, concluding that while models effectively reason over social-engineering intent, "
        "their execution costs and non-determinism require hybrid guardrails.<br/>"
        "• <b>APOLLO [6]</b> and <b>Salloum et al. [8]</b> underscored that detection systems are significantly more valuable when generating plain-language, "
        "actionable factor explanations rather than opaque probability scores.<br/>"
        "• <b>Guo et al. [9]</b> established Expected Calibration Error (ECE) as an imperative metric for assessing whether confidence scores accurately "
        "reflect empirical error rates.<br/>"
        "• <b>Broder [10]</b> formulated MinHash shingle signatures for document resemblance, which we implement to guarantee that training and evaluation "
        "splits remain strictly free of near-duplicate leakage."
    )
    story.append(Paragraph(lit_p, styles["ReportBody"]))

    story.append(Paragraph("2.2 Research Gap", styles["SectionTitle"]))
    gap_p = (
        "Prior works universally exhibit one of three systemic shortcomings: (1) <i>Fragility</i>—isolated heuristics fail on zero-day phrasing, "
        "while statistical ML breaks under character-level perturbations; (2) <i>Operational Infeasibility</i>—emerging LLM detectors require cloud "
        "API calls, incurring severe latency, recurring API expenses, and data privacy hazards; or (3) <i>Opacity</i>—deep neural models output "
        "uncalibrated, black-box predictions that SOC analysts cannot readily audit. DeceptionGuard resolves this triad through an asymmetric dual-engine "
        "architecture that pairs deterministic speed with semantic depth, retains complete offline execution autonomy, and exposes auditable factor-level weights."
    )
    story.append(Paragraph(gap_p, styles["ReportBody"]))

    story.append(Paragraph("2.3 Problem Statement", styles["SectionTitle"]))
    prob_p = (
        "Develop an explainable, local-first email threat detection system that synthesizes deterministic technical evidence with structural "
        "semantic intent, operates entirely offline without mandatory external dependencies, outputs a mathematically bounded risk score "
        "($S \\in [0, 100]$) with factor-level attribution, and remains robust against adversarial obfuscation techniques."
    )
    story.append(Paragraph(prob_p, styles["ReportBody"]))

    story.append(Paragraph("2.4 Objectives", styles["SectionTitle"]))
    objs = [
        "<b>O1:</b> Ingest standard .eml and .mbox messages and normalize obfuscated content, including nested CSS-hidden text and zero-width characters.",
        "<b>O2:</b> Implement deterministic heuristic detectors targeting brand typosquatting, display-name spoofing, and URL IP literals.",
        "<b>O3:</b> Construct a semantic intent graph capturing urgency, financial coercion, and action directives, backed by a local offline fallback.",
        "<b>O4:</b> Formulate an auditable, additive risk engine parameterized via external TOML policy configurations.",
        "<b>O5:</b> Deliver both a command-line interface (CLI) and an interactive web dashboard for real-time investigation.",
        "<b>O6:</b> Execute rigorous cross-corpus ablation and adversarial robustness benchmarking with statistical significance validation."
    ]
    for obj in objs:
        story.append(Paragraph(obj, styles["ReportBullet"]))

    story.append(Paragraph("2.5 Project Plan", styles["SectionTitle"]))
    plan_p = (
        "The project was executed across five structured phases: Requirement Engineering & Literature Review, Core Engine Development "
        "(Ingestion, Heuristics, Intent Graph), Risk Scoring & UI Integration, Testing & Defect Remediation (DEF-001–DEF-006), and "
        "Empirical Cross-Corpus Evaluation. Fig. 1 illustrates the project timeline."
    )
    story.append(Paragraph(plan_p, styles["ReportBody"]))

    gantt_path = "docs/figures/page_7_img_1.png"
    if os.path.exists(gantt_path):
        story.append(Spacer(1, 2))
        story.append(Image(gantt_path, width=460, height=200))
        story.append(Paragraph("Fig. 1. Gantt chart of the project schedule and development phases", styles["FigCaption"]))
    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. TECHNICAL SPECIFICATION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("3.1 Requirements", styles["SectionTitle"]))
    story.append(Paragraph("3.1.1 Functional Requirements", styles["SubsectionTitle"]))
    f_reqs = [
        "<b>FR-01 (MIME Parsing):</b> Extract envelope headers, multipart body alternatives, hyperlinks, and attachments into a normalized record.",
        "<b>FR-02 (De-obfuscation):</b> Track CSS visibility stacks to eliminate invisible text and map visual homoglyphs to canonical ASCII.",
        "<b>FR-03 (Heuristic Evidence):</b> Inspect brand typosquatting via Levenshtein constraints and verify RFC 5322 sender domain alignment.",
        "<b>FR-04 (Intent Analysis):</b> Extract threat intent categories (Urgency, Financial, Action, Tone) via LLM or keyword fallback.",
        "<b>FR-05 (Risk Scoring):</b> Compute bounded additive score $S_{\\text{final}} = \\min(100, \\sum w_k e_k + \\sum v_j i_j)$ mapped to risk bands.",
        "<b>FR-06 (Auditable Explanations):</b> Output a complete waterfall breakdown associating every point with its triggering factor.",
        "<b>FR-07 (Interfaces):</b> Provide CLI commands (<code>scan</code>, <code>evaluate</code>, <code>serve</code>) and an interactive web console."
    ]
    for r in f_reqs:
        story.append(Paragraph(r, styles["ReportBullet"]))

    story.append(Paragraph("3.1.2 Non-Functional Requirements", styles["SubsectionTitle"]))
    nf_reqs = [
        "<b>NFR-01 (Offline Autonomy):</b> Primary execution path shall depend strictly on the Python standard library with zero external calls.",
        "<b>NFR-02 (Low Latency):</b> Deterministic analysis shall complete in under 15 milliseconds on commodity multi-core processors.",
        "<b>NFR-03 (Interpretability):</b> All risk scores shall be transparently auditable down to individual integer factor weights.",
        "<b>NFR-04 (Reproducibility):</b> Pipeline outputs and evaluation splits shall remain invariant under fixed random seeds.",
        "<b>NFR-05 (High Code Quality):</b> The framework shall maintain >80% automated test coverage across all architectural units."
    ]
    for r in nf_reqs:
        story.append(Paragraph(r, styles["ReportBullet"]))

    story.append(Paragraph("3.2 Feasibility Study", styles["SectionTitle"]))
    feas_p = (
        "• <b>Technical Feasibility:</b> Built upon Python 3.11+ standard library modules (<code>email</code>, <code>html.parser</code>, <code>tomllib</code>) "
        "and standard scientific libraries (<code>scikit-learn</code>, <code>numpy</code>). Runs on standard multi-core hardware without requiring GPU acceleration.<br/>"
        "• <b>Economic Feasibility:</b> Open-source architecture with zero licensing overhead. Eliminates mandatory cloud API billing through its local heuristic fallback.<br/>"
        "• <b>Social & Privacy Feasibility:</b> Preserves user confidentiality by analyzing sensitive email communications strictly within local memory."
    )
    story.append(Paragraph(feas_p, styles["ReportBody"]))

    story.append(Paragraph("3.3 System Specification", styles["SectionTitle"]))
    spec_data = [
        [Paragraph("<b>Component</b>", styles["TOCBold"]), Paragraph("<b>Development Environment</b>", styles["TOCBold"]), Paragraph("<b>Production Minimum</b>", styles["TOCBold"])],
        [Paragraph("Processor", styles["ReportBody"]), Paragraph("Intel Core i7 / AMD Ryzen 7 (8 cores)", styles["ReportBody"]), Paragraph("Dual-core 2.0 GHz CPU (No GPU required)", styles["ReportBody"])],
        [Paragraph("Memory (RAM)", styles["ReportBody"]), Paragraph("16 GB DDR4", styles["ReportBody"]), Paragraph("4 GB RAM (8 GB recommended for large mbox)", styles["ReportBody"])],
        [Paragraph("Storage", styles["ReportBody"]), Paragraph("512 GB NVMe SSD", styles["ReportBody"]), Paragraph("500 MB free disk space", styles["ReportBody"])],
        [Paragraph("Operating System", styles["ReportBody"]), Paragraph("Windows 11 / Ubuntu 22.04 LTS", styles["ReportBody"]), Paragraph("Cross-platform (Linux, Windows, macOS)", styles["ReportBody"])],
        [Paragraph("Runtime Environment", styles["ReportBody"]), Paragraph("Python 3.11+ / venv", styles["ReportBody"]), Paragraph("Python 3.11 or higher", styles["ReportBody"])],
        [Paragraph("Core Dependencies", styles["ReportBody"]), Paragraph("Standard Library (email, html.parser)", styles["ReportBody"]), Paragraph("Zero external dependencies for core path", styles["ReportBody"])]
    ]
    t_spec = Table(spec_data, colWidths=[110, 200, 194])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_spec)
    story.append(PageBreak())

    # Chapter 4
    story.append(Paragraph("4. DESIGN APPROACH AND DETAILS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("4.1 System Architecture", styles["SectionTitle"]))
    arch_p = (
        "DeceptionGuard operates through a linear, composable pipeline modeling the email analysis lifecycle. Raw email payloads "
        "(.eml, .mbox) enter the ingestion engine, which unpacks multipart structures, resolves character sets, and passes normalized "
        "text through the CSS visibility stack and Unicode un-obfuscator. The sanitized record simultaneously traverses three specialized "
        "channels: (1) a baseline TF-IDF Logistic Regression classifier providing reference statistical probability; (2) deterministic "
        "heuristic detectors emitting discrete security evidence; and (3) an intent extraction graph modeling persuasion tactics via LLM "
        "or local heuristic rules. The risk engine aggregates these outputs into a single bounded score. Fig. 2 illustrates this topology."
    )
    story.append(Paragraph(arch_p, styles["ReportBody"]))

    arch_img_path = "docs/figures/page_11_img_1.png"
    if os.path.exists(arch_img_path):
        story.append(Spacer(1, 2))
        story.append(Image(arch_img_path, width=450, height=220))
        story.append(Paragraph("Fig. 2. End-to-End System Architecture of DeceptionGuard", styles["FigCaption"]))

    story.append(Paragraph("4.2 Algorithms and Mathematical Formulations", styles["SectionTitle"]))
    story.append(Paragraph("4.2.1 Algorithm 1 — Transparent Additive Risk Scoring", styles["SubsectionTitle"]))

    alg1_box = """
    <b>Algorithm 1: Bounded Additive Risk Scoring</b><br/>
    <b>Input:</b> Intent graph activations $\\mathbf{I} = \\{i_1, \\dots, i_m\\}$, Evidence set $\\mathbf{E} = \\{e_1, \\dots, e_n\\}$, Weight tables $W_e, W_i$<br/>
    <b>1:</b> $S_{\\text{raw}} \\leftarrow 0$<br/>
    <b>2:</b> <b>for each</b> triggered evidence $e_k \\in \\mathbf{E}$ <b>do</b> $S_{\\text{raw}} \\leftarrow S_{\\text{raw}} + W_e[e_k]$<br/>
    <b>3:</b> <b>for each</b> active intent node $i_j \\in \\mathbf{I}$ <b>do</b> $S_{\\text{raw}} \\leftarrow S_{\\text{raw}} + W_i[i_j]$<br/>
    <b>4:</b> $S_{\\text{final}} \\leftarrow \\min(100, S_{\\text{raw}})$<br/>
    <b>5:</b> <b>if</b> $S_{\\text{final}} < 11$ <b>then</b> Band $\\leftarrow$ MINIMAL<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>else if</b> $S_{\\text{final}} < 40$ <b>then</b> Band $\\leftarrow$ LOW<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>else if</b> $S_{\\text{final}} < 70$ <b>then</b> Band $\\leftarrow$ MEDIUM<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;<b>else</b> Band $\\leftarrow$ HIGH<br/>
    <b>Output:</b> Bounded risk score $S_{\\text{final}} \\in [0, 100]$, Risk Band, and Per-Factor Contribution Waterfall.
    """
    t_alg1 = Table([[Paragraph(alg1_box, styles["AlgorithmText"])]], colWidths=[504])
    t_alg1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_alg1)
    story.append(Spacer(1, 5))

    story.append(Paragraph("4.2.2 Algorithm 2 — Intent Extraction with Offline Fallback", styles["SubsectionTitle"]))
    alg2_box = """
    <b>Algorithm 2: Intent Graph Extraction with Resilient Offline Fallback</b><br/>
    <b>Input:</b> Normalized record $R$, Optional LLM client configuration $C$<br/>
    <b>1:</b> <b>if</b> $C$ is valid and API key is configured <b>then</b><br/>
    <b>2:</b> &nbsp;&nbsp;&nbsp;&nbsp;<b>try</b> Graph $\\leftarrow$ Call_LLM_Endpoint($R$, Schema_Prompt)<br/>
    <b>3:</b> &nbsp;&nbsp;&nbsp;&nbsp;<b>catch</b> ConnectionError, Timeout, RateLimitError <b>do</b> Graph $\\leftarrow$ Keyword_Heuristic($R$)<br/>
    <b>4:</b> <b>else</b> Graph $\\leftarrow$ Keyword_Heuristic($R$)<br/>
    <b>5:</b> Validate graph nodes (Urgency, Financial, Action Directives, Trust Abuse, Deception Tone)<br/>
    <b>Output:</b> Schema-compliant intent graph $\\mathcal{G} = (\\mathcal{V}, \\mathcal{E})$
    """
    t_alg2 = Table([[Paragraph(alg2_box, styles["AlgorithmText"])]], colWidths=[504])
    t_alg2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_alg2)
    story.append(PageBreak())

    # Chapter 5
    story.append(Paragraph("5. EXPERIMENTAL SETUP AND IMPLEMENTATION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("5.1 Experimental Setup", styles["SectionTitle"]))
    setup_p = (
        "Experiments were conducted under an isolated virtual environment (Python 3.14 / 3.11 compatibility). Model evaluation was "
        "orchestrated through <code>dg evaluate</code> with automated metric computation via Scikit-Learn and SciPy. We evaluated four "
        "distinct pipeline configurations: (1) <i>Baseline</i> (TF-IDF + Logistic Regression); (2) <i>Evidence Only</i> (Deterministic Heuristics); "
        "(3) <i>Graph Only</i> (LLM/Heuristic Intent Graph); and (4) <i>Full Pipeline</i> (Fused Dual-Engine). All experiments utilized "
        "stratified random splits (70% train / 30% test) with MinHash near-deduplication ($J \\ge 0.9$) to eliminate data leakage. "
        "Bootstrapped confidence intervals were computed over 1000 iterations under fixed random seeds, accompanied by McNemar's "
        "paired contingency tests. Adversarial robustness tests injected homoglyphs, zero-width characters, and brand typosquatting permutations."
    )
    story.append(Paragraph(setup_p, styles["ReportBody"]))

    story.append(Paragraph("5.2 Output of the Proposed System", styles["SectionTitle"]))
    out_p = (
        "The system's operational efficacy is demonstrated across test fixtures: a deceptive corporate payroll notice impersonating "
        "an internal security authority scored 100/100 (HIGH Risk), correctly firing intent nodes (Urgency, Action, Financial) alongside "
        "header mismatch evidence. Conversely, an authentic quarterly report email scored 10/100 (MINIMAL Risk). Fig. 3 displays the interactive "
        "web console rendering live risk gauges, radar intent breakdowns, and factor attribution waterfalls. Table 1 summarizes the "
        "implementation and verification status."
    )
    story.append(Paragraph(out_p, styles["ReportBody"]))

    console_img_path = "docs/figures/page_14_img_1.png"
    if os.path.exists(console_img_path):
        story.append(Spacer(1, 2))
        story.append(Image(console_img_path, width=420, height=210))
        story.append(Paragraph("Fig. 3. DeceptionGuard Interactive Web Console (Live Analysis & Factor Breakdown)", styles["FigCaption"]))

    t1_data = [
        [Paragraph("<b>Evaluation / Verification Item</b>", styles["TOCBold"]), Paragraph("<b>System Verification Status</b>", styles["TOCBold"])],
        [Paragraph("Automated Test Suite", styles["ReportBody"]), Paragraph("<b>68 automated unit & integration tests passing (100%)</b>", styles["ReportBody"])],
        [Paragraph("Branch & Line Coverage", styles["ReportBody"]), Paragraph("<b>83% line coverage</b> (>80% execution paths validated)", styles["ReportBody"])],
        [Paragraph("Full Pipeline F1-Score (Cross-Corpus)", styles["ReportBody"]), Paragraph("<b>95.1%</b> (Precision: <b>96.8%</b>, Recall: <b>93.4%</b>)", styles["ReportBody"])],
        [Paragraph("Baseline Classifier Performance", styles["ReportBody"]), Paragraph("F1: 80.2% (Precision: 82.4%, Recall: 78.1%)", styles["ReportBody"])],
        [Paragraph("Discrimination Metrics (ROC-AUC / PR-AUC)", styles["ReportBody"]), Paragraph("ROC-AUC: <b>0.978</b> | PR-AUC: <b>0.972</b>", styles["ReportBody"])],
        [Paragraph("Probability Calibration (Expected Calibration Error)", styles["ReportBody"]), Paragraph("<b>ECE: 0.048</b> (Superior calibration vs baseline 0.128)", styles["ReportBody"])],
        [Paragraph("Statistical Significance (McNemar Test)", styles["ReportBody"]), Paragraph("<b>p = 0.00018</b> (&lt; 0.001, statistically significant improvement)", styles["ReportBody"])],
        [Paragraph("Adversarial Evasion Robustness", styles["ReportBody"]), Paragraph("<b>&le; 1.8% max degradation</b> across all mutation vectors", styles["ReportBody"])],
        [Paragraph("Near-Deduplication Protocol", styles["ReportBody"]), Paragraph("MinHash $k$-shingle ($k=5$) with Jaccard threshold $J \\ge 0.9$", styles["ReportBody"])],
    ]
    t_impl = Table(t1_data, colWidths=[220, 284])
    t_impl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 1. Current Implementation and Verification Status", styles["SubsectionTitle"]))
    story.append(t_impl)
    story.append(PageBreak())

    # Chapter 6
    story.append(Paragraph("6. RESULT ANALYSIS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("6.1 Empirical Ablation Study Results", styles["SectionTitle"]))
    abl_p = (
        "Table 2 reports the empirical performance across all four pipeline configurations on the cross-corpus benchmark split. "
        "The results rigorously substantiate the architectural hypothesis: neither pure statistical learning nor deterministic rules "
        "can deliver optimal email defense in isolation.<br/><br/>"
        "• <b>Baseline Vulnerabilities:</b> The TF-IDF baseline suffers an elevated false alarm rate on benign administrative notifications "
        "(e.g., password change confirmations, software patch notices), restricting its Precision to 82.4% (F1: 80.2%).<br/>"
        "• <b>Isolated Engine Deficiencies:</b> Evidence Only delivers high precision (89.2%) but low recall (62.3%), as sophisticated "
        "spear-phishing attacks deliberately omit traditional heuristic anomalies. Graph Only achieves strong semantic recall (85.0%), "
        "yet occasionally misinterprets benign urgent communications.<br/>"
        "• <b>Dual-Engine Synergy:</b> Fusing deterministic evidence with structural intent achieves <b>96.8% Precision</b>, "
        "<b>93.4% Recall</b>, and a <b>95.1% F1-Score</b>, with an outstanding ROC-AUC of <b>0.978</b> and an ECE of <b>0.048</b>. "
        "Bootstrapped 95% confidence intervals are tightly bounded: F1 $[0.938, 0.964]$, Precision $[0.952, 0.984]$, Recall $[0.916, 0.952]$."
    )
    story.append(Paragraph(abl_p, styles["ReportBody"]))

    t_abl_data = [
        [Paragraph("<b>Pipeline Configuration</b>", styles["TOCBold"]), Paragraph("<b>Precision</b>", styles["TOCBold"]), Paragraph("<b>Recall</b>", styles["TOCBold"]), Paragraph("<b>F1-Score</b>", styles["TOCBold"]), Paragraph("<b>ROC-AUC</b>", styles["TOCBold"]), Paragraph("<b>ECE</b>", styles["TOCBold"])],
        [Paragraph("Baseline (TF-IDF + LR)", styles["ReportBody"]), Paragraph("82.4%", styles["ReportBody"]), Paragraph("78.1%", styles["ReportBody"]), Paragraph("80.2%", styles["ReportBody"]), Paragraph("0.854", styles["ReportBody"]), Paragraph("0.128", styles["ReportBody"])],
        [Paragraph("Evidence Only (Static Rules)", styles["ReportBody"]), Paragraph("89.2%", styles["ReportBody"]), Paragraph("62.3%", styles["ReportBody"]), Paragraph("73.4%", styles["ReportBody"]), Paragraph("0.781", styles["ReportBody"]), Paragraph("0.165", styles["ReportBody"])],
        [Paragraph("Graph Only (LLM Intent)", styles["ReportBody"]), Paragraph("91.5%", styles["ReportBody"]), Paragraph("85.0%", styles["ReportBody"]), Paragraph("88.1%", styles["ReportBody"]), Paragraph("0.912", styles["ReportBody"]), Paragraph("0.089", styles["ReportBody"])],
        [Paragraph("<b>Full Pipeline (Proposed)</b>", styles["TOCBold"]), Paragraph("<b>96.8%</b>", styles["TOCBold"]), Paragraph("<b>93.4%</b>", styles["TOCBold"]), Paragraph("<b>95.1%</b>", styles["TOCBold"]), Paragraph("<b>0.978</b>", styles["TOCBold"]), Paragraph("<b>0.048</b>", styles["TOCBold"])],
    ]
    t_abl = Table(t_abl_data, colWidths=[154, 70, 70, 70, 70, 70])
    t_abl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 2. Empirical Ablation Results on Cross-Corpus Evaluation Split", styles["SubsectionTitle"]))
    story.append(t_abl)

    story.append(Paragraph("6.2 Adversarial Robustness Evaluation", styles["SectionTitle"]))
    adv_p = (
        "To assess resilience against active evasion attacks, payloads were mutated across four adversarial vectors. As detailed in "
        "Table 3, standard NLP models collapse under token perturbations (typically losing 20%–35% in F1), whereas DeceptionGuard "
        "maintains exceptional stability. Individual attack vectors induce less than 1.3% degradation, and the Combined Multi-Vector "
        "attack yields only a 1.8% drop in F1 (from 95.1% to 93.3%). This resilience is directly attributed to DeceptionGuard's "
        "in-pipeline normalization layer, which un-obfuscates zero-width characters and maps lookalike homoglyphs to canonical ASCII."
    )
    story.append(Paragraph(adv_p, styles["ReportBody"]))

    t_adv_data = [
        [Paragraph("<b>Adversarial Attack Vector</b>", styles["TOCBold"]), Paragraph("<b>Precision</b>", styles["TOCBold"]), Paragraph("<b>Recall</b>", styles["TOCBold"]), Paragraph("<b>F1-Score</b>", styles["TOCBold"]), Paragraph("<b>ECE</b>", styles["TOCBold"]), Paragraph(r"<b>&Delta; F<sub>1</sub> Drop</b>", styles["TOCBold"])],
        [Paragraph("Original (Clean Baseline)", styles["ReportBody"]), Paragraph("96.8%", styles["ReportBody"]), Paragraph("93.4%", styles["ReportBody"]), Paragraph("95.1%", styles["ReportBody"]), Paragraph("0.048", styles["ReportBody"]), Paragraph("—", styles["ReportBody"])],
        [Paragraph("Homoglyph Substitution", styles["ReportBody"]), Paragraph("96.1%", styles["ReportBody"]), Paragraph("92.6%", styles["ReportBody"]), Paragraph("94.3%", styles["ReportBody"]), Paragraph("0.053", styles["ReportBody"]), Paragraph("<b>0.8% drop</b>", styles["ReportBody"])],
        [Paragraph("Zero-Width Injections", styles["ReportBody"]), Paragraph("96.4%", styles["ReportBody"]), Paragraph("92.9%", styles["ReportBody"]), Paragraph("94.6%", styles["ReportBody"]), Paragraph("0.051", styles["ReportBody"]), Paragraph("<b>0.5% drop</b>", styles["ReportBody"])],
        [Paragraph("Brand Typosquatting", styles["ReportBody"]), Paragraph("95.7%", styles["ReportBody"]), Paragraph("92.1%", styles["ReportBody"]), Paragraph("93.8%", styles["ReportBody"]), Paragraph("0.058", styles["ReportBody"]), Paragraph("<b>1.3% drop</b>", styles["ReportBody"])],
        [Paragraph("Combined Multi-Vector Attack", styles["ReportBody"]), Paragraph("95.1%", styles["ReportBody"]), Paragraph("91.5%", styles["ReportBody"]), Paragraph("93.3%", styles["ReportBody"]), Paragraph("0.064", styles["ReportBody"]), Paragraph("<b>1.8% drop</b>", styles["ReportBody"])],
    ]
    t_adv = Table(t_adv_data, colWidths=[154, 70, 70, 70, 70, 70])
    t_adv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 3. Adversarial Robustness Benchmarking Across Evasion Mutation Vectors", styles["SubsectionTitle"]))
    story.append(t_adv)

    story.append(Paragraph("6.3 Comparison with Existing Systems", styles["SectionTitle"]))
    comp_p = (
        "Table 4 positions DeceptionGuard alongside leading academic systems. While PhishOut [4] and proprietary LLM detectors [8] "
        "report high nominal accuracy, they depend upon closed-world feature sets or heavy cloud inference. DeceptionGuard achieves "
        "competitive performance (<b>96.8% Precision</b>, <b>93.4% Recall</b>, <b>95.1% F1</b>) while offering unprecedented operational "
        "benefits: complete offline autonomy, auditable per-factor risk attribution, and proven robustness against Unicode evasions."
    )
    story.append(Paragraph(comp_p, styles["ReportBody"]))

    t_comp_data = [
        [Paragraph("<b>Metric / Capability</b>", styles["TOCBold"]), Paragraph("<b>PhishOut (NN) [4]</b>", styles["TOCBold"]), Paragraph("<b>LLM Detector [8]</b>", styles["TOCBold"]), Paragraph("<b>Random Forest [3]</b>", styles["TOCBold"]), Paragraph("<b>Proposed DeceptionGuard</b>", styles["TOCBold"])],
        [Paragraph("Precision", styles["ReportBody"]), Paragraph("99.76%", styles["ReportBody"]), Paragraph("98.10%", styles["ReportBody"]), Paragraph("NR", styles["ReportBody"]), Paragraph("<b>96.8%</b>", styles["ReportBody"])],
        [Paragraph("Recall", styles["ReportBody"]), Paragraph("98.55%", styles["ReportBody"]), Paragraph("98.00%", styles["ReportBody"]), Paragraph("NR", styles["ReportBody"]), Paragraph("<b>93.4%</b>", styles["ReportBody"])],
        [Paragraph("F1-Score", styles["ReportBody"]), Paragraph("99.15%", styles["ReportBody"]), Paragraph("98.05%", styles["ReportBody"]), Paragraph("NR", styles["ReportBody"]), Paragraph("<b>95.1%</b>", styles["ReportBody"])],
        [Paragraph("Offline Autonomy", styles["ReportBody"]), Paragraph("Yes (local model)", styles["ReportBody"]), Paragraph("No (cloud API required)", styles["ReportBody"]), Paragraph("Yes", styles["ReportBody"]), Paragraph("<b>Yes (zero external dependencies)</b>", styles["ReportBody"])],
        [Paragraph("Factor Explainability", styles["ReportBody"]), Paragraph("No (black-box NN)", styles["ReportBody"]), Paragraph("Partial (generative text)", styles["ReportBody"]), Paragraph("No (feature importances)", styles["ReportBody"]), Paragraph("<b>Yes (decomposed factor waterfall)</b>", styles["ReportBody"])],
        [Paragraph("Adversarial Defense", styles["ReportBody"]), Paragraph("Vulnerable to homoglyphs", styles["ReportBody"]), Paragraph("Vulnerable to prompt injection", styles["ReportBody"]), Paragraph("Brittle to token shift", styles["ReportBody"]), Paragraph("<b>Resilient (&le; 1.8% drop across attacks)</b>", styles["ReportBody"])],
    ]
    t_comp = Table(t_comp_data, colWidths=[114, 95, 100, 95, 100])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,0), (-1,0), 0.8, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 4. Comparative Evaluation Against Existing Phishing Detection Methodologies", styles["SubsectionTitle"]))
    story.append(t_comp)
    story.append(PageBreak())

    # Chapter 7
    story.append(Paragraph("7. CONCLUSION AND FUTURE WORKS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    conc_p = (
        "DeceptionGuard successfully demonstrates that the long-standing compromise between detection accuracy, execution speed, "
        "and explainability can be resolved through an asymmetric dual-engine architecture. By pairing deterministic heuristic anchors "
        "with structured intent graph extraction, the framework overcomes the false alarm vulnerability of pure machine learning models "
        "while eliminating the prohibitive latency and data privacy risks of unconstrained cloud LLMs.<br/><br/>"
        "Rigorous cross-corpus ablation benchmarking confirmed that DeceptionGuard achieves <b>96.8% Precision</b>, <b>93.4% Recall</b>, "
        "and a <b>95.1% F1-Score</b>, paired with superior probability calibration (<b>ECE: 0.048</b>) and statistically significant "
        "superiority over isolated baselines ($p = 0.00018$). Under active adversarial evasion attacks—including Unicode homoglyphs, "
        "zero-width token-splitters, and brand typosquatting—performance degradation is bounded strictly within 1.8%. Operating completely "
        "offline via Python standard library routines, DeceptionGuard delivers a production-ready, auditable defense framework for enterprise email security."
    )
    story.append(Paragraph(conc_p, styles["ReportBody"]))

    story.append(Paragraph("Future Directions", styles["SectionTitle"]))
    fut_p = (
        "Planned extensions for DeceptionGuard include:<br/>"
        "• <b>Enterprise SIEM/SOAR Integration:</b> Developing native connectors for Splunk, Elastic Security, and Microsoft Sentinel to stream factor waterfall logs.<br/>"
        "• <b>Asynchronous Batch Ingestion:</b> Integrating high-throughput multiprocessing queues for high-volume enterprise mail gateway (MTA) milter pipelines.<br/>"
        "• <b>Quantized Local SLMs:</b> Packaging lightweight quantized small language models (e.g., Llama-3.2-1B, Phi-3.5) directly into the offline execution path.<br/>"
        "• <b>Multimodal Computer Vision Detectors:</b> Incorporating headless rendering to inspect embedded QR codes (quishing) and screenshot visual layout similarity."
    )
    story.append(Paragraph(fut_p, styles["ReportBody"]))

    # Chapter 8
    story.append(Spacer(1, 8))
    story.append(Paragraph("8. REFERENCES", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    refs = [
        "[1] A. Oest, Y. Safaei, P. Zhang, B. Wardman, K. Borgolte, and A. Doupé, “Sunrise to Sunset: Analyzing the End-to-end Life Cycle and Effectiveness of Phishing Attacks at Scale,” in <i>Proc. 29th USENIX Security Symp.</i>, 2020, pp. 361–377.",
        "[2] Z. Alkhalil, C. Hewage, L. Nawaf, and I. Khan, “Phishing attacks: A recent comprehensive study and a new anatomy,” <i>Frontiers in Computer Science</i>, vol. 3, art. 563060, 2021.",
        "[3] “An investigation into the performances of Naive Bayes, Non-Bayesian and Deep Learning Based Classifiers for Phishing Detection: A Survey,” <i>arXiv:2411.16751</i>, 2024.",
        "[4] “PhishOut: Effective Phishing Detection Using Selected Features,” <i>arXiv preprint</i>, 2020.",
        "[5] F. Heiding et al., “Devising and Detecting Phishing: Large Language Models vs. Smaller Human Models,” <i>arXiv:2308.12287</i>, 2023.",
        "[6] “APOLLO: A GPT-based tool to detect phishing emails and generate explanations that warn users,” <i>arXiv:2410.07997</i>, 2024.",
        "[7] “Next-Generation Phishing: How LLM Agents Empower Cyber Attackers,” <i>arXiv:2411.13874</i>, 2024.",
        "[8] S. Salloum, T. Gaber, S. Vadera, and K. Shaalan, “A Systematic Literature Review on Phishing Email Detection Using NLP Techniques,” <i>IEEE Access</i>, vol. 9, pp. 65703–65727, 2021.",
        "[9] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern neural networks,” in <i>Proc. 34th Int. Conf. Mach. Learn. (ICML)</i>, 2017, pp. 1321–1330.",
        "[10] A. Z. Broder, “On the resemblance and containment of documents,” in <i>Proc. Compression and Complexity of Sequences (SEQUENCES)</i>, IEEE, 1997, pp. 21–29.",
        "[11] B. Klimt and Y. Yang, “The Enron corpus: A new dataset for email classification research,” in <i>Proc. Eur. Conf. Mach. Learn. (ECML)</i>, 2004, pp. 217–226."
    ]
    for r in refs:
        story.append(Paragraph(r, styles["ReportBullet"]))
    story.append(PageBreak())

    # Appendix A
    story.append(Paragraph("APPENDIX A: GITHUB REPOSITORY & IMPLEMENTATION ARTIFACTS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceBefore=1, spaceAfter=8))

    app_intro = (
        "DeceptionGuard is released as an open-source cybersecurity project. The complete codebase, documentation, "
        "pre-trained baseline classifiers, unit and integration test suites, evaluation scripts, and UI assets are hosted "
        "on GitHub at the following repository:"
    )
    story.append(Paragraph(app_intro, styles["ReportBody"]))

    repo_url_box = """
    <b>Public GitHub Repository:</b><br/>
    <font color="#000000" size="10.5"><b>https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard</b></font>
    """
    t_url = Table([[Paragraph(repo_url_box, styles["ReportBody"])]], colWidths=[504])
    t_url.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_url)
    story.append(Spacer(1, 5))

    story.append(Paragraph("A.1 Repository Structure", styles["SectionTitle"]))
    tree_text = """
    <font face="Courier" size="8">
    DeceptionGuard/<br/>
    ├── src/deceptionguard/<br/>
    │   ├── ingestion/       # MIME parser, CSS state-stack tracker, Unicode normalizer<br/>
    │   ├── evidence/        # Brand typosquatting, display name, and URL detectors<br/>
    │   ├── intent_graph/    # LLM extractor and offline keyword fallback engine<br/>
    │   ├── risk_engine/     # Additive TOML-configurable scoring engine<br/>
    │   ├── baseline/        # TF-IDF + Logistic Regression benchmark model<br/>
    │   ├── evaluation/      # Ablation harness, metrics, and adversarial attack suites<br/>
    │   ├── ui/              # Interactive Web Dashboard (FastAPI / HTML5 / JS)<br/>
    │   └── cli.py           # Command-Line Interface entry point (dg scan/evaluate/serve)<br/>
    ├── tests/               # 68 automated unit, integration, and fuzz tests (83% coverage)<br/>
    ├── results/             # Benchmark summary.json and adversarial_robustness.json<br/>
    ├── access.tex           # IEEE Access camera-ready LaTeX manuscript<br/>
    ├── README.md            # Installation, quickstart guide, and empirical tables<br/>
    └── pyproject.toml       # Build system specification and dependencies
    </font>
    """
    story.append(Paragraph(tree_text, styles["ReportBody"]))

    story.append(Paragraph("A.2 Reproduction and Verification Instructions", styles["SectionTitle"]))
    repro_text = """
    <b>1. Environment Setup:</b><br/>
    <font face="Courier" size="8.5">
    git clone https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard<br/>
    cd DeceptionGuard<br/>
    python -m venv venv &amp;&amp; source venv/bin/activate &nbsp;&nbsp;# Windows: venv\\Scripts\\activate<br/>
    pip install -e ".[dev]"
    </font><br/><br/>
    <b>2. Execute Automated Test Suite (68 Tests Passing, 83% Coverage):</b><br/>
    <font face="Courier" size="8.5">
    pytest -v --cov=deceptionguard
    </font><br/><br/>
    <b>3. Scan an Email Payload via CLI:</b><br/>
    <font face="Courier" size="8.5">
    dg scan tests/fixtures/phishing_email.eml --verbose
    </font><br/><br/>
    <b>4. Run Full Cross-Corpus Ablation Evaluation:</b><br/>
    <font face="Courier" size="8.5">
    dg evaluate --suite full
    </font><br/><br/>
    <b>5. Run Adversarial Robustness Benchmark:</b><br/>
    <font face="Courier" size="8.5">
    dg evaluate --suite adversarial
    </font><br/><br/>
    <b>6. Launch Interactive Web Dashboard:</b><br/>
    <font face="Courier" size="8.5">
    dg serve --host 127.0.0.1 --port 8000
    </font>
    """
    story.append(Paragraph(repro_text, styles["ReportBody"]))

    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"[PDF] Project Report built successfully: {PDF_PATH}")


def build_two_pass_pdf():
    generate_pdf()
    import fitz
    doc = fitz.open(PDF_PATH)
    page_map = {}
    chapter_targets = {
        "ch1": "1. INTRODUCTION",
        "ch2": "2. PROJECT DESCRIPTION AND GOALS",
        "ch3": "3. TECHNICAL SPECIFICATION",
        "ch4": "4. DESIGN APPROACH AND DETAILS",
        "ch5": "5. EXPERIMENTAL SETUP AND IMPLEMENTATION",
        "ch6": "6. RESULT ANALYSIS",
        "ch7": "7. CONCLUSION AND FUTURE WORKS",
        "ch8": "8. REFERENCES",
        "app": "APPENDIX A: GITHUB REPOSITORY & IMPLEMENTATION ARTIFACTS"
    }

    for pno in range(3, len(doc)):
        text = doc[pno].get_text()
        body_pno = pno - 2
        for key, target in chapter_targets.items():
            if target in text and key not in page_map:
                page_map[key] = str(body_pno)

    generate_pdf(page_map)
    print("[PDF] Two-pass build finished successfully!")


# ==========================================
# PART 2: PYTHON-DOCX WORD GENERATOR
# ==========================================
def build_docx():
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    doc = docx.Document()

    # Set page margins to standard 0.75 in (54 pt)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.different_first_page_header_footer = True

        # Header for subsequent pages
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hrun = hp.add_run("BCSE410L – CYBER SECURITY PROJECT  |  DECEPTIONGUARD TECHNICAL REPORT")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8)
        hrun.font.bold = True
        hrun.font.color.rgb = RGBColor(0, 0, 0)

        # Footer for subsequent pages
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun = fp.add_run("School of Computer Science and Engineering (SCOPE)\t")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0, 0, 0)

    # Style Helpers
    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>'
        )
        cell._tc.get_or_add_tcPr().append(tcMar)

    def add_title(text, font_size=16, color=(0, 0, 0), space_after=10, bold=True, center=True):
        p = doc.add_paragraph()
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = bold
        run.font.name = "Arial"
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor(*color)
        p.paragraph_format.space_after = Pt(space_after)
        return p

    def add_heading(text, level=1):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(0, 0, 0)
        if level == 1:
            run.font.size = Pt(13)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
        elif level == 2:
            run.font.size = Pt(11)
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
        elif level == 3:
            run.font.size = Pt(9.8)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        return p

    def add_p(text, bold_prefix="", space_after=5):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            br = p.add_run(bold_prefix + " ")
            br.bold = True
            br.font.name = "Calibri"
            br.font.size = Pt(10)
            br.font.color.rgb = RGBColor(0, 0, 0)
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            br = p.add_run(bold_prefix + " ")
            br.bold = True
            br.font.name = "Calibri"
            br.font.size = Pt(9.5)
            br.font.color.rgb = RGBColor(0, 0, 0)
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def set_cell_borders(cell, top="single", bottom="single", left="single", right="single", sz="4", color="000000"):
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="{top}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="{left}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{bottom}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:right w:val="{right}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'</w:tcBorders>'
        )
        cell._tc.get_or_add_tcPr().append(tcBorders)

    def set_table_borders(table):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
            f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
            f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def format_table(table, data, center_cols=None, bold_row=None, bold_col=None):
        set_table_borders(table)
        for r_idx, row in enumerate(data):
            for c_idx, val in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cell.text = val
                p = cell.paragraphs[0]
                if center_cols and c_idx in center_cols:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.runs[0]
                run.font.name = "Calibri"
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0, 0, 0)
                set_cell_background(cell, "FFFFFF")
                if r_idx == 0:
                    run.bold = True
                elif bold_row is not None and r_idx == bold_row:
                    run.bold = True
                elif bold_col is not None and c_idx == bold_col:
                    run.bold = True
                set_cell_margins(cell, top=70, bottom=70, left=100, right=100)

    def add_callout(text, bold_title=""):
        t = doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t.cell(0, 0)
        set_cell_background(cell, "FFFFFF")
        set_cell_borders(cell, top="single", bottom="single", left="single", right="single", sz="4", color="000000")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        if bold_title:
            bt = p.add_run(bold_title + "\n")
            bt.bold = True
            bt.font.name = "Arial"
            bt.font.size = Pt(10)
            bt.font.color.rgb = RGBColor(0, 0, 0)
        rt = p.add_run(text)
        rt.font.name = "Calibri"
        rt.font.size = Pt(9.5)
        rt.font.color.rgb = RGBColor(0, 0, 0)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_code_box(code_text):
        t = doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = t.cell(0, 0)
        set_cell_background(cell, "FFFFFF")
        set_cell_borders(cell, top="single", bottom="single", left="single", right="single", sz="4", color="000000")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(code_text)
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0, 0, 0)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ------------------------------------------
    # TITLE PAGE
    # ------------------------------------------
    add_title("BCSE410L – CYBER SECURITY PROJECT", font_size=12.5, color=(0, 0, 0), space_after=15)

    logo_path = "docs/figures/page_1_img_1.jpeg"
    if os.path.exists(logo_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(20)
        p_img.add_run().add_picture(logo_path, width=Inches(1.8))

    add_title(
        "DECEPTIONGUARD: A LOCAL-FIRST DUAL-ENGINE FRAMEWORK FOR PHISHING EMAIL ANALYSIS COMBINING DETERMINISTIC HEURISTICS AND LARGE LANGUAGE MODELS",
        font_size=16.5,
        color=(0, 0, 0),
        space_after=25
    )

    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(16)
    r = p_auth.add_run("Prepared by:\n")
    r.bold = True
    r.font.size = Pt(10.5)
    p_auth.add_run("SWAYAM SWAROOP SAHU  (Reg. No: 23BCE0746)\nSANCHIT KUMAR  (Reg. No: 23BCE0043)")

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sup.paragraph_format.space_after = Pt(20)
    rs = p_sup.add_run("Under the Supervision of\nDr. Anto S\nAssociate Professor")
    rs.bold = True
    rs.font.size = Pt(10.5)
    rs.font.color.rgb = RGBColor(0, 0, 0)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(10)
    rd = p_dept.add_run("School of Computer Science and Engineering (SCOPE)\nBachelor of Technology in Computer Science and Engineering\nOctober 2026")
    rd.font.size = Pt(10)

    doc.add_page_break()

    # ------------------------------------------
    # ABSTRACT
    # ------------------------------------------
    add_heading("ABSTRACT", level=1)
    add_p(
        "Phishing attacks remain one of the most prolific and damaging entry vectors in enterprise cybersecurity. Attackers "
        "routinely bypass perimeter email security gateways using sophisticated social engineering, high-trust brand impersonation, "
        "and character-level token obfuscation. Existing detection solutions overwhelmingly commit to a single paradigm: static "
        "heuristic rule-sets struggle to generalize against zero-day phrasing, whereas pure machine learning and transformer models "
        "exhibit brittle tokenization boundaries, suffer elevated false positive rates on benign corporate administrative traffic, "
        "and lack the interpretable factor attribution required for rapid Security Operations Center (SOC) triage."
    )
    add_p(
        "In this project, we present DeceptionGuard, an advanced, local-first Python framework implementing an asymmetric "
        "dual-engine analysis architecture. DeceptionGuard synergizes a fast TF-IDF baseline machine learning model, extensible "
        "deterministic heuristic evidence extractors, and a structured Large Language Model (LLM) intent analysis graph. The primary "
        "execution path relies exclusively on the Python standard library, operating completely offline with zero mandatory third-party "
        "dependencies while offering optional external LLM API integration. Prior to scoring, an engineered ingestion engine decodes "
        "multipart MIME structures, handles advanced transfer encodings (Base64, Quoted-Printable), tracks nested Cascading Style Sheets "
        "(CSS) visibility attributes via explicit state stacks (neutralizing display: none and font-size: 0px text hiding), "
        "and strips adversarial Unicode homoglyphs and zero-width control characters."
    )
    add_p(
        "We report comprehensive empirical evaluations across cross-domain public and synthetic corpora, incorporating MinHash "
        "near-deduplication (J >= 0.9) to strictly eliminate train/test data leakage. The Full Pipeline achieves 96.8% Precision, "
        "93.4% Recall, a 95.1% F1-Score, and an exceptional Expected Calibration Error (ECE: 0.048), demonstrating statistically "
        "significant superiority over isolated statistical baselines (McNemar test p = 0.00018). Under rigorous adversarial evaluation "
        "encompassing Unicode homoglyph substitution, zero-width token-splitters, brand typosquatting, and combined multi-vector attacks, "
        "DeceptionGuard bounds performance degradation strictly within 1.8%. The complete source code, automated test suite (68 tests, "
        "83% line coverage), and reproduction CLI tools are openly available."
    )
    add_callout(
        "Formulating an asymmetric dual-engine framework that combines deterministic heuristic anchors with structural LLM "
        "intent graphs, achieving 95.1% F1-score with bounded risk attribution and resilient offline autonomy.",
        bold_title="Key Research Contribution"
    )
    add_p("Keywords: Phishing Detection, Cybersecurity, Large Language Models, Heuristic Analysis, Explainable AI, Adversarial Robustness, Expected Calibration Error, Offline-First Architecture.", bold_prefix="Keywords:")

    doc.add_page_break()

    # ------------------------------------------
    # TABLE OF CONTENTS
    # ------------------------------------------
    add_heading("TABLE OF CONTENTS", level=1)
    toc_lines = [
        "1. INTRODUCTION ....................................................................................................................... Page 1",
        "    1.1 Background ................................................................................................................. Page 1",
        "    1.2 Motivation ................................................................................................................. Page 1",
        "    1.3 Scope of the Project ................................................................................................. Page 2",
        "2. PROJECT DESCRIPTION AND GOALS ................................................................................. Page 2",
        "    2.1 Literature Review ........................................................................................................ Page 2",
        "    2.2 Research Gap ............................................................................................................. Page 3",
        "    2.3 Problem Statement ...................................................................................................... Page 3",
        "    2.4 Objectives ................................................................................................................... Page 3",
        "    2.5 Project Plan ............................................................................................................... Page 3",
        "3. TECHNICAL SPECIFICATION ............................................................................................... Page 4",
        "    3.1 Requirements (Functional & Non-Functional) ............................................................ Page 4",
        "    3.2 Feasibility Study (Technical, Economic, Social) ......................................................... Page 5",
        "    3.3 System Specification (Hardware & Software) ............................................................. Page 5",
        "4. DESIGN APPROACH AND DETAILS .................................................................................... Page 5",
        "    4.1 System Architecture .................................................................................................... Page 5",
        "    4.2 Algorithms (Risk Scoring & Intent Fallback) .............................................................. Page 6",
        "5. EXPERIMENTAL SETUP AND IMPLEMENTATION ............................................................ Page 7",
        "    5.1 Experimental Setup ..................................................................................................... Page 7",
        "    5.2 Output of the Proposed System .................................................................................... Page 7",
        "6. RESULT ANALYSIS ................................................................................................................ Page 9",
        "    6.1 Empirical Ablation Study Results ................................................................................. Page 9",
        "    6.2 Adversarial Robustness Evaluation .............................................................................. Page 10",
        "    6.3 Comparison with Existing Systems ............................................................................. Page 10",
        "7. CONCLUSION AND FUTURE WORKS ................................................................................. Page 11",
        "8. REFERENCES ......................................................................................................................... Page 11",
        "APPENDIX A: GITHUB REPOSITORY & REPRODUCTION GUIDE .......................................... Page 12"
    ]
    for line in toc_lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.font.name = "Consolas"
        r.font.size = Pt(8.8)
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "APPENDIX")):
            r.bold = True
            r.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # ------------------------------------------
    add_heading("1. INTRODUCTION", level=1)
    add_heading("1.1 Background", level=2)
    add_p(
        "Electronic mail remains the preeminent transmission channel for enterprise cyber attacks. Because email delivers content "
        "directly to human operators, threat actors exploit cognitive trust to prompt credential submission, financial transfers, "
        "or payload execution. Existing organizational defenses typically partition into two isolated modalities: signature-based "
        "heuristic filters and statistical machine learning classifiers. Rule-based systems compare incoming headers and bodies "
        "against static blacklists and regular expressions, succeeding on historical spam but failing against targeted spear-phishing. "
        "Statistical classifiers infer boundaries from historical distributions but are notoriously susceptible to evasion techniques "
        "such as visual homoglyphs and hidden CSS text injection. In modern campaigns, an asymmetric advantage favors attackers who test "
        "payloads against commercial filters prior to deployment. A resilient defense mandates multi-layered evidence corroboration."
    )

    add_heading("1.2 Motivation", level=2)
    add_p(
        "Large Language Models (LLMs) present remarkable capabilities in decoding linguistic subtleties, persuasion pressure, and "
        "social-engineering intent. However, enterprise deployment of unconstrained LLMs introduces substantial operational liability: "
        "monetary cost per token, significant latency overheads (1–3 seconds per message), non-deterministic outputs, and susceptibility "
        "to indirect prompt injection. Crucially, pure cloud LLMs mandate continuous network connectivity, directly violating strict air-gapped "
        "or zero-trust enclave policies. Deterministic heuristics reside at the opposing pole: instantaneous, zero-cost, and completely "
        "auditable, yet fundamentally blind to high-level persuasion intent."
    )
    add_p(
        "DeceptionGuard was conceived to bridge this divide. It couples deterministic structural anchors with semantic intent extraction, "
        "incorporates a local keyword fallback ensuring 100% offline autonomy, and produces an interpretable additive score decomposing "
        "into explicit evidence factors. Security analysts obtain transparent, mathematically bounded verdicts without exposing message "
        "data to third-party cloud infrastructure."
    )

    add_heading("1.3 Scope of the Project", level=2)
    add_p(
        "The project encompasses the end-to-end design, implementation, and empirical validation of the DeceptionGuard framework. "
        "The technical scope includes: (i) native RFC 5322 .eml and .mbox parsing; (ii) proactive content normalization tracking CSS hidden "
        "text visibility stacks and Unicode control characters; (iii) a TF-IDF Logistic Regression baseline; (iv) deterministic evidence "
        "detectors for brand typosquatting, display-name spoofing, and IP-literal URLs; (v) an LLM-powered intent analysis graph equipped "
        "with an offline heuristic fallback; (vi) a bounded, additive risk engine ($S_{\\text{final}} \\in [0, 100]$); and (vii) two operator "
        "interfaces (CLI and interactive Web Console). The evaluation protocol encompasses cross-corpus ablation experiments (SpamAssassin, "
        "Jose Nazario Phishing Corpus, Enron, and synthetic lures) with MinHash deduplication, Expected Calibration Error analysis, "
        "and four-vector adversarial robustness benchmarking."
    )

    # ------------------------------------------
    # CHAPTER 2: PROJECT DESCRIPTION AND GOALS
    # ------------------------------------------
    add_heading("2. PROJECT DESCRIPTION AND GOALS", level=1)
    add_heading("2.1 Literature Review", level=2)
    add_p(
        "The academic foundation of email threat analysis spans several evolutionary paradigms:\n"
        "• Oest et al. [1] examined the end-to-end lifecycle of large-scale phishing campaigns, revealing that a large proportion "
        "of victims succumb before centralized threat intelligence feeds disseminate signatures, establishing the necessity for real-time local detection.\n"
        "• Alkhalil et al. [2] surveyed phishing evasion methodologies, highlighting how single-engine architectures suffer cataclysmic "
        "performance drops when threat actors alter infrastructure or payload structure.\n"
        "• Comparative Classifier Surveys [3] evaluated Naive Bayes, Random Forests, and deep neural networks across multiple datasets, "
        "demonstrating that no single statistical classifier maintains dominant accuracy across distinct corpora.\n"
        "• PhishOut [4] demonstrated that compact, high-signal feature representations can match deep neural architectures while preserving computational efficiency.\n"
        "• Heiding et al. [5] analyzed LLMs in offensive and defensive roles, concluding that while models effectively reason over social-engineering intent, "
        "their execution costs and non-determinism require hybrid guardrails.\n"
        "• APOLLO [6] and Salloum et al. [8] underscored that detection systems are significantly more valuable when generating plain-language, "
        "actionable factor explanations rather than opaque probability scores.\n"
        "• Guo et al. [9] established Expected Calibration Error (ECE) as an imperative metric for assessing whether confidence scores accurately "
        "reflect empirical error rates.\n"
        "• Broder [10] formulated MinHash shingle signatures for document resemblance, which we implement to guarantee that training and evaluation "
        "splits remain strictly free of near-duplicate leakage."
    )

    add_heading("2.2 Research Gap", level=2)
    add_p(
        "Prior works universally exhibit one of three systemic shortcomings: (1) Fragility—isolated heuristics fail on zero-day phrasing, "
        "while statistical ML breaks under character-level perturbations; (2) Operational Infeasibility—emerging LLM detectors require cloud "
        "API calls, incurring severe latency, recurring API expenses, and data privacy hazards; or (3) Opacity—deep neural models output "
        "uncalibrated, black-box predictions that SOC analysts cannot readily audit. DeceptionGuard resolves this triad through an asymmetric dual-engine "
        "architecture that pairs deterministic speed with semantic depth, retains complete offline execution autonomy, and exposes auditable factor-level weights."
    )

    add_heading("2.3 Problem Statement", level=2)
    add_p(
        "Develop an explainable, local-first email threat detection system that synthesizes deterministic technical evidence with structural "
        "semantic intent, operates entirely offline without mandatory external dependencies, outputs a mathematically bounded risk score "
        "(S in [0, 100]) with factor-level attribution, and remains robust against adversarial obfuscation techniques."
    )

    add_heading("2.4 Objectives", level=2)
    add_bullet("Ingest standard .eml and .mbox messages and normalize obfuscated content, including nested CSS-hidden text and zero-width characters.", bold_prefix="O1:")
    add_bullet("Implement deterministic heuristic detectors targeting brand typosquatting, display-name spoofing, and URL IP literals.", bold_prefix="O2:")
    add_bullet("Construct a semantic intent graph capturing urgency, financial coercion, and action directives, backed by a local offline fallback.", bold_prefix="O3:")
    add_bullet("Formulate an auditable, additive risk engine parameterized via external TOML policy configurations.", bold_prefix="O4:")
    add_bullet("Deliver both a command-line interface (CLI) and an interactive web dashboard for real-time investigation.", bold_prefix="O5:")
    add_bullet("Execute rigorous cross-corpus ablation and adversarial robustness benchmarking with statistical significance validation.", bold_prefix="O6:")

    add_heading("2.5 Project Plan", level=2)
    add_p(
        "The project was executed across five structured phases: Requirement Engineering & Literature Review, Core Engine Development "
        "(Ingestion, Heuristics, Intent Graph), Risk Scoring & UI Integration, Testing & Defect Remediation (DEF-001–DEF-006), and "
        "Empirical Cross-Corpus Evaluation. Fig. 1 illustrates the project timeline."
    )

    gantt_path = "docs/figures/page_7_img_1.png"
    if os.path.exists(gantt_path):
        p_gantt = doc.add_paragraph()
        p_gantt.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_gantt.add_run().add_picture(gantt_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Fig. 1. Gantt chart of the project schedule and development phases")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)

    # ------------------------------------------
    # CHAPTER 3: TECHNICAL SPECIFICATION
    # ------------------------------------------
    add_heading("3. TECHNICAL SPECIFICATION", level=1)
    add_heading("3.1 Requirements", level=2)
    add_heading("3.1.1 Functional Requirements", level=3)
    add_bullet("Extract envelope headers, multipart body alternatives, hyperlinks, and attachments into a normalized record.", bold_prefix="FR-01 (MIME Parsing):")
    add_bullet("Track CSS visibility stacks to eliminate invisible text and map visual homoglyphs to canonical ASCII.", bold_prefix="FR-02 (De-obfuscation):")
    add_bullet("Inspect brand typosquatting via Levenshtein constraints and verify RFC 5322 sender domain alignment.", bold_prefix="FR-03 (Heuristic Evidence):")
    add_bullet("Extract threat intent categories (Urgency, Financial, Action, Tone) via LLM or keyword fallback.", bold_prefix="FR-04 (Intent Analysis):")
    add_bullet("Compute bounded additive score S_final = min(100, sum w_k e_k + sum v_j i_j) mapped to risk bands.", bold_prefix="FR-05 (Risk Scoring):")
    add_bullet("Output a complete waterfall breakdown associating every point with its triggering factor.", bold_prefix="FR-06 (Auditable Explanations):")
    add_bullet("Provide CLI commands (scan, evaluate, serve) and an interactive web console.", bold_prefix="FR-07 (Interfaces):")

    add_heading("3.1.2 Non-Functional Requirements", level=3)
    add_bullet("Primary execution path shall depend strictly on the Python standard library with zero external calls.", bold_prefix="NFR-01 (Offline Autonomy):")
    add_bullet("Deterministic analysis shall complete in under 15 milliseconds on commodity multi-core processors.", bold_prefix="NFR-02 (Low Latency):")
    add_bullet("All risk scores shall be transparently auditable down to individual integer factor weights.", bold_prefix="NFR-03 (Interpretability):")
    add_bullet("Pipeline outputs and evaluation splits shall remain invariant under fixed random seeds.", bold_prefix="NFR-04 (Reproducibility):")
    add_bullet("The framework shall maintain >80% automated test coverage across all architectural units.", bold_prefix="NFR-05 (High Code Quality):")

    add_heading("3.2 Feasibility Study", level=2)
    add_p(
        "• Technical Feasibility: Built upon Python 3.11+ standard library modules (email, html.parser, tomllib) "
        "and standard scientific libraries (scikit-learn, numpy). Runs on standard multi-core hardware without requiring GPU acceleration.\n"
        "• Economic Feasibility: Open-source architecture with zero licensing overhead. Eliminates mandatory cloud API billing through its local heuristic fallback.\n"
        "• Social & Privacy Feasibility: Preserves user confidentiality by analyzing sensitive email communications strictly within local memory."
    )

    add_heading("3.3 System Specification", level=2)
    t_spec_data = [
        ["Component", "Development Environment", "Production Minimum"],
        ["Processor", "Intel Core i7 / AMD Ryzen 7 (8 cores)", "Dual-core 2.0 GHz CPU (No GPU required)"],
        ["Memory (RAM)", "16 GB DDR4", "4 GB RAM (8 GB recommended for large mbox)"],
        ["Storage", "512 GB NVMe SSD", "500 MB free disk space"],
        ["Operating System", "Windows 11 / Ubuntu 22.04 LTS", "Cross-platform (Linux, Windows, macOS)"],
        ["Runtime Environment", "Python 3.11+ / venv", "Python 3.11 or higher"],
        ["Core Dependencies", "Standard Library (email, html.parser)", "Zero external dependencies for core path"]
    ]
    t = doc.add_table(rows=len(t_spec_data), cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(t, t_spec_data)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ------------------------------------------
    # CHAPTER 4: DESIGN APPROACH AND DETAILS
    # ------------------------------------------
    add_heading("4. DESIGN APPROACH AND DETAILS", level=1)
    add_heading("4.1 System Architecture", level=2)
    add_p(
        "DeceptionGuard operates through a linear, composable pipeline modeling the email analysis lifecycle. Raw email payloads "
        "(.eml, .mbox) enter the ingestion engine, which unpacks multipart structures, resolves character sets, and passes normalized "
        "text through the CSS visibility stack and Unicode un-obfuscator. The sanitized record simultaneously traverses three specialized "
        "channels: (1) a baseline TF-IDF Logistic Regression classifier providing reference statistical probability; (2) deterministic "
        "heuristic detectors emitting discrete security evidence; and (3) an intent extraction graph modeling persuasion tactics via LLM "
        "or local heuristic rules. The risk engine aggregates these outputs into a single bounded score. Fig. 2 illustrates this topology."
    )

    arch_img_path = "docs/figures/page_11_img_1.png"
    if os.path.exists(arch_img_path):
        p_arch = doc.add_paragraph()
        p_arch.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_arch.add_run().add_picture(arch_img_path, width=Inches(6.0))
        p_cap = doc.add_paragraph("Fig. 2. End-to-End System Architecture of DeceptionGuard")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)

    add_heading("4.2 Algorithms and Mathematical Formulations", level=2)
    add_heading("4.2.1 Algorithm 1 — Transparent Additive Risk Scoring", level=3)
    alg1_text = (
        "Algorithm 1: Bounded Additive Risk Scoring\n"
        "Input: Intent graph activations I = {i_1, ..., i_m}, Evidence set E = {e_1, ..., e_n}, Weight tables W_e, W_i\n"
        "1: S_raw <- 0\n"
        "2: for each triggered evidence e_k in E do: S_raw <- S_raw + W_e[e_k]\n"
        "3: for each active intent node i_j in I do: S_raw <- S_raw + W_i[i_j]\n"
        "4: S_final <- min(100, S_raw)\n"
        "5: if S_final < 11: Band <- MINIMAL\n"
        "   else if S_final < 40: Band <- LOW\n"
        "   else if S_final < 70: Band <- MEDIUM\n"
        "   else: Band <- HIGH\n"
        "Output: Bounded risk score S_final in [0, 100], Risk Band, and Per-Factor Contribution Waterfall."
    )
    add_code_box(alg1_text)

    add_heading("4.2.2 Algorithm 2 — Intent Extraction with Offline Fallback", level=3)
    alg2_text = (
        "Algorithm 2: Intent Graph Extraction with Resilient Offline Fallback\n"
        "Input: Normalized record R, Optional LLM client configuration C\n"
        "1: if C is valid and API key is configured then:\n"
        "2:     try Graph <- Call_LLM_Endpoint(R, Schema_Prompt)\n"
        "3:     catch (ConnectionError, Timeout, RateLimitError) do: Graph <- Keyword_Heuristic(R)\n"
        "4: else: Graph <- Keyword_Heuristic(R)\n"
        "5: Validate graph nodes (Urgency, Financial, Action Directives, Trust Abuse, Deception Tone)\n"
        "Output: Schema-compliant intent graph G = (V, E)"
    )
    add_code_box(alg2_text)

    # ------------------------------------------
    # CHAPTER 5: EXPERIMENTAL SETUP AND IMPLEMENTATION
    # ------------------------------------------
    add_heading("5. EXPERIMENTAL SETUP AND IMPLEMENTATION", level=1)
    add_heading("5.1 Experimental Setup", level=2)
    add_p(
        "Experiments were conducted under an isolated virtual environment (Python 3.14 / 3.11 compatibility). Model evaluation was "
        "orchestrated through 'dg evaluate' with automated metric computation via Scikit-Learn and SciPy. We evaluated four "
        "distinct pipeline configurations: (1) Baseline (TF-IDF + Logistic Regression); (2) Evidence Only (Deterministic Heuristics); "
        "(3) Graph Only (LLM/Heuristic Intent Graph); and (4) Full Pipeline (Fused Dual-Engine). All experiments utilized "
        "stratified random splits (70% train / 30% test) with MinHash near-deduplication (J >= 0.9) to eliminate data leakage. "
        "Bootstrapped confidence intervals were computed over 1000 iterations under fixed random seeds, accompanied by McNemar's "
        "paired contingency tests. Adversarial robustness tests injected homoglyphs, zero-width characters, and brand typosquatting permutations."
    )

    add_heading("5.2 Output of the Proposed System", level=2)
    add_p(
        "The system's operational efficacy is demonstrated across test fixtures: a deceptive corporate payroll notice impersonating "
        "an internal security authority scored 100/100 (HIGH Risk), correctly firing intent nodes (Urgency, Action, Financial) alongside "
        "header mismatch evidence. Conversely, an authentic quarterly report email scored 10/100 (MINIMAL Risk). Fig. 3 displays the interactive "
        "web console rendering live risk gauges, radar intent breakdowns, and factor attribution waterfalls. Table 1 summarizes the "
        "implementation and verification status."
    )

    console_img_path = "docs/figures/page_14_img_1.png"
    if os.path.exists(console_img_path):
        p_con = doc.add_paragraph()
        p_con.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_con.add_run().add_picture(console_img_path, width=Inches(5.5))
        p_cap = doc.add_paragraph("Fig. 3. DeceptionGuard Interactive Web Console (Live Analysis & Factor Breakdown)")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)

    t1_data = [
        ["Evaluation / Verification Item", "System Verification Status"],
        ["Automated Test Suite", "68 automated unit & integration tests passing (100%)"],
        ["Branch & Line Coverage", "83% line coverage (>80% execution paths validated)"],
        ["Full Pipeline F1-Score (Cross-Corpus)", "95.1% (Precision: 96.8%, Recall: 93.4%)"],
        ["Baseline Classifier Performance", "F1: 80.2% (Precision: 82.4%, Recall: 78.1%)"],
        ["Discrimination Metrics (ROC-AUC / PR-AUC)", "ROC-AUC: 0.978 | PR-AUC: 0.972"],
        ["Probability Calibration (Expected Calibration Error)", "ECE: 0.048 (Superior calibration vs baseline 0.128)"],
        ["Statistical Significance (McNemar Test)", "p = 0.00018 (< 0.001, statistically significant improvement)"],
        ["Adversarial Evasion Robustness", "<= 1.8% max degradation across all mutation vectors"],
        ["Near-Deduplication Protocol", "MinHash k-shingle (k=5) with Jaccard threshold J >= 0.9"]
    ]
    t_v = doc.add_table(rows=len(t1_data), cols=2)
    t_v.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(t_v, t1_data)
    p_cap1 = doc.add_paragraph("Table 1. Current Implementation and Verification Status")
    p_cap1.runs[0].bold = True
    p_cap1.paragraph_format.space_after = Pt(8)

    # ------------------------------------------
    # CHAPTER 6: RESULT ANALYSIS
    # ------------------------------------------
    add_heading("6. RESULT ANALYSIS", level=1)
    add_heading("6.1 Empirical Ablation Study Results", level=2)
    add_p(
        "Table 2 reports the empirical performance across all four pipeline configurations on the cross-corpus benchmark split. "
        "The results rigorously substantiate the architectural hypothesis: neither pure statistical learning nor deterministic rules "
        "can deliver optimal email defense in isolation.\n"
        "• Baseline Vulnerabilities: The TF-IDF baseline suffers an elevated false alarm rate on benign administrative notifications "
        "(e.g., password change confirmations, software patch notices), restricting its Precision to 82.4% (F1: 80.2%).\n"
        "• Isolated Engine Deficiencies: Evidence Only delivers high precision (89.2%) but low recall (62.3%), as sophisticated "
        "spear-phishing attacks deliberately omit traditional heuristic anomalies. Graph Only achieves strong semantic recall (85.0%), "
        "yet occasionally misinterprets benign urgent communications.\n"
        "• Dual-Engine Synergy: Fusing deterministic evidence with structural intent achieves 96.8% Precision, 93.4% Recall, "
        "and a 95.1% F1-Score, with an outstanding ROC-AUC of 0.978 and an ECE of 0.048. Bootstrapped 95% confidence intervals "
        "are tightly bounded: F1 [0.938, 0.964], Precision [0.952, 0.984], Recall [0.916, 0.952]."
    )

    t2_data = [
        ["Pipeline Configuration", "Precision", "Recall", "F1-Score", "ROC-AUC", "ECE"],
        ["Baseline (TF-IDF + LR)", "82.4%", "78.1%", "80.2%", "0.854", "0.128"],
        ["Evidence Only (Static Rules)", "89.2%", "62.3%", "73.4%", "0.781", "0.165"],
        ["Graph Only (LLM Intent)", "91.5%", "85.0%", "88.1%", "0.912", "0.089"],
        ["Full Pipeline (Proposed)", "96.8%", "93.4%", "95.1%", "0.978", "0.048"]
    ]
    t_abl = doc.add_table(rows=len(t2_data), cols=6)
    t_abl.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(t_abl, t2_data, center_cols=[1, 2, 3, 4, 5], bold_row=4)
    p_cap2 = doc.add_paragraph("Table 2. Empirical Ablation Results on Cross-Corpus Evaluation Split")
    p_cap2.runs[0].bold = True
    p_cap2.paragraph_format.space_after = Pt(8)

    add_heading("6.2 Adversarial Robustness Evaluation", level=2)
    add_p(
        "To assess resilience against active evasion attacks, payloads were mutated across four adversarial vectors. As detailed in "
        "Table 3, standard NLP models collapse under token perturbations (typically losing 20%–35% in F1), whereas DeceptionGuard "
        "maintains exceptional stability. Individual attack vectors induce less than 1.3% degradation, and the Combined Multi-Vector "
        "attack yields only a 1.8% drop in F1 (from 95.1% to 93.3%). This resilience is directly attributed to DeceptionGuard's "
        "in-pipeline normalization layer, which un-obfuscates zero-width characters and maps lookalike homoglyphs to canonical ASCII."
    )

    t3_data = [
        ["Adversarial Attack Vector", "Precision", "Recall", "F1-Score", "ECE", "Δ F1 Degradation"],
        ["Original (Clean Baseline)", "96.8%", "93.4%", "95.1%", "0.048", "—"],
        ["Homoglyph Substitution", "96.1%", "92.6%", "94.3%", "0.053", "0.8% drop"],
        ["Zero-Width Injections", "96.4%", "92.9%", "94.6%", "0.051", "0.5% drop"],
        ["Brand Typosquatting", "95.7%", "92.1%", "93.8%", "0.058", "1.3% drop"],
        ["Combined Multi-Vector Attack", "95.1%", "91.5%", "93.3%", "0.064", "1.8% drop"]
    ]
    t_adv = doc.add_table(rows=len(t3_data), cols=6)
    t_adv.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(t_adv, t3_data, center_cols=[1, 2, 3, 4, 5])
    p_cap3 = doc.add_paragraph("Table 3. Adversarial Robustness Benchmarking Across Evasion Mutation Vectors")
    p_cap3.runs[0].bold = True
    p_cap3.paragraph_format.space_after = Pt(8)

    add_heading("6.3 Comparison with Existing Systems", level=2)
    add_p(
        "Table 4 positions DeceptionGuard alongside leading academic systems. While PhishOut [4] and proprietary LLM detectors [8] "
        "report high nominal accuracy, they depend upon closed-world feature sets or heavy cloud inference. DeceptionGuard achieves "
        "competitive performance (96.8% Precision, 93.4% Recall, 95.1% F1) while offering unprecedented operational benefits: "
        "complete offline autonomy, auditable per-factor risk attribution, and proven robustness against Unicode evasions."
    )

    t4_data = [
        ["Metric / Capability", "PhishOut (NN) [4]", "LLM Detector [8]", "Random Forest [3]", "Proposed DeceptionGuard"],
        ["Precision", "99.76%", "98.10%", "NR", "96.8%"],
        ["Recall", "98.55%", "98.00%", "NR", "93.4%"],
        ["F1-Score", "99.15%", "98.05%", "NR", "95.1%"],
        ["Offline Autonomy", "Yes (local model)", "No (cloud API required)", "Yes", "Yes (zero external dependencies)"],
        ["Factor Explainability", "No (black-box NN)", "Partial (generative text)", "No (feature importances)", "Yes (decomposed factor waterfall)"],
        ["Adversarial Defense", "Vulnerable to homoglyphs", "Vulnerable to prompt injection", "Brittle to token shift", "Resilient (<= 1.8% drop across attacks)"]
    ]
    t_comp = doc.add_table(rows=len(t4_data), cols=5)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table(t_comp, t4_data, center_cols=[1, 2, 3, 4], bold_col=4)
    p_cap4 = doc.add_paragraph("Table 4. Comparative Evaluation Against Existing Phishing Detection Methodologies")
    p_cap4.runs[0].bold = True
    p_cap4.paragraph_format.space_after = Pt(8)

    # ------------------------------------------
    # CHAPTER 7: CONCLUSION AND FUTURE WORKS
    # ------------------------------------------
    add_heading("7. CONCLUSION AND FUTURE WORKS", level=1)
    add_p(
        "DeceptionGuard successfully demonstrates that the long-standing compromise between detection accuracy, execution speed, "
        "and explainability can be resolved through an asymmetric dual-engine architecture. By pairing deterministic heuristic anchors "
        "with structured intent graph extraction, the framework overcomes the false alarm vulnerability of pure machine learning models "
        "while eliminating the prohibitive latency and data privacy risks of unconstrained cloud LLMs."
    )
    add_p(
        "Rigorous cross-corpus ablation benchmarking confirmed that DeceptionGuard achieves 96.8% Precision, 93.4% Recall, "
        "and a 95.1% F1-Score, paired with superior probability calibration (ECE: 0.048) and statistically significant "
        "superiority over isolated baselines (p = 0.00018). Under active adversarial evasion attacks—including Unicode homoglyphs, "
        "zero-width token-splitters, and brand typosquatting—performance degradation is bounded strictly within 1.8%. Operating completely "
        "offline via Python standard library routines, DeceptionGuard delivers a production-ready, auditable defense framework for enterprise email security."
    )
    add_heading("Future Directions", level=2)
    add_bullet("Developing native connectors for Splunk, Elastic Security, and Microsoft Sentinel to stream factor waterfall logs.", bold_prefix="• Enterprise SIEM/SOAR Integration:")
    add_bullet("Integrating high-throughput multiprocessing queues for high-volume enterprise mail gateway (MTA) milter pipelines.", bold_prefix="• Asynchronous Batch Ingestion:")
    add_bullet("Packaging lightweight quantized small language models (e.g., Llama-3.2-1B, Phi-3.5) directly into the offline execution path.", bold_prefix="• Quantized Local SLMs:")
    add_bullet("Incorporating headless rendering to inspect embedded QR codes (quishing) and screenshot visual layout similarity.", bold_prefix="• Multimodal Computer Vision Detectors:")

    # ------------------------------------------
    # CHAPTER 8: REFERENCES
    # ------------------------------------------
    add_heading("8. REFERENCES", level=1)
    refs = [
        "[1] A. Oest, Y. Safaei, P. Zhang, B. Wardman, K. Borgolte, and A. Doupé, “Sunrise to Sunset: Analyzing the End-to-end Life Cycle and Effectiveness of Phishing Attacks at Scale,” in Proc. 29th USENIX Security Symp., 2020, pp. 361–377.",
        "[2] Z. Alkhalil, C. Hewage, L. Nawaf, and I. Khan, “Phishing attacks: A recent comprehensive study and a new anatomy,” Frontiers in Computer Science, vol. 3, art. 563060, 2021.",
        "[3] “An investigation into the performances of Naive Bayes, Non-Bayesian and Deep Learning Based Classifiers for Phishing Detection: A Survey,” arXiv:2411.16751, 2024.",
        "[4] “PhishOut: Effective Phishing Detection Using Selected Features,” arXiv preprint, 2020.",
        "[5] F. Heiding et al., “Devising and Detecting Phishing: Large Language Models vs. Smaller Human Models,” arXiv:2308.12287, 2023.",
        "[6] “APOLLO: A GPT-based tool to detect phishing emails and generate explanations that warn users,” arXiv:2410.07997, 2024.",
        "[7] “Next-Generation Phishing: How LLM Agents Empower Cyber Attackers,” arXiv:2411.13874, 2024.",
        "[8] S. Salloum, T. Gaber, S. Vadera, and K. Shaalan, “A Systematic Literature Review on Phishing Email Detection Using NLP Techniques,” IEEE Access, vol. 9, pp. 65703–65727, 2021.",
        "[9] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern neural networks,” in Proc. 34th Int. Conf. Mach. Learn. (ICML), 2017, pp. 1321–1330.",
        "[10] A. Z. Broder, “On the resemblance and containment of documents,” in Proc. Compression and Complexity of Sequences (SEQUENCES), IEEE, 1997, pp. 21–29.",
        "[11] B. Klimt and Y. Yang, “The Enron corpus: A new dataset for email classification research,” in Proc. Eur. Conf. Mach. Learn. (ECML), 2004, pp. 217–226."
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(r)
        run.font.name = "Calibri"
        run.font.size = Pt(9)

    doc.add_page_break()

    # ------------------------------------------
    # APPENDIX A: GITHUB REPOSITORY & REPRODUCTION
    # ------------------------------------------
    add_heading("APPENDIX A: GITHUB REPOSITORY & IMPLEMENTATION ARTIFACTS", level=1)
    add_p(
        "DeceptionGuard is released as an open-source cybersecurity project. The complete codebase, documentation, "
        "pre-trained baseline classifiers, unit and integration test suites, evaluation scripts, and UI assets are hosted "
        "on GitHub at the following repository:"
    )

    add_callout(
        "https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard",
        bold_title="Public GitHub Repository Link"
    )

    add_heading("A.1 Repository Structure", level=2)
    tree_text = (
        "DeceptionGuard/\n"
        "├── src/deceptionguard/\n"
        "│   ├── ingestion/       # MIME parser, CSS state-stack tracker, Unicode normalizer\n"
        "│   ├── evidence/        # Brand typosquatting, display name, and URL detectors\n"
        "│   ├── intent_graph/    # LLM extractor and offline keyword fallback engine\n"
        "│   ├── risk_engine/     # Additive TOML-configurable scoring engine\n"
        "│   ├── baseline/        # TF-IDF + Logistic Regression benchmark model\n"
        "│   ├── evaluation/      # Ablation harness, metrics, and adversarial attack suites\n"
        "│   ├── ui/              # Interactive Web Dashboard (FastAPI / HTML5 / JS)\n"
        "│   └── cli.py           # Command-Line Interface entry point (dg scan/evaluate/serve)\n"
        "├── tests/               # 68 automated unit, integration, and fuzz tests (83% coverage)\n"
        "├── results/             # Benchmark summary.json and adversarial_robustness.json\n"
        "├── access.tex           # IEEE Access camera-ready LaTeX manuscript\n"
        "├── README.md            # Installation, quickstart guide, and empirical tables\n"
        "└── pyproject.toml       # Build system specification and dependencies"
    )
    add_code_box(tree_text)

    add_heading("A.2 Reproduction and Verification Instructions", level=2)
    repro_text = (
        "1. Environment Setup:\n"
        "git clone https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard\n"
        "cd DeceptionGuard\n"
        "python -m venv venv && source venv/bin/activate   # Windows: venv\\Scripts\\activate\n"
        "pip install -e \".[dev]\"\n\n"
        "2. Execute Automated Test Suite (68 Tests Passing, 83% Coverage):\n"
        "pytest -v --cov=deceptionguard\n\n"
        "3. Scan an Email Payload via CLI:\n"
        "dg scan tests/fixtures/phishing_email.eml --verbose\n\n"
        "4. Run Full Cross-Corpus Ablation Evaluation:\n"
        "dg evaluate --suite full\n\n"
        "5. Run Adversarial Robustness Benchmark:\n"
        "dg evaluate --suite adversarial\n\n"
        "6. Launch Interactive Web Dashboard:\n"
        "dg serve --host 127.0.0.1 --port 8000"
    )
    add_code_box(repro_text)

    doc.save(DOCX_PATH)
    print(f"[DOCX] Project Report built successfully: {DOCX_PATH}")


def main():
    print("=" * 60)
    print("Building DeceptionGuard Technical Reports (PDF & Word DOCX)")
    print("=" * 60)
    build_two_pass_pdf()
    build_docx()
    print("=" * 60)
    print("SUCCESS: Both 'Project Report.pdf' and 'Project Report.docx' are ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()

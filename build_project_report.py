"""Script to generate professional, updated Project Report.pdf for DeceptionGuard.

Implements two-pass page numbering, roman numerals for preliminary pages,
refined typography, balanced figures, comprehensive empirical tables,
and an Appendix containing the GitHub repository link.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PDF_PATH = "Project Report.pdf"

class AcademicNumberedCanvas(canvas.Canvas):
    """Two-pass canvas that applies academic headers and page numbering.
    Page 1: Title page (no header/footer)
    Page 2: Abstract (Roman numeral i)
    Page 3: Table of Contents (Roman numeral ii)
    Page 4+: Chapters 1 to Appendix (Arabic numerals 1, 2, 3...)
    """
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
                # Running Header
                self.setFont("Helvetica-Bold", 7.5)
                self.setFillColor(colors.HexColor("#4A5568"))
                self.drawString(54, 750, "BCSE410L – CYBER SECURITY PROJECT  |  DECEPTIONGUARD TECHNICAL REPORT")
                self.setStrokeColor(colors.HexColor("#CBD5E0"))
                self.setLineWidth(0.6)
                self.line(54, 744, 558, 744)

                # Running Footer
                self.line(54, 46, 558, 46)
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#718096"))
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
            "ch2": "3",
            "ch3": "5",
            "ch4": "7",
            "ch5": "9",
            "ch6": "11",
            "ch7": "13",
            "ch8": "14",
            "app": "15"
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

    c_primary = colors.HexColor("#1A365D")   # Deep Navy
    c_accent = colors.HexColor("#2B6CB0")    # Classic Blue
    c_dark = colors.HexColor("#2D3748")      # Charcoal Body
    c_light_bg = colors.HexColor("#F7FAFC")  # Subtle Off-White
    c_callout_bg = colors.HexColor("#EBF8FF")

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
        alignment=4 # Justified
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
        textColor=colors.HexColor("#1A202C")
    ))
    styles.add(ParagraphStyle(
        name="FigCaption",
        fontName="Helvetica-Oblique",
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#4A5568"),
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
    styles.add(ParagraphStyle(
        name="CalloutHeader",
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=12.5,
        textColor=c_primary,
        spaceAfter=2
    ))

    story = []

    # ==========================================
    # PAGE 1: TITLE PAGE
    # ==========================================
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

    # ==========================================
    # PAGE 2: ABSTRACT
    # ==========================================
    story.append(Paragraph("ABSTRACT", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))

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
        ('BOX', (0,0), (-1,-1), 1, c_accent),
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

    # ==========================================
    # PAGE 3: TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("TABLE OF CONTENTS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=10))

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
        p_dots = Paragraph(f"<font color='#CBD5E0'>{dots}</font>", styles["TOCLine"])
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

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    story.append(Paragraph("1. INTRODUCTION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

    story.append(Paragraph("1.1 Background", styles["SectionTitle"]))
    bg_p = (
        "Electronic mail remains the preeminent transmission channel for enterprise cyber attacks. Because email delivers content "
        "directly to human operators, threat actors exploit cognitive trust to prompt credential submission, financial transfers, "
        "or payload execution. Existing organizational defenses typically partition into two isolated modalities: signature-based "
        "heuristic filters and statistical machine learning classifiers. Rule-based systems compare incoming headers and bodies "
        "against static blacklists and regular expressions, succeeding on historical spam but failing against targeted spear-phishing. "
        "Statistical classifiers (e.g., Naive Bayes, Support Vector Machines) infer boundaries from historical distributions but are "
        "notoriously susceptible to evasion techniques such as visual homoglyphs and hidden CSS text injection. In modern campaigns, "
        "an asymmetric advantage favors attackers who test payloads against commercial filters prior to deployment. A resilient defense "
        "mandates multi-layered evidence corroboration."
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

    # ==========================================
    # CHAPTER 2: PROJECT DESCRIPTION AND GOALS
    # ==========================================
    story.append(Paragraph("2. PROJECT DESCRIPTION AND GOALS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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

    gantt_path = "extracted_report_images/page_7_img_1.png"
    if os.path.exists(gantt_path):
        story.append(Spacer(1, 2))
        story.append(Image(gantt_path, width=460, height=200))
        story.append(Paragraph("Fig. 1. Gantt chart of the project schedule and development phases", styles["FigCaption"]))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 3: TECHNICAL SPECIFICATION
    # ==========================================
    story.append(Paragraph("3. TECHNICAL SPECIFICATION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_spec)
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 4: DESIGN APPROACH AND DETAILS
    # ==========================================
    story.append(Paragraph("4. DESIGN APPROACH AND DETAILS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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

    arch_img_path = "extracted_report_images/page_11_img_1.png"
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
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E0")),
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
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E0")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_alg2)
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 5: EXPERIMENTAL SETUP AND IMPLEMENTATION
    # ==========================================
    story.append(Paragraph("5. EXPERIMENTAL SETUP AND IMPLEMENTATION", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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

    console_img_path = "extracted_report_images/page_14_img_1.png"
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
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 1. Current Implementation and Verification Status", styles["SubsectionTitle"]))
    story.append(t_impl)
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 6: RESULT ANALYSIS
    # ==========================================
    story.append(Paragraph("6. RESULT ANALYSIS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
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
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
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
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Table 4. Comparative Evaluation Against Existing Phishing Detection Methodologies", styles["SubsectionTitle"]))
    story.append(t_comp)
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 7: CONCLUSION AND FUTURE WORKS
    # ==========================================
    story.append(Paragraph("7. CONCLUSION AND FUTURE WORKS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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

    # ==========================================
    # CHAPTER 8: REFERENCES
    # ==========================================
    story.append(Spacer(1, 8))
    story.append(Paragraph("8. REFERENCES", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_accent, spaceBefore=1, spaceAfter=8))

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

    # ==========================================
    # APPENDIX A: GITHUB REPOSITORY & REPRODUCTION
    # ==========================================
    story.append(Paragraph("APPENDIX A: GITHUB REPOSITORY & IMPLEMENTATION ARTIFACTS", styles["ChapterTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=1, spaceAfter=8))

    app_intro = (
        "DeceptionGuard is released as an open-source cybersecurity project. The complete codebase, documentation, "
        "pre-trained baseline classifiers, unit and integration test suites, evaluation scripts, and UI assets are hosted "
        "on GitHub at the following repository:"
    )
    story.append(Paragraph(app_intro, styles["ReportBody"]))

    repo_url_box = """
    <b>Public GitHub Repository:</b><br/>
    <font color="#1A365D" size="10.5"><b>https://github.com/Swayam-Swaroop-Sahu/DeceptionGuard</b></font>
    """
    t_url = Table([[Paragraph(repo_url_box, styles["ReportBody"])]], colWidths=[504])
    t_url.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
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

    # Build document
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Project Report built successfully: {PDF_PATH}")


def build_two_pass():
    # Pass 1: Build draft
    generate_pdf()

    # Pass 2: Inspect chapter starting pages using pymupdf
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
        body_pno = pno - 2  # pno=3 is Page 4, which is body page 1
        for key, target in chapter_targets.items():
            if target in text and key not in page_map:
                page_map[key] = str(body_pno)

    print("Discovered Chapter Pages (body numbering):", page_map)

    # Re-build PDF with precise TOC page map
    generate_pdf(page_map)
    print("Two-pass build finished successfully!")

if __name__ == "__main__":
    build_two_pass()

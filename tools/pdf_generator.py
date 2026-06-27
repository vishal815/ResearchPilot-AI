"""
ResearchPilot AI — PDF Generator (ReportLab edition)

Why ReportLab instead of fpdf2:
fpdf2 requires manually tracking the cursor (x/y) for every element, which is
what caused the two-column drift bug in the old version. ReportLab's
SimpleDocTemplate uses a "flowable" model — paragraphs, spacers, and images
are appended to a list and the library handles all positioning, wrapping,
and page-breaking automatically. This makes safe chart embedding trivial.

Academic paper style:
- Deep blue (#1e3a5f) bold headings with a horizontal rule underneath,
  matching the "Real-World Examples" reference style.
- Single-column flowable layout, 0.75" margins.
- Charts (Plotly → PNG via kaleido) inserted directly under their matching
  section heading, with calculated spacing before/after so text never
  collides with the image.
"""
import io
import re
import json
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable,
    PageBreak, KeepTogether, Table, TableStyle
)
from reportlab.pdfgen import canvas as pdfcanvas

# ── Brand palette ────────────────────────────────────────────────
DEEP_BLUE   = colors.HexColor("#1e3a5f")   # academic heading colour
ACCENT      = colors.HexColor("#6366f1")   # indigo accent (rules, cover)
TEXT_DARK   = colors.HexColor("#1e1e2e")
MUTED       = colors.HexColor("#64748b")
COVER_BG    = colors.HexColor("#0f172a")
COVER_TEXT  = colors.HexColor("#f1f5f9")

MARGIN = 0.75 * inch


def clean(text: str) -> str:
    """Strip markdown syntax. Escape XML-unsafe chars for ReportLab paragraphs."""
    text = re.sub(r"^#{1,6}\s+", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)   # bold markers
    text = re.sub(r"\*(.+?)\*",     r"\1", text)   # italic markers
    text = re.sub(r"`(.+?)`",       r"\1", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text


def build_styles():
    ss = getSampleStyleSheet()

    ss.add(ParagraphStyle(
        name="RPTitle", fontName="Helvetica-Bold", fontSize=15,
        textColor=DEEP_BLUE, spaceBefore=14, spaceAfter=2, leading=19,
    ))
    ss.add(ParagraphStyle(
        name="RPHeading2", fontName="Helvetica-Bold", fontSize=12.5,
        textColor=DEEP_BLUE, spaceBefore=16, spaceAfter=2, leading=16,
    ))
    ss.add(ParagraphStyle(
        name="RPHeading3", fontName="Helvetica-Bold", fontSize=11,
        textColor=colors.HexColor("#334155"), spaceBefore=10, spaceAfter=4, leading=14,
    ))
    ss.add(ParagraphStyle(
        name="RPBody", fontName="Helvetica", fontSize=10.3,
        textColor=TEXT_DARK, leading=15.5, spaceAfter=6, alignment=TA_JUSTIFY,
    ))
    ss.add(ParagraphStyle(
        name="RPBullet", fontName="Helvetica", fontSize=10.3,
        textColor=TEXT_DARK, leading=15, spaceAfter=4,
        leftIndent=14, bulletIndent=2,
    ))
    ss.add(ParagraphStyle(
        name="RPCaption", fontName="Helvetica-Oblique", fontSize=8.5,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=12,
    ))
    ss.add(ParagraphStyle(
        name="RPCoverBrand", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.HexColor("#a5b4fc"), alignment=TA_CENTER, leading=14,
    ))
    ss.add(ParagraphStyle(
        name="RPCoverTitle", fontName="Helvetica-Bold", fontSize=22,
        textColor=COVER_TEXT, alignment=TA_CENTER, leading=28,
    ))
    ss.add(ParagraphStyle(
        name="RPCoverMeta", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER, leading=15,
    ))
    ss.add(ParagraphStyle(
        name="RPReference", fontName="Helvetica", fontSize=9.3,
        textColor=TEXT_DARK, leading=13.5, spaceAfter=8, leftIndent=14,
    ))
    return ss


def academic_heading(text: str, style, rule_color=DEEP_BLUE, rule_width=1.1):
    """
    Builds a bold deep-blue heading + horizontal rule underneath it,
    as a KeepTogether block so the heading never gets orphaned at the
    bottom of a page separated from its underline.
    """
    flow = [
        Paragraph(text, style),
        Spacer(1, 3),
        HRFlowable(width="100%", thickness=rule_width, color=rule_color,
                  spaceBefore=0, spaceAfter=10),
    ]
    return KeepTogether(flow)


def plotly_json_to_png_matplotlib(chart_json: str) -> bytes:
    """
    Convert a Plotly figure JSON to PNG using matplotlib.
    Works without kaleido — pure Python, works in any Docker container.
    Handles bar charts, line/area charts, pie/donut, gauge, scatter.
    """
    import matplotlib
    matplotlib.use("Agg")           # non-interactive backend, safe in Docker
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np

    data = json.loads(chart_json)
    traces = data.get("data", [])
    layout = data.get("layout", {})
    title  = layout.get("title", {})
    title_text = title.get("text", "") if isinstance(title, dict) else str(title)

    # Strip plotly icon prefix (📊 etc.) from title
    title_text = re.sub(r"^[^\w\s]+\s*", "", title_text).strip()

    COLORS = ["#6366f1","#34d399","#f59e0b","#ef4444","#06b6d4",
              "#8b5cf6","#10b981","#f97316","#a78bfa","#ec4899"]

    fig, ax = plt.subplots(figsize=(9, 4.2))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(colors="#475569", labelsize=9)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)

    plotted = False

    for i, trace in enumerate(traces):
        ttype = trace.get("type", "scatter")
        color = COLORS[i % len(COLORS)]

        if ttype == "bar":
            x = trace.get("x") or trace.get("y") or []
            y = trace.get("y") or trace.get("x") or []
            orient = trace.get("orientation", "v")
            if orient == "h":
                bars = ax.barh([str(v)[:30] for v in x], y, color=color, alpha=0.85)
                ax.set_xlabel(layout.get("xaxis", {}).get("title", {}).get("text",""), fontsize=9)
                # value labels
                for bar in bars:
                    w = bar.get_width()
                    ax.text(w * 1.01, bar.get_y() + bar.get_height()/2,
                            f"{w:,.1f}", va="center", fontsize=7, color="#334155")
            else:
                xs = list(range(len(x)))
                ax.bar(xs, y, color=color, alpha=0.85)
                ax.set_xticks(xs)
                ax.set_xticklabels([str(v)[:18] for v in x], rotation=30, ha="right", fontsize=8)
            plotted = True

        elif ttype == "scatter":
            x = trace.get("x", [])
            y = trace.get("y", [])
            mode = trace.get("mode", "lines")
            name = trace.get("name", "")
            fill = trace.get("fill", "")
            if "lines" in mode or fill:
                ax.plot(x, y, color=color, linewidth=2, label=name, marker="o",
                        markersize=4, markerfacecolor=color)
                if fill:
                    ax.fill_between(range(len(y)), y, alpha=0.08, color=color)
            if "markers" in mode and "lines" not in mode:
                sizes = trace.get("marker", {}).get("size", 10)
                if isinstance(sizes, list):
                    sizes = [max(20, min(300, s*s)) for s in sizes]
                ax.scatter(range(len(x)), y, s=sizes, color=color, alpha=0.7, label=name)
            plotted = True

        elif ttype in ("pie", "sunburst"):
            labels = trace.get("labels", [])
            values = trace.get("values", [])
            hole   = trace.get("hole", 0)
            if labels and values:
                wedge_colors = COLORS[:len(labels)]
                wedges, texts, autotexts = ax.pie(
                    values, labels=[str(l)[:20] for l in labels],
                    colors=wedge_colors, autopct="%1.1f%%",
                    startangle=90, pctdistance=0.75,
                    wedgeprops={"linewidth": 1, "edgecolor": "white"}
                )
                for t in texts:    t.set_fontsize(8)
                for t in autotexts: t.set_fontsize(7)
                if hole > 0:
                    centre = plt.Circle((0, 0), hole, color="white")
                    ax.add_artist(centre)
                plotted = True

        elif ttype == "indicator":
            # Render as a large number in the centre
            val = trace.get("value", 0)
            suffix = trace.get("number", {}).get("suffix", "")
            ax.text(0.5, 0.55, f"{val:.1f}{suffix}", transform=ax.transAxes,
                    ha="center", va="center", fontsize=38, fontweight="bold",
                    color="#6366f1")
            title_inner = trace.get("title", {}).get("text", "")
            if title_inner:
                ax.text(0.5, 0.25, title_inner, transform=ax.transAxes,
                        ha="center", va="center", fontsize=10, color="#64748b")
            ax.axis("off")
            plotted = True

    if not plotted:
        ax.text(0.5, 0.5, "Chart data unavailable",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=11, color="#94a3b8")
        ax.axis("off")

    # Title
    if title_text:
        fig.suptitle(title_text, fontsize=11, fontweight="bold",
                     color="#1e3a5f", y=0.98)

    # Legend (for multi-trace)
    if len(traces) > 1 and any(t.get("type") not in ("pie","indicator") for t in traces):
        ax.legend(fontsize=8, loc="upper right", framealpha=0.6)

    # Y-axis label
    yaxis = layout.get("yaxis", {})
    ylabel = yaxis.get("title", {})
    if isinstance(ylabel, dict): ylabel = ylabel.get("text","")
    if ylabel: ax.set_ylabel(str(ylabel), fontsize=9, color="#475569")

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="#ffffff")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def chart_image_flowable(png_bytes: bytes, max_width_in: float = 6.4):
    """
    Converts chart PNG bytes into a properly-sized ReportLab Image flowable,
    preserving aspect ratio, with calculated spacers before/after so the
    image never collides with surrounding text.
    """
    from PIL import Image as PILImage
    pil_img = PILImage.open(io.BytesIO(png_bytes))
    w_px, h_px = pil_img.size
    aspect = h_px / w_px

    target_w = max_width_in * inch
    target_h = target_w * aspect
    max_h = 3.6 * inch
    if target_h > max_h:
        target_h = max_h
        target_w = target_h / aspect

    img = Image(io.BytesIO(png_bytes), width=target_w, height=target_h)
    return [Spacer(1, 6), img, Spacer(1, 10)]


def render_charts_for_section(chart_specs, section_key, styles):
    """
    Returns a list of flowables for charts matching this section_key.
    Uses matplotlib (no kaleido needed) — works in any Docker environment.
    """
    flowables = []
    matched = [c for c in chart_specs if c.get("section") == section_key]
    if not matched:
        return flowables

    for spec in matched:
        try:
            png_bytes = plotly_json_to_png_matplotlib(spec["json"])
            flowables.extend(chart_image_flowable(png_bytes))
            if spec.get("caption"):
                flowables.append(Paragraph(clean(spec["caption"]), styles["RPCaption"]))
        except Exception as e:
            flowables.append(Paragraph(
                f"<i>[Chart rendering error: {str(e)[:80]}]</i>", styles["RPCaption"]
            ))
    return flowables


# ── Section-name → chart-tag mapping ───────────────────────────
# Report headings (## Statistical Overview, ## Key Findings, etc.) are
# matched against this map (case-insensitive substring match) to decide
# where each generated chart gets seamlessly inserted.
SECTION_CHART_MAP = {
    "statistical overview": "statistics",
    "key findings":         "key_findings",
    "data":                 "statistics",
}


def _section_key_for_heading(heading_text: str):
    h = heading_text.lower()
    for key_phrase, tag in SECTION_CHART_MAP.items():
        if key_phrase in h:
            return tag
    return None


def _strip_references_section(report: str) -> str:
    """
    Removes a trailing '## References' (or '# References') section from the
    report markdown, including everything after it up to the next heading of
    equal-or-higher level or the end of the document / footer line.
    This prevents the LLM-written reference list from duplicating the
    structured citations list rendered separately by generate_pdf().
    """
    lines = report.split("\n")
    out = []
    skipping = False
    skip_level = None

    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")

    for line in lines:
        m = heading_re.match(line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip().lower()

            if skipping:
                # Stop skipping once we hit a heading at the same or
                # shallower level than the References heading itself.
                if level <= skip_level:
                    skipping = False
                else:
                    continue  # still inside the references subsection

            if title == "references":
                skipping = True
                skip_level = level
                continue  # drop the heading line itself

        if skipping:
            # Also stop skipping on the footer divider/attribution line
            if line.strip().startswith("---") or "Report generated by" in line:
                skipping = False
            else:
                continue

        out.append(line)

    return "\n".join(out)


def _cover_page(canvas_obj, doc, query, today, score, agents_str):
    canvas_obj.saveState()
    canvas_obj.setFillColor(COVER_BG)
    canvas_obj.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas_obj.setFillColor(ACCENT)
    canvas_obj.rect(0, 0, 5, doc.pagesize[1], fill=1, stroke=0)
    canvas_obj.restoreState()


def generate_pdf(report, query, quality_score, citations,
                 chart_json_list=None, thumbnail_svg=None, active_agents=None):
    """
    Builds a professional, academic-style research PDF using ReportLab's
    flowable layout engine. Charts are safely embedded directly beneath
    their matching section heading with auto-calculated spacing.

    chart_json_list: list of Plotly JSON strings (order = generation order).
    Charts are auto-tagged to sections using simple heuristics: the first
    chart goes under "Statistical Overview" / "Key Findings" if present,
    remaining charts append to an "Additional Data Visualizations" section
    near the end — never overlapping text.
    """
    active_agents = active_agents or []
    chart_json_list = chart_json_list or []
    today = date.today().strftime("%B %d, %Y")
    styles = build_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"ResearchPilot AI — {query[:80]}",
    )

    story = []

    # ── COVER PAGE ───────────────────────────────────────────────
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("RESEARCHPILOT AI&nbsp;&nbsp;|&nbsp;&nbsp;AUTONOMOUS MULTI-AGENT RESEARCH",
                           styles["RPCoverBrand"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(clean(query[:140]), styles["RPCoverTitle"]))
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph(f"Generated: {today}", styles["RPCoverMeta"]))
    story.append(Paragraph(f"Quality Score: {quality_score:.1f} / 10", styles["RPCoverMeta"]))
    agents_str = ", ".join(active_agents) if active_agents else "—"
    story.append(Paragraph(f"Agents: {agents_str}", styles["RPCoverMeta"]))
    story.append(PageBreak())

    # ── Build chart spec list with auto-section tagging ───────────
    chart_specs = []
    if chart_json_list:
        # First chart → Statistical Overview, second → Key Findings,
        # rest → end-of-report "Additional Visualizations" section.
        tags = ["statistics", "key_findings"]
        for idx, cj in enumerate(chart_json_list):
            tag = tags[idx] if idx < len(tags) else None
            chart_specs.append({
                "json": cj,
                "section": tag,
                "caption": f"Figure {idx + 1}. Data visualization generated by the Statistics Agent.",
            })

    used_chart_indices = set(
        i for i, spec in enumerate(chart_specs) if spec["section"] is not None
    )

    # ── Strip any "## References" section from the report body ────
    # The synthesizer LLM often writes its own References section as
    # plain text. We only want the structured `citations` list (passed
    # in separately) to render — otherwise references appear twice.
    report = _strip_references_section(report)

    # ── REPORT BODY — parse markdown, insert charts inline ────────
    lines = report.split("\n")
    i = 0
    pending_bullets = []

    def flush_bullets():
        nonlocal pending_bullets
        if pending_bullets:
            for b in pending_bullets:
                story.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean(b)}", styles["RPBullet"]))
            pending_bullets = []

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        i += 1

        if not line.strip():
            flush_bullets()
            continue

        if line.strip() == "---":
            flush_bullets()
            continue

        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(clean(line[2:].strip()), styles["RPTitle"]))
            story.append(Spacer(1, 4))

        elif line.startswith("## "):
            flush_bullets()
            heading_text = line[3:].strip()
            story.append(academic_heading(clean(heading_text), styles["RPHeading2"]))

            # Seamless chart insertion directly under matching heading
            section_tag = _section_key_for_heading(heading_text)
            if section_tag:
                chart_flowables = render_charts_for_section(chart_specs, section_tag, styles)
                story.extend(chart_flowables)

        elif line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(clean(line[4:].strip()), styles["RPHeading3"]))

        elif line.startswith("• ") or line.startswith("- "):
            pending_bullets.append(line[2:].strip())

        else:
            flush_bullets()
            story.append(Paragraph(clean(line), styles["RPBody"]))

    flush_bullets()

    # ── Any charts not matched to a section → appendix ────────────
    leftover = [s for idx, s in enumerate(chart_specs) if idx not in used_chart_indices]
    if leftover:
        story.append(PageBreak())
        story.append(academic_heading("Additional Data Visualizations", styles["RPHeading2"]))
        for spec in leftover:
            try:
                png_bytes = plotly_json_to_png_matplotlib(spec["json"])
                story.extend(chart_image_flowable(png_bytes))
                story.append(Paragraph(clean(spec["caption"]), styles["RPCaption"]))
            except Exception:
                pass

    # ── REFERENCES PAGE ────────────────────────────────────────────
    if citations:
        story.append(PageBreak())
        story.append(academic_heading("References", styles["RPHeading2"]))
        for c in citations:
            apa = clean(c.get("apa") or f"[{c.get('number','')}] {c.get('title','')}")
            story.append(Paragraph(apa, styles["RPReference"]))

    # ── Build with cover-page background callback ──────────────────
    def on_first_page(canvas_obj, doc_obj):
        _cover_page(canvas_obj, doc_obj, query, today, quality_score, agents_str)

    def on_later_pages(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(MUTED)
        canvas_obj.drawCentredString(
            doc_obj.pagesize[0] / 2, 0.4 * inch,
            f"ResearchPilot AI  —  Page {doc_obj.page}"
        )
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
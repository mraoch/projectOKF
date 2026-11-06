"""
Draw the block diagrams used in the notebook (saved to images/).

    python scripts/make_diagrams.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

OUT = Path(__file__).resolve().parent.parent / "images"

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

INK = "#1f1f1f"
MUTED = "#5f5e5a"
ARROW = "#8a8984"
GREY = "#7d7c78"
SCHEMA = "#eb6834"   # orange: schema-only context
INDEX = "#2a78d6"    # blue: OKF index files
CONCEPT = "#1baf7a"  # green: OKF concept files
LLM = "#7a5af5"      # purple: a call to the LLM
DB = "#336791"       # Postgres blue
BAD = "#d64545"
GOOD = "#1a9e6c"


def tint(hex_colour, amount=0.88):
    """Mix a colour with white so it can be used as a soft box fill."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    mix = lambda c: int(c + (255 - c) * amount)
    return f"#{mix(r):02x}{mix(g):02x}{mix(b):02x}"


def canvas(title, subtitle=None):
    """Blank 16x9 drawing area. The title/subtitle are not drawn: the notebook's markdown heading
    already says it, so they are only kept here as a note of what each picture is for."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, title, body="", colour=GREY, step=None, title_size=16, body_size=12.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.18",
                                fc=tint(colour), ec=colour, lw=2.2))
    if body:
        ax.text(x + w / 2, y + h - 0.32, title, fontsize=title_size, fontweight="bold",
                color=INK, ha="center", va="top")
        ax.text(x + w / 2, y + (h - 0.75) / 2, body, fontsize=body_size, color=MUTED,
                ha="center", va="center", linespacing=1.45)
    else:
        ax.text(x + w / 2, y + h / 2, title, fontsize=title_size, fontweight="bold",
                color=INK, ha="center", va="center", linespacing=1.3)
    if step is not None:
        ax.add_patch(Circle((x + 0.05, y + h - 0.05), 0.27, fc=colour, ec="white", lw=2, zorder=5))
        ax.text(x + 0.05, y + h - 0.05, str(step), fontsize=14, fontweight="bold",
                color="white", ha="center", va="center", zorder=6)


def arrow(ax, start, end, colour=ARROW, rad=0.0, label=None, label_pos=None):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=colour, lw=2.2, mutation_scale=22,
                                shrinkA=2, shrinkB=2, connectionstyle=f"arc3,rad={rad}"))
    if label:
        lx, ly = label_pos or ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.22)
        ax.text(lx, ly, label, fontsize=11.5, color=MUTED, ha="center", va="bottom", style="italic")


def chip(ax, x, y, text, colour, w=2.55, h=0.42):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="white", ec=colour, lw=1.6))
    ax.text(x + 0.12, y + h / 2, text, fontsize=9, color=INK, va="center", family="monospace")


def legend(ax, items, y=0.35):
    x = 0.4
    for label, colour in items:
        ax.add_patch(FancyBboxPatch((x, y - 0.13), 0.26, 0.26, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=tint(colour), ec=colour, lw=1.6))
        ax.text(x + 0.4, y, label, fontsize=12, color=MUTED, va="center")
        x += 0.4 + 0.115 * len(label) + 0.7


def save(fig, name, ylim):
    """ylim crops the empty space above and below the drawing (the title area is no longer used)."""
    fig.axes[0].set_ylim(*ylim)
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.25, facecolor="white")
    plt.close(fig)
    print("saved", OUT / name)


# ---------------------------------------------------------------------------
# 1. The big picture: one question, two agents, one ground truth
# ---------------------------------------------------------------------------

def overview():
    fig, ax = canvas("One question, two agents",
                     "Same LLM, same database, same code. The only thing that changes is what the LLM gets to read.")

    box(ax, 0.4, 3.55, 2.6, 1.9, "Business\nquestion", colour=GREY, title_size=17)

    # top lane: without OKF
    ax.text(3.7, 6.95, "WITHOUT OKF", fontsize=13, fontweight="bold", color=SCHEMA)
    box(ax, 3.7, 5.2, 3.2, 1.5, "Schema only", "table and column names", SCHEMA)
    box(ax, 7.6, 5.2, 2.4, 1.5, "LLM", "writes SQL", LLM)
    box(ax, 10.7, 5.2, 2.2, 1.5, "PostgreSQL", "runs it", DB)
    box(ax, 13.6, 5.2, 2.0, 1.5, "Answer", "may be a guess", BAD)

    # bottom lane: with OKF
    ax.text(3.7, 3.25, "WITH OKF", fontsize=13, fontweight="bold", color=CONCEPT)
    box(ax, 3.7, 1.5, 3.2, 1.5, "OKF files", "definitions + business rules", CONCEPT)
    box(ax, 7.6, 1.5, 2.4, 1.5, "LLM", "writes SQL", LLM)
    box(ax, 10.7, 1.5, 2.2, 1.5, "PostgreSQL", "runs it", DB)
    box(ax, 13.6, 1.5, 2.0, 1.5, "Answer", "follows the rules", GOOD)

    arrow(ax, (3.0, 4.7), (3.7, 5.95))
    arrow(ax, (3.0, 4.3), (3.7, 2.25))
    for lane_y in (5.95, 2.25):
        arrow(ax, (6.9, lane_y), (7.6, lane_y))
        arrow(ax, (10.0, lane_y), (10.7, lane_y))
        arrow(ax, (12.9, lane_y), (13.6, lane_y))

    # ground truth sits between the two answers
    ax.add_patch(FancyBboxPatch((13.35, 3.55), 2.5, 1.0, boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#fff8e6", ec="#eda100", lw=2.2, ls="--"))
    ax.text(14.6, 4.05, "Ground truth\nhand-written SQL", fontsize=12.5, fontweight="bold", color=INK,
            ha="center", va="center", linespacing=1.3)
    arrow(ax, (14.6, 4.55), (14.6, 5.2), colour="#eda100")
    arrow(ax, (14.6, 3.55), (14.6, 3.0), colour="#eda100")
    ax.text(15.95, 4.05, "compare", fontsize=11.5, color="#b07a00", rotation=90, va="center", style="italic")

    save(fig, "01_overview.png", ylim=(1.2, 7.3))


# ---------------------------------------------------------------------------
# 2. Question 1 without OKF, step by step
# ---------------------------------------------------------------------------

def without_okf():
    fig, ax = canvas("Question 1 without OKF",
                     "The LLM only knows table and column names, so it has to guess what the business means.")

    ax.text(0.4, 6.7, "“What was the average delivery time in each city in October 2026?”",
            fontsize=17, color=INK, style="italic")

    y, h = 3.3, 2.6
    box(ax, 0.4, y, 3.3, h, "Schema only",
        "orders: order_id, city,\nstatus, order_placed_at,\norder_delivered_at, ...\n\nrestaurants: ...", SCHEMA, step=1)
    box(ax, 4.45, y, 3.3, h, "LLM writes SQL", "question + schema\n↓\none SQL query", LLM, step=2)
    box(ax, 8.5, y, 3.3, h, "Run the SQL", "PostgreSQL\n(read-only user)\n↓\nresult table", DB, step=3)
    box(ax, 12.55, y, 3.05, h, "LLM writes\nthe answer", "result → 2-4 sentences\nin plain English", LLM, step=4)
    for x in (3.7, 7.75, 11.8):
        arrow(ax, (x, y + h / 2), (x + 0.75, y + h / 2))

    # what is missing
    ax.add_patch(FancyBboxPatch((0.4, 0.75), 9.2, 1.85, boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#fdeeee", ec=BAD, lw=1.8, ls="--"))
    ax.text(0.7, 2.3, "Rules the LLM can't see (they live in metrics/delivery_time.md)",
            fontsize=13.5, fontweight="bold", color=BAD, va="top")
    ax.text(0.7, 1.75, "• Only 'Delivered' orders count, cancelled ones never do\n"
                       "• Delivery time = delivered_at minus placed_at, in minutes\n"
                       "• Averages are rounded to 1 decimal",
            fontsize=12.5, color=INK, va="top", linespacing=1.5)
    arrow(ax, (2.05, 2.6), (2.05, 3.3), colour=BAD)

    save(fig, "02_without_okf.png", ylim=(0.5, 7.2))


# ---------------------------------------------------------------------------
# 3. Question 1 with OKF, step by step
# ---------------------------------------------------------------------------

def with_okf():
    fig, ax = canvas("Question 1 with OKF",
                     "The agent reads the small index files first, then opens only the files it needs.")

    # the bundle
    ax.add_patch(FancyBboxPatch((0.4, 5.05), 15.2, 2.45, boxstyle="round,pad=0,rounding_size=0.18",
                                fc="#f6f6f4", ec="#c9c8c3", lw=1.6))
    ax.text(0.7, 7.2, "OKF bundle   okf/aai-food/", fontsize=14, fontweight="bold", color=INK, va="center")
    ax.text(0.7, 6.65, "index files (table of contents)", fontsize=11.5, color=INDEX, va="center")
    for i, name in enumerate(["index.md", "tables/index.md", "metrics/index.md",
                              "glossary/index.md", "playbooks/index.md"]):
        chip(ax, 0.7 + (i % 2) * 2.4, 6.05 - (i // 2) * 0.5, name, INDEX, w=2.25)
    ax.plot([5.6, 5.6], [5.3, 7.3], color="#c9c8c3", lw=1.4)
    ax.text(5.85, 6.65, "concept files (definitions, rules, playbooks)", fontsize=11.5, color=CONCEPT, va="center")
    for i, name in enumerate(["tables/orders.md", "tables/restaurants.md", "metrics/delivery_time.md",
                              "metrics/late_delivery_rate.md", "metrics/net_revenue.md",
                              "glossary/business_terms.md", "playbooks/heavy_rain.md"]):
        chip(ax, 5.85 + (i % 3) * 3.25, 6.05 - (i // 3) * 0.5, name, CONCEPT, w=3.15)

    # top row: steps 1-3
    y1, h = 2.75, 1.65
    box(ax, 0.4, y1, 2.9, h, "Question 1", "average delivery time\nper city, Oct 2026", GREY)
    box(ax, 4.0, y1, 3.3, h, "Read index files", "only the 5 short\ntable-of-contents files", INDEX, step=1)
    box(ax, 8.0, y1, 3.3, h, "LLM picks files", "“I need these 3 files”", LLM, step=2)
    box(ax, 12.0, y1, 3.6, h, "Read those files", "full text: definitions,\nfilters, rules", CONCEPT, step=3)
    arrow(ax, (3.3, y1 + h / 2), (4.0, y1 + h / 2))
    arrow(ax, (7.3, y1 + h / 2), (8.0, y1 + h / 2))
    arrow(ax, (11.3, y1 + h / 2), (12.0, y1 + h / 2))
    arrow(ax, (3.5, 5.05), (5.6, y1 + h), colour=INDEX)
    arrow(ax, (11.0, 5.05), (13.8, y1 + h), colour=CONCEPT)

    # bottom row: steps 4-6, running right to left under the top row
    y2 = 0.35
    box(ax, 12.0, y2, 3.6, h, "LLM writes SQL", "question + OKF files\n↓ one SQL query", LLM, step=4)
    box(ax, 8.0, y2, 3.3, h, "Run the SQL", "PostgreSQL\n(read-only user)", DB, step=5)
    box(ax, 4.0, y2, 3.3, h, "LLM writes the answer", "plain English\n+ the files it used", LLM,
        step=6, title_size=15)
    arrow(ax, (13.8, y1), (13.8, y2 + h))
    arrow(ax, (12.0, y2 + h / 2), (11.3, y2 + h / 2))
    arrow(ax, (8.0, y2 + h / 2), (7.3, y2 + h / 2))

    ax.text(2.0, 1.15, "Steps 4-6 are the\nsame code as\nwithout OKF.\nOnly the input\nchanged.",
            fontsize=12.5, color=MUTED, ha="center", va="center", style="italic", linespacing=1.35)

    save(fig, "03_with_okf.png", ylim=(0.1, 7.7))


# ---------------------------------------------------------------------------
# 4. Changing a rule: edit a markdown file, not the code
# ---------------------------------------------------------------------------

def update_knowledge():
    fig, ax = canvas("Changing a rule",
                     "The team edits a markdown file. No Python changes, no redeploy.")

    y, h = 3.6, 2.3
    box(ax, 0.4, y, 3.4, h, "New team rule", "“Always show the counts\nwith the late rate”", GREY, step=1)
    box(ax, 4.5, y, 3.4, h, "Edit one file", "metrics/\nlate_delivery_rate.md\n+ a line in log.md", CONCEPT, step=2)
    box(ax, 8.6, y, 3.4, h, "Ask again", "same question 2,\nsame code", LLM, step=3)
    box(ax, 12.7, y, 2.9, h, "New answer", "12.7%\n(42 late out of 331)", GOOD, step=4)
    for x in (3.8, 7.9, 12.0):
        arrow(ax, (x, y + h / 2), (x + 0.7, y + h / 2))

    ax.add_patch(FancyBboxPatch((4.5, 1.2), 7.5, 1.4, boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#f6f6f4", ec="#c9c8c3", lw=1.4, ls="--"))
    ax.text(8.25, 1.9, "okf_agent.py   →   untouched", fontsize=15, color=MUTED,
            ha="center", va="center", family="monospace")

    save(fig, "04_update_knowledge.png", ylim=(0.9, 6.3))


if __name__ == "__main__":
    overview()
    without_okf()
    with_okf()
    update_knowledge()

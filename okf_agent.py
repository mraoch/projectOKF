"""
Helpers for the Aai-Food x OKF notebook.

Sections, in the order the notebook uses them:
  1. Settings
  2. Database      run_sql
  3. LLM           ask_llm
  4. OKF bundle    load_bundle, validate_bundle, build_graph, draw_graph
  5. Context       schema_only (no OKF), index_files / select_concepts / read_concepts (OKF)
  6. Steps         write_sql, write_answer
  7. Agents        ask_without_okf, ask_with_okf
"""

import json
import os
import re
import time
from functools import cache
from pathlib import Path

import frontmatter
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from matplotlib.lines import Line2D


# =============================================================================
# 1. Settings
# =============================================================================

PROJECT_DIR = Path(__file__).resolve().parent
BUNDLE_PATH = PROJECT_DIR / "okf" / "aai-food"

# "Last Friday" in the questions is worked out from this date
TODAY = "2026-11-02 (Monday)"

load_dotenv(PROJECT_DIR / ".env")


# =============================================================================
# 2. Database
# =============================================================================

def run_sql(sql):
    """Run one SELECT query as the read-only user and return a DataFrame."""
    sql = sql.strip().rstrip(";").strip()

    # Only allow a single SELECT / WITH query
    first_word = sql.split(None, 1)[0].upper() if sql else ""
    if first_word not in ("SELECT", "WITH") or ";" in sql:
        raise ValueError("Only a single SELECT or WITH query is allowed.")

    # Never pull back more than 200 rows
    if not re.search(r"\blimit\s+\d+", sql, re.IGNORECASE):
        sql = f"SELECT * FROM (\n{sql}\n) AS q LIMIT 200"

    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DB", "aai_food"),
        user="okf_reader",
        password=os.getenv("PG_READER_PASSWORD"),
    )
    conn.set_session(readonly=True)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [col.name for col in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        conn.close()


# =============================================================================
# 3. LLM
# =============================================================================

@cache
def _groq():
    # Reads GROQ_API_KEY from .env. Retries are handled in ask_llm below.
    return Groq(max_retries=0)


def ask_llm(system, user):
    """Send one message to the LLM and return its reply as text."""
    def call():
        response = _groq().chat.completions.create(
            model=os.getenv("LLM_MODEL", "openai/gpt-oss-120b"),
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0,
            max_completion_tokens=2000,
        )
        return (response.choices[0].message.content or "").strip()

    try:
        return call()
    except RateLimitError:
        # Groq's free tier has a per-minute limit; wait once and try again
        print("Groq rate limit reached, waiting 20 seconds...")
        time.sleep(20)
        return call()


# =============================================================================
# 4. OKF bundle: load, validate, draw
# =============================================================================

# Matches a markdown link [text](target) and captures the target
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _link_to_path(target, from_file):
    """'/tables/orders.md' -> 'tables/orders.md'. Returns None for web links."""
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = target.split("#")[0]
    if target.startswith("/"):                               # link from the bundle root
        return target.lstrip("/")
    return (Path(from_file).parent / target).as_posix()      # link relative to this file


def load_bundle():
    """Read every .md file in the bundle: its type, title and the files it links to."""
    concepts = []
    for md_file in sorted(BUNDLE_PATH.rglob("*.md")):
        path = md_file.relative_to(BUNDLE_PATH).as_posix()
        try:
            post = frontmatter.load(md_file)
        except Exception as error:
            concepts.append({"path": path, "error": f"front matter does not parse: {error}"})
            continue

        links = {_link_to_path(target, path) for target in LINK_PATTERN.findall(post.content)}
        concepts.append({
            "path": path,
            "type": post.get("type"),
            "title": post.get("title"),
            "links": sorted(link for link in links if link),
        })
    return concepts


def validate_bundle(concepts):
    """Every file needs a 'type', and every link must point to a real file. [] = valid."""
    problems = []
    all_paths = {c["path"] for c in concepts}

    for c in concepts:
        if "error" in c:
            problems.append(f"{c['path']}: {c['error']}")
            continue
        if not str(c["type"] or "").strip():
            problems.append(f"{c['path']}: front matter is missing 'type'")
        for link in c["links"]:
            if link not in all_paths:
                problems.append(f"{c['path']}: broken link -> /{link}")
    return problems


def build_graph(concepts):
    """One node per file, one arrow per link."""
    G = nx.DiGraph()
    for c in concepts:
        G.add_node(c["path"], type=c.get("type") or "Unknown")
    for c in concepts:
        for link in c.get("links", []):
            if link in G:
                G.add_edge(c["path"], link)
    return G


TYPE_COLOURS = {
    "Index": "#2a78d6",
    "Table": "#eb6834",
    "Metric": "#1baf7a",
    "Playbook": "#eda100",
    "Glossary": "#e87ba4",
    "Log": "#9a9893",
}


def _colour_group(okf_type):
    # "PostgreSQL Table" -> "Table", everything else stays as it is
    return "Table" if "Table" in okf_type else okf_type


def _label(path):
    # 'metrics/net_revenue.md' -> 'net_revenue',  'tables/index.md' -> 'tables/index'
    p = Path(path)
    return f"{p.parent.name}/index" if p.stem == "index" and p.parent.name else p.stem


def draw_graph(G):
    """Draw the bundle as rings: root index in the middle, folder indexes around it, files outside."""
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)

    centre = [n for n in G if n == "index.md"]
    middle = sorted(n for n in G if n not in centre and (n.endswith("index.md") or "/" not in n))
    outer = sorted(n for n in G if n not in centre and n not in middle)
    pos = nx.shell_layout(G, nlist=[centre, middle, outer], rotate=0.3)

    colours = [TYPE_COLOURS.get(_colour_group(G.nodes[n]["type"]), "#9a9893") for n in G]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#b5b4ae", width=1.2, arrows=True,
                           arrowsize=14, node_size=1400, connectionstyle="arc3,rad=0.08")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colours, node_size=1400,
                           edgecolors="white", linewidths=2)

    # File name just under each dot
    for node, (x, y) in pos.items():
        ax.annotate(_label(node), (x, y), xytext=(0, -26), textcoords="offset points",
                    ha="center", va="top", fontsize=13, color="#0b0b0b",
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5))

    # Legend: only the types that are actually in the bundle
    present = sorted({_colour_group(G.nodes[n]["type"]) for n in G}, key=list(TYPE_COLOURS).index)
    handles = [Line2D([], [], marker="o", linestyle="", markersize=14, label=t,
                      markerfacecolor=TYPE_COLOURS[t], markeredgecolor="white") for t in present]
    ax.legend(handles=handles, loc="upper left", fontsize=13, frameon=False,
              title="Concept type", title_fontsize=13)

    ax.set_title(f"Aai-Food OKF bundle: {G.number_of_nodes()} concepts, {G.number_of_edges()} links",
                 fontsize=18, loc="left")
    ax.axis("off")
    fig.tight_layout()
    plt.show()


# =============================================================================
# 5. Context: what the LLM gets to read before writing SQL
# =============================================================================

# --- Without OKF: only the schema --------------------------------------------

def schema_only():
    """Table and column names with their data types. No meaning, no rules."""
    df = run_sql("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name IN ('orders', 'restaurants')
        ORDER BY table_name, ordinal_position
    """)
    lines = []
    for table, cols in df.groupby("table_name"):
        columns = ", ".join(f"{c} ({t})" for c, t in zip(cols.column_name, cols.data_type))
        lines.append(f"- {table}: {columns}")
    return "Database tables:\n" + "\n".join(lines)


# --- With OKF: index files first, then only the files that are needed -------

def _read(path):
    return (BUNDLE_PATH / path).read_text(encoding="utf-8")


def index_files():
    """The table-of-contents files: index.md plus one index.md per folder."""
    folders = sorted(p.relative_to(BUNDLE_PATH).as_posix() for p in BUNDLE_PATH.glob("*/index.md"))
    return ["index.md"] + folders


def select_concepts(question):
    """Show the LLM the index files only. It replies with up to 3 files it wants to read."""
    indexes = "\n\n".join(f"=== {name} ===\n{_read(name)}" for name in index_files())

    system = ("You help a data analyst find documentation. You see only the table-of-contents "
              "files of a knowledge bundle. Pick the concept files needed to answer the question "
              "correctly: tables to query, metric definitions, playbooks and glossary terms. "
              "Reply with ONLY a JSON list of up to 3 paths, e.g. [\"tables/orders.md\"].")
    reply = ask_llm(system, f"Today's date: {TODAY}\n\nQuestion: {question}\n\n{indexes}")

    # Pull the JSON list out of the reply and keep only files that really exist
    match = re.search(r"\[.*?\]", reply, re.DOTALL)
    chosen = json.loads(match.group(0)) if match else []
    chosen = [p.lstrip("/") for p in chosen if (BUNDLE_PATH / p.lstrip("/")).is_file()][:3]

    print("OKF files chosen:", ", ".join(chosen) or "(none)")
    return chosen


def read_concepts(paths):
    """Full text of the chosen files, joined into one block for the prompt."""
    knowledge = "\n\n".join(f"=== {p} ===\n{_read(p)}" for p in paths)
    return f"OKF knowledge files:\n\n{knowledge}"


# =============================================================================
# 6. Steps: the LLM writes SQL, then turns the result into an answer
# =============================================================================

BASELINE_SYSTEM = "You are a data analyst for a food delivery company. You query a PostgreSQL database."

OKF_SYSTEM = ("You are a data analyst for Aai-Food Delivery. You query a PostgreSQL database. "
              "The OKF knowledge files below are the source of truth: follow their definitions, "
              "filters, allowed values and reporting rules exactly.")

SQL_RULES = ("Write ONE PostgreSQL query that answers the question. "
             "Return the numbers the answer depends on as columns (e.g. the metric you rank or filter by). "
             "Put it inside a ```sql code block. Return only that code block.")


def write_sql(question, system, context, failed_sql=None, error=None):
    """Ask the LLM for one SQL query. Pass failed_sql + error to ask it to fix a broken one."""
    prompt = f"Today's date: {TODAY}\n\n{context}\n\nQuestion: {question}"
    if failed_sql:
        prompt += f"\n\nThis SQL:\n```sql\n{failed_sql}\n```\nfailed with:\n{error}\n\nFix it."

    reply = ask_llm(system, f"{prompt}\n\n{SQL_RULES}")

    # Take what's inside ```sql ... ```, or the whole reply if there's no code block
    match = re.search(r"```sql\s*(.*?)```", reply, re.DOTALL | re.IGNORECASE)
    return (match.group(1) if match else reply).strip()


def write_answer(question, system, sql, df, files_used=()):
    """Ask the LLM to explain the result in a few plain sentences."""
    # The OKF files are not sent again here, to stay under Groq's tokens-per-minute limit
    cite = f" End with 'Sources: {', '.join(files_used)}'." if files_used else ""
    prompt = (f"Today's date: {TODAY}\nQuestion: {question}\n\n"
              f"SQL used:\n```sql\n{sql}\n```\n\n"
              f"Result:\n{df.head(30).to_markdown(index=False)}\n\n"
              f"Answer the question for a business user in 2-4 sentences with the key numbers "
              f"(rounded to 1 decimal). Only use numbers that appear in the result; never estimate "
              f"or invent a number that is not there.{cite}")
    return ask_llm(system, prompt)


# =============================================================================
# 7. Agents: all the steps in one call
# =============================================================================

def ask_without_okf(question):
    """Agent that only knows the table and column names."""
    return _answer(question, BASELINE_SYSTEM, schema_only(), files_used=[])


def ask_with_okf(question):
    """Agent that picks files from the OKF bundle, reads them, then follows their rules."""
    files_used = select_concepts(question)
    return _answer(question, OKF_SYSTEM, read_concepts(files_used), files_used)


def _try_sql(sql):
    """Run the SQL. Returns (DataFrame, None) if it worked, or (None, error message) if not."""
    try:
        return run_sql(sql), None
    except Exception as error:
        return None, str(error).strip()


def _answer(question, system, context, files_used):
    """Write SQL -> run it (one retry if it fails) -> write the answer -> print everything."""
    sql = write_sql(question, system, context)
    df, error = _try_sql(sql)

    if error:
        print("SQL failed, asking the LLM to fix it:", error.splitlines()[0])
        sql = write_sql(question, system, context, failed_sql=sql, error=error)
        df, error = _try_sql(sql)

    if error:
        answer = f"Could not answer: the SQL failed twice ({error.splitlines()[0]})."
    else:
        answer = write_answer(question, system, sql, df, files_used)

    result = {"question": question, "files_used": files_used, "sql": sql, "dataframe": df, "answer": answer}
    _print_result(result)
    return result


def _print_result(result):
    print("Question:", result["question"])
    if result["files_used"]:
        print("Files used:", ", ".join(result["files_used"]))

    print(f"\nSQL:\n{result['sql']}\n")

    df = result["dataframe"]
    if df is not None:
        print(df.head(10).to_markdown(index=False, floatfmt=".1f"))
        if len(df) > 10:
            print(f"... ({len(df)} rows)")

    print(f"\nAnswer:\n{result['answer']}\n")

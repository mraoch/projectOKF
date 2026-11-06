# Aai-Food Delivery × Open Knowledge Format (OKF)

Aai-Food Delivery's October 2026 orders live in PostgreSQL. An OKF knowledge bundle
(`okf/aai-food/`) explains the tables, metrics and business rules. The notebook shows an AI
agent answering business questions first without the bundle and then with it.

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), a local PostgreSQL server, and a Groq API key.

```bash
uv sync                    # creates .venv with Python 3.12 and installs everything
cp .env.example .env       # then fill in your Postgres and Groq details
```

(Without uv: `python -m venv .venv`, activate it, then `pip install -r requirements.txt`.)

Put `restaurants.csv` and `orders.csv` in `data/`.

## Run

```bash
uv run python scripts/ingest_data.py     # create tables, load data, create read-only role
```

Open `aai_food_okf_demo.ipynb` in VS Code, select the `.venv` kernel, and **Run All**.

## Project layout

```
data/                   restaurants.csv, orders.csv
okf/aai-food/           the OKF bundle (tables, metrics, playbooks, glossary)
scripts/ingest_data.py  loads the CSVs into Postgres
okf_agent.py            bundle loader/validator, graph, LLM helper, the two agents
aai_food_okf_demo.ipynb the demo notebook
```

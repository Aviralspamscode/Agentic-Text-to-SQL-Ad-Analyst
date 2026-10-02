import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.graph import run_question

q = (
    "On multi-touch journeys, which named contextual segment (exclude other) "
    "has the largest last-touch over-credit versus linear?"
)
r = run_question(q)
print("SQL:", r.get("sql"))
print(r.get("result_df"))
print("ANSWER:", r.get("answer"))

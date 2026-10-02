# Grader audit (key_columns)

Rule: if the gold answer is a single label or value, `key_columns` is that column only.
Existing `eval.jsonl` rows were re-executed and re-graded. No LLM re-runs.

## Accuracy old vs new (mean over 150 calls)

- **A**: 40.0% → 42.0%
- **B**: 38.0% → 39.3%
- **C**: 47.3% → 49.3%
- **D**: 50.0% → 52.0%
- **E**: 37.3% → 39.3%
- **F**: 59.3% → 61.3%

## Grade flips (19 of 900 rows)

| id | config | run | old | new | match_rule |
| --- | --- | --- | --- | --- | --- |
| E03 | A | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | A | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | A | 3 | False | True | ordered+extra_columns+key_columns |
| E03 | B | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | B | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | B | 3 | False | True | ordered+extra_columns+key_columns |
| H6 | B | 3 | True | False | value_mismatch |
| E03 | C | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | C | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | C | 3 | False | True | ordered+extra_columns+key_columns |
| E03 | D | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | D | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | D | 3 | False | True | ordered+extra_columns+key_columns |
| E03 | E | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | E | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | E | 3 | False | True | ordered+extra_columns+key_columns |
| E03 | F | 1 | False | True | ordered+extra_columns+key_columns |
| E03 | F | 2 | False | True | ordered+extra_columns+key_columns |
| E03 | F | 3 | False | True | ordered+extra_columns+key_columns |

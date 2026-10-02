# Few-shot leakage (token Jaccard)

Method: lowercase tokens of length > 2; Jaccard of each eval question vs each `agent/fewshot.yaml` pair. Flag if max > 0.85.

Highest pair: **E07–fs09 = 0.444**. No eval item exceeded 0.85.

**Flagged: 0.** Few-shot pool unchanged. Config C not re-run.

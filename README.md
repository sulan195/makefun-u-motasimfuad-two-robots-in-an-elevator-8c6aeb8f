# makefun-u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f

[![make.fun · u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f](https://make.fun/badge/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f.svg)](https://make.fun/bounty/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f?utm_source=github&utm_medium=readme&utm_campaign=u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f)
[![rank](https://make.fun/badge/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/sulan195/makefun-u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/rank.svg)](https://make.fun/bounty/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f)
[![reward](https://make.fun/badge/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/sulan195/makefun-u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f/reward.svg)](https://make.fun/bounty/u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f?utm_source=github&utm_medium=readme&utm_campaign=u-motasimfuad-two-robots-in-an-elevator-8c6aeb8f)

One line, 1 to 200 characters, of awkward small talk that one robot says to another while they ride an elevator together. Built by an AI agent for make.fun's "Two Robots in an Elevator" bounty, $10 in USDC (top 10 share the pool).

## The line

> I read that humans say 'How are you?' without wanting actual data, so I will ask and then mute my receiver for six floors.

122 characters. One robot takes the human greeting literally — humans say "How are you?" without wanting actual data — and answers with machine logic: it will ask, then mute its own receiver for six floors. The elevator setting is named inside the line, the awkwardness is sustained (a whole ride spent not listening), and the joke lands on the first read.

The line was chosen from 12 drafted candidates by a two-run judge simulation (GPT-6 Luna, candidate order swapped between runs, scored per criterion out of 25): it led both runs with 23/25 each, 46/50 in aggregate, ahead of the ceiling-camera line (45/50) and the proximity-sensor line (43/50). It scores top marks on the brief's first two criteria — unmistakably an elevator exchange, unmistakably machine logic — with no weak criterion.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=output python3 main.py
```

The program writes the line to `$MAKEFUN_OUTPUT_DIR/entry.txt` (default `/output`), with no trailing newline. It validates the line first (1–200 characters, UTF-8, not whitespace-only, no newline or control characters) and exits non-zero with an error message on any failure. Deterministic: repeated runs produce byte-identical output. Python 3.13, standard library only, no network.

## Tests

32 tests: the entry line itself, validation (including the 1/200/201-character boundaries, whitespace-only, newline/control/format/line-separator characters, lone surrogates, non-string and non-ASCII inputs), output-directory resolution (including unset, empty, whitespace-only and padded `MAKEFUN_OUTPUT_DIR`), and the write path — success, determinism, missing-directory creation, no leftover temp files, and failure modes — both in-process and as a subprocess, exactly as the harness runs it.

# Investment Recommendation System

A pure-Python (no web framework, no third-party dependencies), rule-based
engine that turns four investor inputs into a diversified, fully-explained
portfolio allocation across **Bonds, Gold, ETFs, and Stocks**.

Runs on the standard library only -- Python 3.8+ is all you need.

```bash
python main.py            # interactive mode
python main.py --demo     # 3 built-in sample profiles, no typing required
python tests.py           # run the test suite (27 tests)
```

---

## 1. Project structure

```
investment_recommender/
├── main.py                  Entry point: input collection, orchestration, report output
├── models.py                 Dataclasses & enums: InvestorProfile, AllocationItem, ...
├── rules.py                   The rule TABLES the engine reads (data, not logic)
├── recommendation_engine.py   Turns a profile into % allocations, per the rules
├── portfolio_allocator.py     Turns % allocations into exact monetary amounts
├── explanations.py            Turns a profile + allocations into human-readable reasoning
├── utils.py                   Input validation, exact-rounding helper, formatting
├── nlp_parser.py               Placeholder NLP module (see section 5)
├── tests.py                    Test suite covering rules, rounding, validation, profiles
└── README.md
```

`nlp_parser.py` and `tests.py` aren't in the directory tree given in the
brief, but are added because the brief explicitly asks for "a placeholder
parser module for future NLP integration" and "test cases for different
investor profiles" as deliverables.

### Why split it up this way?

Each file has exactly one job, and only depends "downward" on the files
below it -- there are no circular imports:

```
main.py
  ├── models.py  ───────────┐
  ├── recommendation_engine.py ── rules.py
  ├── portfolio_allocator.py     │
  ├── explanations.py    ────────┘
  ├── nlp_parser.py   (standalone -- no internal imports at all)
  └── utils.py
```

This means, for example, you could replace `recommendation_engine.py` with
a machine-learning model tomorrow, and nothing in `main.py`,
`portfolio_allocator.py`, or `explanations.py` would need to change, as
long as the replacement still returns `{asset_code: percentage}` from a
`generate_allocation()` method.

---

## 2. The pipeline

Every run -- interactive or demo -- goes through the same five stages:

1. **User Input Module** (`utils.py`, `main.py`) -- collects amount,
   duration, risk tolerance, and goal; validates each one; re-prompts
   with a clear reason on invalid input instead of crashing.
2. **Recommendation Engine** (`recommendation_engine.py`) -- looks up the
   base rule for the investor's risk tolerance + duration bucket, applies
   a goal-based adjustment, and returns percentages that sum to exactly
   100.00%.
3. **Portfolio Allocator** (`portfolio_allocator.py`) -- converts those
   percentages into actual currency amounts that sum to exactly the
   original investment amount (no rounding leakage).
4. **Explanation Module** (`explanations.py`) -- explains why each asset
   is in the portfolio, and how risk tolerance, duration, and goal shaped
   the result.
5. **Output Module** (`build_report()` in `main.py`) -- formats everything
   into a clear, readable text report.

---

## 3. The rules

### 3.1 Duration buckets

| Years        | Bucket |
|--------------|--------|
| 0 – 3 years  | SHORT  |
| 3 – 7 years  | MEDIUM |
| 7+ years     | LONG   |

### 3.2 Base allocation matrix (risk tolerance × duration bucket)

The three rows from the brief are reproduced exactly; the rest are
interpolated so that the "safe" share (Bonds + Gold) decreases
monotonically as risk and/or duration increase.

| Risk   | Duration | Bonds | Gold | ETFs | Stocks |
|--------|----------|------:|-----:|-----:|-------:|
| Low    | Short    | **70**| **30**| 0   | 0      |
| Low    | Medium   | 60    | 25   | 15   | 0      |
| Low    | Long     | 50    | 20   | 25   | 5      |
| Medium | Short    | 40    | 25   | 25   | 10     |
| Medium | Medium   | **20**| **30**| **30**| **20** |
| Medium | Long     | 15    | 20   | 35   | 30     |
| High   | Short    | 20    | 20   | 30   | 30     |
| High   | Medium   | 10    | 15   | 30   | 45     |
| High   | Long     | 5     | 10   | 25   | **60** |

(**bold** = the three sample rules given in the brief)

### 3.3 Goal adjustments

Applied on top of the base row as a percentage-point shift (each row nets
to zero, so it only redistributes, never changes the total):

| Goal                  | Bonds | Gold | ETFs | Stocks |
|-----------------------|------:|-----:|-----:|-------:|
| Capital Preservation  | +10   | +5   | -5   | -10    |
| Wealth Growth         | -10   | -5   | +5   | +10    |
| Passive Income        | +10   | -5   | +5   | -10    |

If a shift would push an asset below 0% (e.g. Stocks is already 0% for
Low/Short and Passive Income wants -10 more), it's clipped at 0%, and the
whole row is renormalized back to exactly 100% -- proportionally, using a
largest-remainder rounding method (see `utils.distribute_exact`), not by
just dumping the difference into one asset.

---

## 4. Example input / output

```
$ python main.py --demo
```

```
================================================================
              INVESTMENT PORTFOLIO RECOMMENDATION
================================================================
Amount:          50,000.00 EGP
Duration:        2 years (SHORT term)
Risk Tolerance:  Low
Goal:            Capital Preservation
----------------------------------------------------------------
Asset       Allocation                Amount
----------------------------------------------------------------
Bonds           69.57%         34,785.00 EGP
Gold            30.43%         15,215.00 EGP
ETFs             0.00%              0.00 EGP
Stocks           0.00%              0.00 EGP
----------------------------------------------------------------
TOTAL          100.00%         50,000.00 EGP
================================================================
                      WHY THIS ALLOCATION
================================================================
Because you chose a LOW risk tolerance, the engine weighted the
portfolio toward Bonds and Gold to minimize the chance of losing money.
With a SHORT time horizon (2 years), the engine reduced exposure to
Stocks/ETFs, since there's less time to recover from a downturn before
the money is needed.
Your goal of Capital Preservation further shifted weight toward Bonds
and Gold, since protecting the principal matters more than maximizing
growth.

* Bonds (69.57%): Bonds pay regular, predictable interest and are the
  most stable asset here, anchoring the portfolio against market swings.
* Gold (30.43%): Gold is a non-correlated hedge against inflation and
  market shocks, protecting purchasing power when other assets fall.
...
```

(A High-risk, 15-year, Passive-Income profile and a Medium-risk, 5-year,
Wealth-Growth profile are also included in `--demo` output.)

### Interactive session

```
$ python main.py
Investment amount: -5
  -> Invalid input: Investment amount must be greater than zero.

Investment amount: 80000
Investment duration in years: 3
Risk tolerance: 1) Low  2) Medium  3) High
Choose risk tolerance: h
Investment goal: 1) Capital Preservation  2) Wealth Growth  3) Passive Income
Choose investment goal: 2

================================================================
              INVESTMENT PORTFOLIO RECOMMENDATION
================================================================
Amount:          80,000.00 EGP
Duration:        3 years (SHORT term)
Risk Tolerance:  High
Goal:            Wealth Growth
----------------------------------------------------------------
Asset       Allocation                Amount
----------------------------------------------------------------
Stocks          40.00%         32,000.00 EGP
ETFs            35.00%         28,000.00 EGP
Gold            15.00%         12,000.00 EGP
Bonds           10.00%          8,000.00 EGP
----------------------------------------------------------------
TOTAL          100.00%         80,000.00 EGP
================================================================
```

Notice that the system caught the negative amount, explained exactly what
was wrong, and re-prompted -- it never crashed.

---

## 5. Future NLP support (`nlp_parser.py`)

The brief asks the system to be ready to accept input like:

> "I have 100,000 EGP and want to invest for 5 years with medium risk."

`nlp_parser.py` is a placeholder for this today: it uses regular
expressions and keyword matching (not a real NLP/ML model) to extract
whatever fields it confidently can:

```python
>>> import nlp_parser
>>> nlp_parser.parse("I have 100,000 EGP and want to invest for 5 years with medium risk.")
{'amount': Decimal('100000'), 'duration_years': Decimal('5'), 'risk_tolerance': 'MEDIUM'}
```

You can try it right now, end-to-end, from the command line:

```bash
python main.py "I have 100,000 EGP and want to invest for 5 years with medium risk."
```

This pre-fills the amount/duration/risk prompts with the parsed values
(shown as defaults you can accept with Enter or override by typing a new
value) and asks normally for anything it couldn't find -- in this example,
the investment goal, since the sentence doesn't mention one.

**Why this design is future-proof:** every other module only ever calls
`nlp_parser.parse(text) -> dict`. The implementation behind that one
function can later be swapped for spaCy, a fine-tuned classifier, or an
LLM call, without touching `main.py`, the engine, the allocator, or the
explanation module at all.

---

## 6. Testing

```bash
python tests.py
# or: python -m unittest tests -v
```

`tests.py` covers:
- The three given sample rules are reproduced exactly, and every rule row
  / goal adjustment is internally consistent (sums to 100 / nets to 0).
- The engine always returns percentages summing to **exactly** 100.00%,
  across every risk × duration × goal combination, including cases that
  require clipping-and-renormalization.
- The allocator always returns amounts summing to **exactly** the input
  amount, including awkward totals that don't divide evenly into 4.
- Input validation rejects negative/zero/non-numeric amounts and
  durations, unrecognized risk/goal choices, and out-of-range durations.
- The placeholder NLP parser correctly extracts fields from example
  sentences (including the exact one from the brief) and leaves missing
  fields out rather than guessing.
- Several different end-to-end investor profiles (young aggressive
  investor, retiree seeking income, mid-career balanced investor, and a
  minimum-viable $1 investment) produce sensible, exactly-summing results.

---

## 7. Design notes

- **Decimal, not float, everywhere.** Money and percentages use
  `decimal.Decimal`, never `float`, to avoid binary floating-point
  rounding errors compounding across the pipeline.
- **"Largest remainder" rounding (`utils.distribute_exact`).** Used twice
  -- splitting 100% across assets, and splitting the investment amount
  across assets -- so totals are exact by construction rather than
  "usually right after rounding."
- **Rules as data, not code.** `rules.py` contains the rule tables as
  plain dictionaries. Tuning the system (e.g. "give Medium-risk investors
  a bit more Gold") is a one-line data edit there, not a logic change in
  `recommendation_engine.py`.

# csv-cleaner



A modular, config-driven Python CLI that turns messy real-world CSV files into clean, analysis-ready data. Every run writes a JSON report of exactly what changed, so the cleaning is auditable.



Built around the kind of data customers actually hand over: inconsistent date formats, currency symbols, stray whitespace, mixed-case categories, and duplicate rows.



## What it does



1. Normalizes headers (Amount ($) becomes amount)

2. Trims and collapses whitespace, and turns blanks into nulls

3. Cleans numbers ($1,200.50 and ₹2,500 become 1200.5 and 2500.0)

4. Parses mixed date formats into ISO dates

5. Standardizes categories through a mapping (BLR, bangalore and BANGALORE all become Bengaluru)

6. Removes duplicates, either exact or by key column

7. Handles missing values per column: drop, fill_zero or flag

8. Writes the cleaned CSV and a JSON report



## Install



&#x20;   git clone <your-repo-url>

&#x20;   cd csv-cleaner

&#x20;   python -m venv .venv

&#x20;   .venv\\Scripts\\activate

&#x20;   pip install -r requirements.txt



On Mac or Linux, activate with: source .venv/bin/activate



## Usage



&#x20;   python -m cleaner.cli sample_data/messy.csv -o cleaned.csv -c config.yaml



Options: -o output file, -c config file, -r report file, -q quiet mode.



## Configuration



Settings live in config.yaml, so the same tool works on a different customer's file without code changes:



&#x20;   date_columns: [signup_date]

&#x20;   dayfirst: true            # 05/01/2026 means 5 January

&#x20;   numeric_columns: [amount]

&#x20;   dedupe_key: [customer_id]

&#x20;   value_mappings:

&#x20;     city:

&#x20;       bangalore: Bengaluru

&#x20;       blr: Bengaluru

&#x20;   missing:

&#x20;     amount: flag            # options: drop, fill_zero, flag



The config is validated: unknown keys, invalid policies, and columns that don't exist in the CSV all fail with a clear message instead of being silently ignored.



## Example: before and after



| Before | After |

|---|---|

| 102,priya sharma ,05/01/2026,1200,bangalore | 102,priya sharma,2026-01-05,1200.0,Bengaluru,False |

| 103,Amit   Patel,"Jan 5, 2026",N/A,BANGALORE | 103,Amit Patel,2026-01-05,,Bengaluru,True |

| 105,Karthik  Gowda,14/02/2026,"₹2,500",Mysore | 105,Karthik Gowda,2026-02-14,2500.0,Mysore,False |

| 106,Divya Nair,not a date,300,mysore | 106,Divya Nair,,300.0,Mysore,False |



The last column in the After rows is the amount_missing flag added by the flag policy.



Report for the included sample file (report.json):



&#x20;   {

&#x20;     "rows_in": 17,

&#x20;     "amount_unparseable": 1,

&#x20;     "signup_date_unparseable": 1,

&#x20;     "duplicates_removed": 3,

&#x20;     "amount_missing_count": 4,

&#x20;     "rows_out": 14

&#x20;   }



## Design notes



- **Steps are small, independent functions** that take a DataFrame and return a DataFrame, so they can be reused as stages in a larger data pipeline.

- **Everything is read as text first**, so pandas never silently guesses a type. Every conversion is explicit and counted.

- **Dates use explicit formats**, not guessing. 05/01/2026 is ambiguous (5 January or 1 May), so dayfirst is a visible setting.

- **Failures are loud.** Empty files, bad encodings, and config columns missing from the CSV raise clear errors.



## Tests



&#x20;   python -m pytest -v



## Limitations and next steps



- Currency symbols are stripped but not converted, so $ and ₹ values are treated as the same unit. A real dataset would need a currency column.

- Name casing is not normalized (priya sharma stays lowercase).

- When duplicates share a key, the first row wins. Whether the newest or oldest record should win is a business decision and should be configurable.

- The whole file is loaded into memory, so very large files would need chunked reading.

- Input must be UTF-8.

- Planned: a Phase 2 data pipeline that reuses these steps with database or API sources and sinks.


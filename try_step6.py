import logging
from cleaner.pipeline import run

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

report = run("sample_data/messy.csv", "cleaned.csv", "config.yaml")
print(report)
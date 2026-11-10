import argparse
import logging
import sys

from .pipeline import run


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Clean a messy CSV file.")
    p.add_argument("input", help="path to the messy CSV")
    p.add_argument("-o", "--output", default="cleaned.csv", help="cleaned CSV to write")
    p.add_argument("-c", "--config", default="config.yaml", help="YAML config file")
    p.add_argument("-r", "--report", default="report.json", help="JSON report to write")
    p.add_argument("-q", "--quiet", action="store_true", help="only show warnings")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        run(args.input, args.output, args.config, args.report)
    except FileNotFoundError as e:
        print(f"Error: file not found: {e.filename}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
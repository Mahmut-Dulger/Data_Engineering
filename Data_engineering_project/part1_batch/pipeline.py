# Part 1: runs the batch pipeline for the Nashville housing data.
# Steps: read -> validate -> process -> backup check -> write
# Run with: python part1_batch/pipeline.py
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import reader
import validator
import processor
import writer

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("part1")


def run():
    log.info("--- Part 1 batch pipeline start ---")
    df = reader.read()
    rows_in = len(df)

    clean, rejected = validator.validate(df)
    writer.write_rejected(rejected)          # keep the bad rows for inspection

    processed = processor.process(clean)
    processed = validator.backup_check(processed)
    path = writer.write(processed)

    writer.write_report({
        "source_file": os.path.basename(config.find_input()),
        "rows_in": rows_in,
        "rows_rejected": len(rejected),
        "rows_out": len(processed),
        "output_file": os.path.basename(path),
    })
    log.info("--- Done -> %s ---", path)
    return path


if __name__ == "__main__":
    run()

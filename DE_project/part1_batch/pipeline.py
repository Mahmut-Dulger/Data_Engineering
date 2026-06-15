# Part 1: runs the batch pipeline for the Nashville housing data.
# Steps: read -> validate -> process -> backup check -> write
# Run with: python part1_batch/pipeline.py
import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import reader
import validator
import processor
import writer

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("part1")


def run():
    log.info("--- Part 1 batch pipeline start ---")
    df = reader.read()
    df = validator.validate(df)
    df = processor.process(df)
    df = validator.backup_check(df)
    path = writer.write(df)
    log.info("--- Done -> %s ---", path)
    return path


if __name__ == "__main__":
    run()

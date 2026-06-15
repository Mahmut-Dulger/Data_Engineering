# Part 2: runs the pipeline on one dropped file, then moves it to archive/
# (or archive/errors/ if it failed). Called by watcher.py and the Airflow DAG,
# but you can also run it by hand: python part2_realtime/pipeline.py <file>
import os
import sys
import shutil
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from . import config, reader, validator, processor, writer
except ImportError:
    import config, reader, validator, processor, writer

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("part2")


def _move(path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    if os.path.exists(path):
        shutil.move(path, os.path.join(dest_dir, os.path.basename(path)))


def process_file(path):
    log.info("--- Part 2 pipeline start: %s ---", os.path.basename(path))
    try:
        df = reader.read(path)
        rows_in = len(df)

        clean, rejected = validator.validate(df)
        writer.write_rejected(rejected, path)    # keep the bad rows for inspection

        processed = processor.process(clean)
        processed = validator.backup_check(processed)
        out = writer.write(processed, path)

        writer.write_report(path, {
            "source_file": os.path.basename(path),
            "rows_in": rows_in,
            "rows_rejected": len(rejected),
            "rows_out": len(processed),
            "output_file": os.path.basename(out),
        })
        _move(path, config.ARCHIVE_DIR)
        log.info("--- Done -> %s ---", out)
        return out
    except Exception as e:
        log.error("Failed on %s: %s", path, e)
        _move(path, config.ERROR_DIR)
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        print("Usage: python part2_realtime/pipeline.py <file>")

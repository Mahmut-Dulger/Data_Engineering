# Watches the input folder and runs the pipeline when a file shows up.
# Run with: python part2_realtime/watcher.py  (then drop a file into input/)
import os
import sys
import time
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("watcher")


def watch(interval=2):
    os.makedirs(config.INPUT_DIR, exist_ok=True)
    log.info("Watching %s (drop a .csv or .xlsx here)", config.INPUT_DIR)
    seen_sizes = {}
    while True:
        for name in sorted(os.listdir(config.INPUT_DIR)):
            path = os.path.join(config.INPUT_DIR, name)
            if not os.path.isfile(path) or not name.lower().endswith(config.ALLOWED_EXTENSIONS):
                continue
            # only process once the size stops changing (file finished copying)
            size = os.path.getsize(path)
            if seen_sizes.get(path) == size:
                pipeline.process_file(path)
                seen_sizes.pop(path, None)
            else:
                seen_sizes[path] = size
        time.sleep(interval)


if __name__ == "__main__":
    watch()

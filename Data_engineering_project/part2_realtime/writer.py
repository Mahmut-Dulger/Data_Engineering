# Saves the result locally (+ parquet) and uploads to Azure. Also saves the
# rejected rows and a small run report.
import os

try:
    from . import config
except ImportError:
    import config
from storage import save_local, upload_to_azure, save_rejected, save_run_report


def write(df, source_name):
    name = "processed_" + os.path.splitext(os.path.basename(source_name))[0]
    path = save_local(df, config.OUTPUT_DIR, name)
    upload_to_azure(path)
    return path


def write_rejected(df, source_name):
    base = os.path.splitext(os.path.basename(source_name))[0]
    return save_rejected(df, config.OUTPUT_DIR, base)


def write_report(source_name, stats):
    base = os.path.splitext(os.path.basename(source_name))[0]
    return save_run_report(config.OUTPUT_DIR, base, stats)

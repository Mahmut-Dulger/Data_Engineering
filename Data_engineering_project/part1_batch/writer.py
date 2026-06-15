# Saves the result locally (+ parquet) and uploads to Azure. Also saves the
# rejected rows and a small run report.
try:
    from . import config
except ImportError:
    import config
from storage import save_local, upload_to_azure, save_rejected, save_run_report


def write(df):
    path = save_local(df, config.OUTPUT_DIR, "nashville_processed")
    upload_to_azure(path)
    return path


def write_rejected(df):
    return save_rejected(df, config.OUTPUT_DIR, "nashville")


def write_report(stats):
    return save_run_report(config.OUTPUT_DIR, "nashville", stats)

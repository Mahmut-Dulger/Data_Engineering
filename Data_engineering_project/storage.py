# Output helpers used by both pipelines: save locally (CSV + Parquet), save
# rejected rows, write a small run report, and upload to Azure.
import os
import json
import logging
from datetime import datetime

log = logging.getLogger("storage")

# the azure sdk logs every HTTP request/response at INFO, which is very noisy
logging.getLogger("azure").setLevel(logging.WARNING)


# read a .env file if one exists, so we don't depend on python-dotenv
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env()


def save_local(df, output_dir, name):
    os.makedirs(output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(output_dir, f"{name}_{stamp}.csv")
    df.to_csv(csv_path, index=False)
    log.info("Saved %d rows -> %s", len(df), csv_path)
    # also keep a parquet copy (smaller, keeps data types); skip if pyarrow is missing
    try:
        df.to_parquet(csv_path.replace(".csv", ".parquet"), index=False)
    except Exception as e:
        log.warning("Could not write parquet (%s)", e)
    return csv_path


def save_rejected(df, output_dir, base):
    # write the rows that failed validation, with their reason, to output/rejected/
    if df is None or len(df) == 0:
        return None
    rej_dir = os.path.join(output_dir, "rejected")
    os.makedirs(rej_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(rej_dir, f"{base}_rejected_{stamp}.csv")
    df.to_csv(path, index=False)
    log.info("Saved %d rejected row(s) -> %s", len(df), path)
    return path


def save_run_report(output_dir, base, stats):
    # small JSON summary of the run (row counts, files, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    stats = {"run_at": datetime.now().isoformat(timespec="seconds"), **stats}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"{base}_report_{stamp}.json")
    with open(path, "w") as f:
        json.dump(stats, f, indent=2, default=str)
    log.info("Wrote run report -> %s", path)
    return path


def upload_to_azure(path):
    conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("AZURE_BLOB_CONTAINER", "processed-data")

    # no connection string set, so just keep the local file
    if not conn:
        log.warning("Azure not configured - skipping upload (local copy is saved).")
        return

    try:
        from azure.storage.blob import BlobServiceClient

        # short timeout so it doesn't hang when Azurite/Azure isn't running
        service = BlobServiceClient.from_connection_string(
            conn, retry_total=0, connection_timeout=5, read_timeout=5)
        try:
            service.create_container(container)
        except Exception:
            pass  # container already exists

        blob_name = os.path.basename(path)
        with open(path, "rb") as f:
            service.get_blob_client(container, blob_name).upload_blob(f, overwrite=True)
        log.info("Uploaded %s -> Azure container '%s'", blob_name, container)
    except Exception as e:
        log.warning("Azure upload failed (local copy is safe): %s", e)

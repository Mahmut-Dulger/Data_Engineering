# Output helpers used by both pipelines: save to a local folder and to Azure.
import os
import logging
from datetime import datetime

log = logging.getLogger("storage")


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
    path = os.path.join(output_dir, f"{name}_{datetime.now():%Y%m%d_%H%M%S}.csv")
    df.to_csv(path, index=False)
    log.info("Saved %d rows -> %s", len(df), path)
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

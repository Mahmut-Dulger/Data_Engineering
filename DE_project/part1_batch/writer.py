# Saves the result locally and uploads it to Azure.
try:
    from . import config
except ImportError:
    import config
from storage import save_local, upload_to_azure


def write(df):
    path = save_local(df, config.OUTPUT_DIR, "nashville_processed")
    upload_to_azure(path)
    return path

# Saves the result locally and uploads it to Azure.
import os

try:
    from . import config
except ImportError:
    import config
from storage import save_local, upload_to_azure


def write(df, source_name):
    name = "processed_" + os.path.splitext(os.path.basename(source_name))[0]
    path = save_local(df, config.OUTPUT_DIR, name)
    upload_to_azure(path)
    return path

import os
from botocore.exceptions import BotoCoreError, ClientError
import openfinance.constants as ct


def upload_file_to_s3(
        file_path: str,
        bucket_name: str,
        object_name: str = None) -> bool:
    """
    Upload a file to an S3 bucket.

    Args:
        file_path (str): Path to the file to upload.
        bucket_name (str): Name of the S3 bucket.
        object_name (str, optional): S3 object name.
        If not specified, file_path's basename is used.

    Returns:
        bool: True if file was uploaded, else False.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        ct.s3_client.upload_file(file_path, bucket_name, object_name)
    except (BotoCoreError, ClientError) as e:
        print(f"Failed to upload {file_path} to S3: {e}")
        return False
    return True

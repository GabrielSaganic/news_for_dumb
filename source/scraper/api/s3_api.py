import os

import boto3
from botocore.exceptions import ClientError
from log_utilis import make_logger

logger = make_logger()

SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY", "")
ACCESS_KEY = os.environ.get("ACCESS_KEY", "")


class S3API:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY
        )

    def upload_file_s3(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket"""

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        try:
            self.s3_client.upload_file(file_name, bucket, object_name)
            logger.info("Database successfully uploaded.")
        except ClientError as e:
            logger.error(f"Error uploading file from S3: {e}")
            return False
        return True

    def download_from_s3(self, bucket_name, object_name, local_file_path):
        """Download file from S3 bucket"""

        try:
            self.s3_client.download_file(bucket_name, object_name, local_file_path)
            logger.info("Database successfully downloaded.")

        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            return False
        return True

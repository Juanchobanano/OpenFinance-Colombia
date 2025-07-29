import boto3
from dotenv import dotenv_values

config = dotenv_values(".env")

AWS_ACCESS_KEY = config.get("AWS_ACCESS_KEY")
AWS_PRIVATE_ACCESS_KEY = config.get("AWS_PRIVATE_ACCESS_KEY")
REGION_NAME = "us-east-1"
TEXTRACT_BUCKET_NAME = "openfinance-colombia-textract-bucket"
TEMP_FOLDER = "tmp"
MAX_PDF_CHUNK_SIZE = 1

# Define AWS credentials as a dictionary
aws_credentials = {
    "aws_access_key_id": AWS_ACCESS_KEY,
    "aws_secret_access_key": AWS_PRIVATE_ACCESS_KEY,
    "region_name": REGION_NAME
}

# Initialize AWS Textract client
textract_client = boto3.client(
    'textract',
    **aws_credentials
)

s3_client = boto3.client(
    's3',
    **aws_credentials
)

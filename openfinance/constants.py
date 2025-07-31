import boto3
from dotenv import dotenv_values

config = dotenv_values(".env")

AWS_ACCESS_KEY = config.get("AWS_ACCESS_KEY")
AWS_PRIVATE_ACCESS_KEY = config.get("AWS_PRIVATE_ACCESS_KEY")
REGION_NAME = "us-east-1"
TEXTRACT_BUCKET_NAME = "openfinance-colombia-textract-bucket"
TEMP_FOLDER = "tmp"
MAX_PDF_CHUNK_SIZE = 1
OUTPUT_FOLDER = "output"
NU_BANK_PASSWORD = config.get("NU_BANK_PASSWORD")
ITAU_PASSWORD = config.get("ITAU_PASSWORD")

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

month_map = {
    'ENE': 'JAN', 'FEB': 'FEB', 'MAR': 'MAR', 'ABR': 'APR', 'MAY': 'MAY',
    'JUN': 'JUN', 'JUL': 'JUL', 'AGO': 'AUG', 'SEP': 'SEP',
    'OCT': 'OCT', 'NOV': 'NOV', 'DIC': 'DEC'
}

import openfinance.parsers.common.utils as ut
from openfinance.parsers.common.textract import analyze_documents_s3
from openfinance.parsers.common.aws_utils import upload_file_to_s3
import logging
import openfinance.constants as ct
import os
import pandas as pd
from openfinance.parsers.preprocess.nu_bank import (
    preprocess_nu_bank, concatenate_csv_to_df)

logger = logging.getLogger(__name__)


def analyze_first_page(
        csv_path: str) -> dict:
    """
    Analyze the first page of the Nu Bank PDF file.
    """
    return


def parse_csv_to_pandas(
        csv_path: str) -> pd.DataFrame:
    """
    Parse the CSV file to a pandas DataFrame.
    """
    return pd.read_csv(csv_path)


def parse_nubank_pdf(
        input_path: str,
        password: str) -> dict:
    """
    Parse the Nu Bank PDF file.
    """

    # Decrypt the PDF file
    logger.info(f"Decrypting the PDF file: {input_path}")
    decrypted_output_path = ut.decrypt_pdf_file(
        input_pdf=input_path,
        password=password
    )

    # Split the PDF file into pages
    logger.info(f"Splitting the PDF file into pages: {decrypted_output_path}")
    chunks_paths = ut.split_pdf_into_chunks(
        input_pdf=decrypted_output_path
    )

    # Upload chunks to S3
    logger.info("Uploading chunks to S3 ...")
    for chunk_path in chunks_paths:
        upload_file_to_s3(
            file_path=chunk_path,
            bucket_name=ct.TEXTRACT_BUCKET_NAME
        )

    # Get documents keys (S3 objects)
    document_keys = [
        os.path.basename(chunk_path) for chunk_path in chunks_paths]

    # Analyze chunks
    logger.info("Analyzing chunks ...")
    csv_paths = analyze_documents_s3(
        bucket_name=ct.TEXTRACT_BUCKET_NAME,
        document_keys=document_keys,
        output_path=ct.TEMP_FOLDER
    )
    logger.info(f"CSV paths: {csv_paths}")

    # Preprocess CSV files
    logger.info("Preprocessing CSV files ...")
    df = concatenate_csv_to_df(csv_files=csv_paths)
    df = preprocess_nu_bank(df)
    df.to_csv(
        f"{ct.OUTPUT_FOLDER}/{os.path.basename(input_path)}.csv", index=False)
    output_csv_path = f"{ct.OUTPUT_FOLDER}/{os.path.basename(input_path)}.csv"
    logger.info(
        f"CSV file saved to {output_csv_path}"
    )

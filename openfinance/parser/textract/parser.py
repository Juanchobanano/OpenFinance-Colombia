import openfinance.parser.textract.utils as ut
from openfinance.parser.textract.textract import analyze_documents_s3
from openfinance.parser.textract.aws_utils import upload_file_to_s3
import logging
import openfinance.constants as ct
import os


logger = logging.getLogger(__name__)


class FinancialStatementTextractParser:
    """
    A class to parse financial statements using AWS Textract.
    """

    def __init__(
            self,
            input_path: str,
            password: str,
            bank_name: str,
            textract_bucket_name: str = ct.TEXTRACT_BUCKET_NAME,
            temp_folder: str = ct.TEMP_FOLDER,
            output_folder: str = ct.OUTPUT_FOLDER):
        """
        Initialize the FinancialStatementTextract   Parser.

        Args:
            input_path (str): Path to the encrypted PDF file
            password (str): Password to decrypt the PDF
            bank_name (str): Name of the bank
            textract_bucket_name (str): Name of the S3 bucket for Textract
            temp_folder (str): Path to the temporary folder
            output_folder (str): Path to the output folder
        """
        self.input_path = input_path
        self.password = password
        self.bank_name = bank_name
        self.textract_bucket_name = textract_bucket_name
        self.temp_folder = temp_folder
        self.output_folder = output_folder
        self.decrypted_output_path = None
        self.chunks_paths = []
        self.csv_paths = []
        self.output_csv_path = None

    def decrypt_pdf(self) -> str:
        """
        Decrypt the PDF file.

        Returns:
            str: Path to the decrypted PDF file
        """
        logger.info(f"Decrypting the PDF file: {self.input_path}")
        logger.info(f"Password: {self.password}")
        self.decrypted_output_path = ut.decrypt_pdf_file(
            input_pdf=self.input_path,
            password=self.password
        )
        return self.decrypted_output_path

    def split_pdf_into_chunks(self) -> list:
        """
        Split the decrypted PDF file into pages.

        Returns:
            list: List of paths to the PDF chunks
        """
        logger.info(
            f"Splitting the PDF file into pages: {self.decrypted_output_path}")
        self.chunks_paths = ut.split_pdf_into_chunks(
            input_pdf=self.decrypted_output_path
        )
        return self.chunks_paths

    def upload_chunks_to_s3(self) -> None:
        """
        Upload PDF chunks to S3 for Textract processing.
        """
        logger.info("Uploading chunks to S3 ...")
        for chunk_path in self.chunks_paths:
            upload_file_to_s3(
                file_path=chunk_path,
                bucket_name=self.textract_bucket_name
            )

    def get_document_keys(self) -> list:
        """
        Get the S3 document keys for the uploaded chunks.

        Returns:
            list: List of S3 document keys
        """
        return [
            os.path.basename(chunk_path) for chunk_path in self.chunks_paths]

    def analyze_chunks(self) -> list:
        """
        Analyze the PDF chunks using AWS Textract.

        Returns:
            list: List of paths to the generated CSV files
        """
        logger.info("Analyzing chunks ...")
        document_keys = self.get_document_keys()
        self.csv_paths = analyze_documents_s3(
            bucket_name=self.textract_bucket_name,
            document_keys=document_keys,
            output_path=self.temp_folder
        )
        logger.info(f"CSV paths: {self.csv_paths}")
        return self.csv_paths

    def parse(self) -> dict:
        """
        Parse the Nu Bank PDF file through the complete pipeline.

        Returns:
            dict: Dictionary containing parsing results and file paths
        """
        try:
            # Step 1: Decrypt PDF
            self.decrypt_pdf()

            # Step 2: Split into chunks
            self.split_pdf_into_chunks()

            # Step 3: Upload to S3
            self.upload_chunks_to_s3()

            # Step 4: Analyze with Textract
            self.analyze_chunks()

            # Step 5: Preprocess and save final CSV
            # self.preprocess_csv_files()

            return {
                'success': True,
                'input_path': self.input_path,
                'decrypted_path': self.decrypted_output_path,
                'chunks_paths': self.chunks_paths,
                'csv_paths': self.csv_paths
            }

        except Exception as e:
            logger.error(f"Error parsing Financial Statement PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_path': self.input_path
            }

import openfinance.parsers.common.utils as ut
from openfinance.parsers.common.textract import textract_pdf
import logging

logger = logging.getLogger(__name__)


def parse_itau_pdf(
        input_path: str,
        decrypted_output_path: str,
        textract_output_path: str,
        password: str) -> dict:
    pass

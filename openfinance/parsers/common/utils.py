from PyPDF2 import PdfReader, PdfWriter
import os
import logging
import openfinance.constants as ct

logger = logging.getLogger(__name__)


def read_pdf(pdf_path: str) -> PdfReader:
    """
    Read a PDF file.
    """
    return PdfReader(pdf_path)


def write_pdf(
        pdf_path: str,
        reader: PdfReader):
    """
    Write a PDF file.
    """
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(pdf_path, "wb") as output_file:
        writer.write(output_file)


def decrypt_pdf(
        reader: PdfReader,
        password: str):
    """
    Decrypt a PDF file.
    """
    if reader.is_encrypted:
        reader.decrypt(password)  # Decrypt the PDF with the given password
    return reader


def decrypt_pdf_file(
        input_pdf: str,
        password: str):
    """
    Remove the password from a PDF file.

    Args:
        input_pdf (str): The path to the input PDF file.
        output_pdf (str): The path to the output PDF file.
        password (str): The password to remove from the PDF file.
    """
    # Read the PDF file
    reader = read_pdf(input_pdf)

    # Decrypt the PDF file
    reader = decrypt_pdf(reader, password)

    # Write the PDF file
    output_pdf = (
        f"{ct.TEMP_FOLDER}/{os.path.basename(input_pdf)}_decrypted.pdf"
    )
    write_pdf(output_pdf, reader)
    return output_pdf


def split_pdf_into_chunks(
        input_pdf: str,
        chunks_dir: str = ct.TEMP_FOLDER):
    """
    Split a PDF file into chunks.
    """

    if not os.path.exists(chunks_dir):
        os.mkdir(chunks_dir)

    reader = read_pdf(input_pdf)
    total_pages = len(reader.pages)
    chunks_paths = []

    # Get file name wihtout entire path
    file_name = os.path.basename(input_pdf)

    for i in range(0, total_pages, ct.MAX_PDF_CHUNK_SIZE):
        writer = PdfWriter()
        for j in range(i, min(i + ct.MAX_PDF_CHUNK_SIZE, total_pages)):
            writer.add_page(reader.pages[j])

        output_pdf = (
            f"{chunks_dir}/{file_name}_chunk_"
            f"{i//ct.MAX_PDF_CHUNK_SIZE + 1}.pdf"
        )
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)

        chunks_paths.append(output_pdf)

    return chunks_paths


def get_file_format(file_path: str) -> str:
    """
    Return the file extension (format) of the file, in lowercase,
    without the dot.
    """
    return os.path.splitext(file_path)[1][1:].lower()

from PyPDF2 import PdfReader, PdfWriter
import hashlib
import os
import logging


def remove_pdf_password(input_pdf, output_pdf, password):
    reader = PdfReader(input_pdf)

    if reader.is_encrypted:
        reader.decrypt(password)  # Decrypt the PDF with the given password

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    print(f"Password removed. Saved as '{output_pdf}'")


def split_pdf_into_chunks(
        input_pdf: str,
        chunks_dir: str,
        file_id: str,
        chunk_size: int = 11):

    if not os.path.exists(chunks_dir):
        os.mkdir(chunks_dir)
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    for i in range(0, total_pages, chunk_size):
        writer = PdfWriter()
        for j in range(i, min(i + chunk_size, total_pages)):
            writer.add_page(reader.pages[j])

        output_pdf = f"{chunks_dir}/{i//chunk_size + 1}.pdf"
        with open(output_pdf, "wb") as output_file:
            writer.write(output_file)


def generate_deterministic_id(seed):
    return hashlib.sha256(seed.encode()).hexdigest()[:32]

from textract import process_pdfs_in_bulk
from utils import (
    remove_pdf_password,
    split_pdf_into_chunks,
    generate_deterministic_id
)
import constants as ct

# def lambda_handler(event, context):


#     # analyze_document_local(
#     #     local_file=,
#     #     output_file=
#     # )

#     return


if __name__ == '__main__':
    event = {
        "file_path": "./raw/CuentaNu.pdf"
    }

    raw_pdf = event.get("file_path")
    bronze_pdf = raw_pdf.replace("raw", "bronze")
    file_id = generate_deterministic_id(
        seed=raw_pdf
    )

    # Remove PDF password
    remove_pdf_password(
        input_pdf=raw_pdf,
        output_pdf=bronze_pdf,
        password=ct.PASSWORD
    )

    # Split document
    # chunks_dir = f"{ct.SILVER_PATH}/{file_id}"
    # chunks_path = split_pdf_into_chunks(
    #     input_pdf=bronze_pdf,
    #     chunks_dir=chunks_dir,
    #     file_id=file_id,
    #     chunk_size=11
    # )

    # process_pdfs_in_bulk(
    #     file_id=file_id,
    #     chunks_dir=chunks_dir
    # )
    # # Example 2: Analyze local document and save output
    # local_file = 'mydocument.pdf'
    # chunks_path = analyze_document_local(
    #     local_file, 'output_local.txt')

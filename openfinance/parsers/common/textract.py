import openfinance.constants as ct
import os
import logging
from PyPDF2 import PdfReader


logger = logging.getLogger(__name__)


def is_pdf_encrypted(file_path: str) -> bool:
    """Check if a PDF file is encrypted."""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        return reader.is_encrypted


def analyze_document_s3(
        bucket_name: str,
        document_key: str,
        output_path: str):
    """
    Analyze a document stored in an S3 bucket using
    AWS Textract and save the results locally.
    """
    response = ct.textract_client.analyze_document(
        Document={'S3Object': {'Bucket': bucket_name, 'Name': document_key}},
        FeatureTypes=['TABLES', 'FORMS']  # Extract both table and form data
    )

    # Get the text blocks
    blocks = response['Blocks']

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index+1)
        # csv += '\n\n'

    # Save CSV
    csv_filename = f"{os.path.splitext(document_key)[0]}_table.csv"
    csv_path = os.path.join(output_path, csv_filename)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.write(csv)
    logger.info(f"Table saved as CSV: {csv_path}")

    return csv_path


def analyze_documents_s3(
        bucket_name: str,
        document_keys: list[str],
        output_path: str):
    """
    Analyze a list of documents stored in an S3 bucket using
    AWS Textract and save the results locally.
    """
    csv_paths = []
    for document_key in document_keys:
        csv_path = analyze_document_s3(
            bucket_name=bucket_name,
            document_key=document_key,
            output_path=output_path)
        csv_paths.append(csv_path)

    return csv_paths


def save_to_file(
        filename: str,
        text_lines: list[str]):
    """
    Save the extracted text to a local file.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("\n".join(text_lines))


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        # Always clean up the text by removing extra spaces
                        cleaned_word = word['Text'].replace(" ", "")
                        text += cleaned_word + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '
    return text.strip()


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    scores = []
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}

                    # get confidence score
                    scores.append(str(cell['Confidence']))

                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows, scores


def generate_table_csv(table_result, blocks_map, table_index):
    rows, scores = get_rows_columns_map(table_result, blocks_map)

    #  table_id = 'Table_' + str(table_index)

    # get cells.
    csv = ''  # Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():
        row_values = []
        for col_index, text in cols.items():
            _ = len(cols.items())
            # Clean up the text by stripping whitespace
            cleaned_text = text.strip() if text else ""
            # Quote the text if it contains
            # commas to prevent CSV parsing issues
            if ',' in cleaned_text:
                cleaned_text = f'"{cleaned_text}"'
            row_values.append(cleaned_text)
        csv += ','.join(row_values) + '\n'

    # Save confidence scores
    # csv += '\n\nConfidence Scores % (Table Cell) \n'
    # cols_count = 0
    # for score in scores:
    #     cols_count += 1
    #     csv += score + ","
    #     if cols_count == col_indices:
    #        csv += '\n'
    #        cols_count = 0

    #  csv += '\n\n\n'
    return csv

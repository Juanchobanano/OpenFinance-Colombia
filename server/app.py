from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import shutil
import tempfile
import os
from openfinance.parsers.nu_bank import parse_nubank_pdf
from openfinance.parsers.itau import parse_itau_pdf

app = FastAPI()


def save_temp_file(uploaded_file):
    # Save the uploaded file to a temporary location and return the path
    suffix = (
        os.path.splitext(uploaded_file.filename)[-1]
        if hasattr(uploaded_file, "filename")
        else ".pdf"
    )
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        if hasattr(uploaded_file, "file"):
            shutil.copyfileobj(uploaded_file.file, tmp)
        else:
            tmp.write(uploaded_file.read())
        return tmp.name


def classify_bank(sender_email):
    # Dummy logic for bank classification based on sender email
    sender_email = sender_email.lower()
    if "itau" in sender_email:
        return "itau"
    elif "nubank" in sender_email or "nu-bank" in sender_email:
        return "nubank"
    else:
        return "unknown"


def save_to_db(parsed_data):
    # Placeholder for saving parsed data to DB
    # For now, just print or pass
    pass


@app.post("/api/incoming-email")
async def handle_email(request: Request):
    form = await request.form()
    attachment_file = form['attachment']
    bank_sender = form['from']

    # Save the file
    filename = save_temp_file(attachment_file)

    # Determine bank type based on sender
    bank = classify_bank(bank_sender)

    # Parse attachment with correct parser
    if bank == "itau":
        parsed_data = parse_itau_pdf(filename)
    elif bank == "nubank":
        parsed_data = parse_nubank_pdf(filename)
    else:
        return JSONResponse(
            status_code=400, content={"error": "Unknown bank sender"})

    # Store transaction info to DB
    save_to_db(parsed_data)

    # Optionally, clean up the temp file
    try:
        os.remove(filename)
    except Exception:
        pass

    return {"status": "ok"}

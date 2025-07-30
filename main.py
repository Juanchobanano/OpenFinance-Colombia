from openfinance.parsers.nu_bank import parse_nubank_pdf
import logging
import openfinance.files.utils as ut
import openfinance.constants as ct

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="main.log",
    filemode="a"
)
logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":

    # Reset tmp folder
    ut.reset_folder("./tmp")

    try:
        parse_nubank_pdf(
            input_path="./data/Nu_2025-05-12.pdf",
            password=ct.NU_BANK_PASSWORD
        )
    except Exception as e:
        logging.error(f"Error: {e}")

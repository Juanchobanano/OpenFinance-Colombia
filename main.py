from openfinance.parser.textract.parser import FinancialStatementTextractParser
import logging
import openfinance.files.utils as ut
import openfinance.constants as ct
from openfinance.parser.processors.itau import CreditCardItauStatementPreprocessor
from openfinance.parser.processors.nu_bank import CreditCardNuBankStatementPreprocessor

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="main.log",
    filemode="a"
)
logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":

    for input_path in [
            "./data/Itau_extracto_TCR_TarjetaCredito_6467.pdf",
            "./data/Itau_extracto_TCR_TarjetaCredito_6475.pdf"]:

        # Reset tmp folder
        ut.reset_folder("./tmp")
        # input_path = "./data/Nu_2025-06-12.pdf"

        try:
            parser = FinancialStatementTextractParser(
                input_path=input_path,
                password=ct.ITAU_PASSWORD,
                bank_name="Itau"
            )
            parser_results = parser.parse()
            csv_files = parser_results['csv_paths']

            preprocessor = CreditCardItauStatementPreprocessor(
                input_path=input_path,
                csv_files=csv_files,
                output_folder=ct.OUTPUT_FOLDER
            )
            preprocessor.process_financial_statement()
            # print(preprocessor.df)

        except Exception as e:
            logging.error(f"Error: {e}")

from pathlib import Path
import fitz


class PDFParser:

    @staticmethod
    def extract_text(file_path: str) -> str:

        pdf_path = Path(file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        document = fitz.open(pdf_path)

        text = []

        try:

            for page in document:

                page_text = page.get_text("text")

                if page_text:

                    text.append(page_text)

        finally:

            document.close()

        return "\n".join(text)


# ------------------------------------
# Backward Compatible Function
# ------------------------------------

def extract_text_from_pdf(file_path: str) -> str:
    return PDFParser.extract_text(file_path)
import ocrmypdf
from PyPDF2 import PdfReader


def main():
    reader = PdfReader("tailieu.pdf")
    page = reader.pages[1]
    text = page.extract_text()
    print(text)
    ocrmypdf.ocr("tailieu.pdf", "output.pdf", language="eng")


if __name__ == "__main__":
    main()

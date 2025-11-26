from dataclasses import dataclass

import fitz


@dataclass
class PDFHandler:
    pdf_path: str
    zoom_factor: int = 2

    def extract_pdf_pages_as_images(self, from_page, to_page):
        """
        Extracts each page of a PDF as a PNG image.
        Args:
            pdf_path (str): Path to the PDF file.
            zoom_factor (int): Factor to increase image resolution (e.g., 2 for 2x resolution).
        Returns:
            list: A list of dictionaries, where each dict contains 'page_number'
                and 'image_bytes' (raw PNG bytes).
        """
        document = fitz.open(self.pdf_path)
        page_images = []

        # for page_num in range(len(document)):
        for page_num in range(from_page - 1, to_page):
            page = document.load_page(page_num)

            # Render page as a high-resolution PNG image
            # matrix applies a zoom factor for better image quality, which helps Gemini
            matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=matrix)

            # Get raw PNG bytes
            img_bytes = pix.tobytes("png")

            page_images.append({"page_number": page_num + 1, "image_bytes": img_bytes})
        document.close()
        return page_images

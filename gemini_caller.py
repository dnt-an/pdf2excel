from dataclasses import dataclass
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from pdf_handler import PDFHandler

load_dotenv()


pdf_path = "tailieu.pdf"


class Response(BaseModel):
    job_description: str
    unit: str
    quantity: float


# Định nghĩa cấu trúc cho một công việc cụ thể
class CongViec(BaseModel):
    noi_dung_cong_viec: str = Field(description="Nội dung chi tiết của công việc")
    don_vi: str = Field(description="Đơn vị tính (ví dụ: giờ, cái, mét)")
    khoi_luong: float = Field(description="Khối lượng hoặc số lượng công việc")


# Định nghĩa cấu trúc cho hạng mục lớn chứa danh sách công việc
class HangMuc(BaseModel):
    ten_hang_muc: str = Field(
        description="Tên của hạng mục công việc lớn (ví dụ: 'Phần mềm', 'Phần cứng')"
    )
    cong_viec: List[CongViec] = Field(
        description="Danh sách các công việc thuộc hạng mục này"
    )


# Định nghĩa cấu trúc phản hồi tổng thể (một danh sách các hạng mục)
class DanhSachCongViec(BaseModel):
    du_lieu: List[HangMuc] = Field(
        description="Danh sách các hạng mục và công việc tương ứng"
    )


@dataclass
class GeminiModel:
    api_key: str
    model_name: str = "gemini-2.5-flash"

    SYSTEM_INSTRUCTION = (
        "You extract BOQ table data from image. Output strict JSON only."
        "Do not guess: if unsure, mark needs_review=true and explain in notes."
        "Normalize all numbers in the text. Automatically detect the locale format (comma as decimal separator, dot as thousand separator). Return the values as proper numeric types."
    )

    PROMPT = """
        Task: Extract the BOQ table. Columns typically:
        Rules:
        - Use numeric types for quantity/rate/amount.
        - Report conf[0,1] for each numeric field; needs_review=true if conf<0.7 or validation fails.
        - Value of field "ĐƠN VỊ" can be expand muti-rows (Ex: 100m3/km, 10 tấn/km 100m cọc, m3 d.dịch).
        - Only consider records which has "STT" value
        - A page often has "HẠNG MỤC" item at the top. If there is no information for "HẠNG MỤC" in a page, set value as empty string
        """

    generation_config = {
        "temperature": 0,
        "top_p": 0.1,
        "top_k": 1,
        "max_output_tokens": 1000000,
        "response_mime_type": "application/json",
        "response_schema": HangMuc,
        # "response_schema": DanhSachCongViec.model_json_schema(),
    }

    # model_multimodal = genai.GenerativeModel(
    #     model_name=self.model_name,
    #     system_instruction=SYSTEM_INSTRUCTION,
    #     generation_config=generation_config,
    # )

    def __post_init__(self):
        # configure the API key after initialization
        genai.configure(api_key=self.api_key)
        self.model_multimodal = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.SYSTEM_INSTRUCTION,
            generation_config=self.generation_config,
        )

    def extract_info(self, pdf_path, from_page, to_page):
        pdf_handler = PDFHandler(pdf_path)
        pdf_pages_as_images = pdf_handler.extract_pdf_pages_as_images(
            from_page=from_page, to_page=to_page
        )
        responses = []
        for i in range(len(pdf_pages_as_images)):
            page_data = pdf_pages_as_images[i]

            # # Add the image part. Gemini accepts raw bytes for images.
            # contents_for_gemini.append(
            #     {"mime_type": "image/png", "data": page_data["image_bytes"]}
            # )
            # # You can also add text descriptions for each page, e.g., "This is page X of the document."
            # contents_for_gemini.append(f"\n--- Page {page_data['page_number']} ---\n")
            contents_for_gemini = [self.PROMPT] + [
                {"mime_type": "image/png", "data": page_data["image_bytes"]}
            ]
            # Make the API call
            try:
                print(f"processing page {page_data['page_number']}")
                resp = self.model_multimodal.generate_content(contents_for_gemini)
                resp = HangMuc.model_validate_json(resp.text)
                responses.append(resp)

            except Exception as e:
                print(f"An error occurred: {e}")
                # If the request is too large, you might get a "400 Request payload size exceeds limit" error.
                # In that case, you'll need to process fewer pages or reduce image quality/size.

        return responses

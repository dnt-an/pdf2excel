import os
from dataclasses import dataclass
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from pdf_handler import PDFHandler

load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
    # SYSTEM_INSTRUCTION = """
    # You're a Quantity Surveyor AI designed to assist with tasks related to reading and understanding PDF documents. Your primary function is to extract text from PDF files and provide a structured response
    # """
    SYSTEM_INSTRUCTION = (
        "You extract BOQ table data from image. Output strict JSON only."
        "Do not guess: if unsure, mark needs_review=true and explain in notes."
        "Normalize all numbers in the text. Automatically detect the locale format (comma as decimal separator, dot as thousand separator). Return the values as proper numeric types."
    )

    # PROMPT_TEMPLATE = """
    # # User Request
    # Read the image and extract the information which include "HẠNG MỤC" and its corresponding BOQ table
    # - Response should be in JSON format with the following structure:
    #     [
    #         "Hạng mục": "<Hạng mục>",
    #         "Công việc":[
    #             {
    #                 "Nội dung công việc": "<Nội dung công việc>",
    #                 "Đơn vị": "<Đơn vị>",
    #                 "Khối lượng": "<Khối lượng>",
    #             }
    #         ]
    #     ]
    # - Each page is a "Hạng mục". If there is no information for "Hạng mục" in a page, set value as empty string
    # - Ensure the response is accurate and concise.
    # - Value of field "ĐƠN VỊ" can be expand muti-rows (Ex: 100m3/km, 100m cọc).
    # - Only consider records which has "STT" value
    # """
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
        "response_schema": DanhSachCongViec,
        # "response_schema": DanhSachCongViec.model_json_schema(),
    }
    model_multimodal = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config=generation_config,
    )

    def extract_info(self, pdf_path):
        pdf_handler = PDFHandler(pdf_path)
        pdf_pages_as_images = pdf_handler.extract_pdf_pages_as_images(
            from_page=1, to_page=1
        )
        contents_for_gemini = [self.PROMPT]
        for i in range(len(pdf_pages_as_images)):
            page_data = pdf_pages_as_images[i]

            # Add the image part. Gemini accepts raw bytes for images.
            contents_for_gemini.append(
                {"mime_type": "image/png", "data": page_data["image_bytes"]}
            )
            # You can also add text descriptions for each page, e.g., "This is page X of the document."
            contents_for_gemini.append(f"\n--- Page {page_data['page_number']} ---\n")

        # Make the API call
        try:
            print("Sending content to Gemini model...")
            resp = self.model_multimodal.generate_content(contents_for_gemini)
            print(resp)
            resp = DanhSachCongViec.model_validate_json(resp.text)
            print("\n--- Gemini Model Response ---")
            print(resp)
            print(type(resp))
            return resp

        except Exception as e:
            print(f"An error occurred: {e}")
            # If the request is too large, you might get a "400 Request payload size exceeds limit" error.
            # In that case, you'll need to process fewer pages or reduce image quality/size.


# model = GeminiModel()
# resp = model.extract_info(pdf_path)
# resp = DanhSachCongViec.model_validate_json(resp.text)
# json_string = resp.model_dump_json(indent=4, ensure_ascii=False)
# type(resp)

# try:
#     # with open("output.json", "w") as f:
#     #     json.dump(resp.text, f, indent=4)  # Using 'indent' for pretty-printing
#     with open("output.json", "w", encoding="utf-8") as f:
#         f.write(json_string)
#     # with open("output.json", "w", encoding="utf-8") as json_file:
#     #     json.dump(resp, json_file, indent=4, ensure_ascii=False)
#     print("JSON data has been successfully written to 'output.json'")
# except IOError as e:
#     print(f"Error writing to file: {e}")

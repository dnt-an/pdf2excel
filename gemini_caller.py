from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import google.generativeai as genai
from pydantic import BaseModel

from pdf_handler import PDFHandler


# -----------------------------
# Pydantic Models
# -----------------------------
class CongViec(BaseModel):
    noi_dung_cong_viec: str
    don_vi: str
    khoi_luong: float


class HangMuc(BaseModel):
    ten_hang_muc: str
    cong_viec: List[CongViec]


class DanhSachCongViec(BaseModel):
    du_lieu: List[HangMuc]


# -----------------------------
# Gemini Model Wrapper
# -----------------------------
@dataclass
class GeminiModel:
    api_key: str
    model_name: str = "gemini-2.5-flash"

    # Cached models to avoid reloading
    _cached_models: Dict[str, genai.GenerativeModel] = None

    SYSTEM_INSTRUCTION = (
        "You extract BOQ table data from image. Output strict JSON only. "
        "Do not guess: if unsure, mark needs_review=true and explain in notes. "
        "Normalize all numbers with locale detection. Return numeric types."
    )

    PROMPT = """
        Task: Extract the BOQ table from the page.
        Rules:
        - Use numeric types only for quantities. Automatically detect the locale format (comma as decimal separator, dot as thousand separator)
        - Report conf[0,1] for each numeric field; set needs_review=true if conf<0.7.
        - Column 'ĐƠN VỊ' may span multiple row formats. (Ex: 100m3/km, 10 tấn/km 100m cọc, m3 d.dịch).
        - Only include rows with an STT value.
        - If a page has no 'HẠNG MỤC', return an empty string for 'ten_hang_muc'.
        - If a page has a 'HẠNG MỤC', return its value **without the prefix 'HẠNG MỤC :'** or any colon/label; only return the actual name of the section.
    """

    generation_config = {
        "temperature": 0,
        "top_p": 0.1,
        "top_k": 1,
        "max_output_tokens": 1000000,
        "response_mime_type": "application/json",
        "response_schema": HangMuc,
    }

    def __post_init__(self):
        genai.configure(api_key=self.api_key)

        if GeminiModel._cached_models is None:
            GeminiModel._cached_models = {}

        # Load once
        if self.model_name not in GeminiModel._cached_models:
            GeminiModel._cached_models[self.model_name] = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.SYSTEM_INSTRUCTION,
                generation_config=self.generation_config,
            )

        self.model_multimodal = GeminiModel._cached_models[self.model_name]

    # ---------------------------------------------------------
    # Main extraction logic with progress + cancellation
    # ---------------------------------------------------------
    def extract_info(
        self,
        pdf_path: str,
        from_page: int,
        to_page: int,
        cancel_flag: Callable[[], bool],
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        pdf_handler = PDFHandler(pdf_path)
        pdf_pages = pdf_handler.extract_pdf_pages_as_images(
            from_page=from_page, to_page=to_page
        )

        responses = []

        for page in pdf_pages:
            page_number = page["page_number"]

            # Send progress to UI
            progress_callback(f"Extracting page {page_number}…")

            # Check cancellation BEFORE starting API call
            if cancel_flag():
                progress_callback("Cancelling…")
                break

            try:
                resp = self.model_multimodal.generate_content(
                    [
                        self.PROMPT,
                        {"mime_type": "image/png", "data": page["image_bytes"]},
                    ]
                )

                # Check cancellation immediately after API returns
                if cancel_flag():
                    progress_callback("Cancelling…")
                    break

                parsed = HangMuc.model_validate_json(resp.text)
                responses.append(parsed)

            except Exception as e:
                progress_callback(f"Error on page {page_number}: {e}")
                continue

        return responses

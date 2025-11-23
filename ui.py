# import os
# import threading
# import tkinter as tk
# from tkinter import filedialog, messagebox

# import ttkbootstrap as tb

# from excel_handler import ExcelHandler
# from gemini_caller import GeminiModel


# class PDFExtractionApp:
#     def __init__(self, root):
#         self.root = root
#         style = tb.Style(theme="darkly")
#         self.root.title("AI PDF Extraction App")
#         self.root.geometry("500x320")

#         # App state
#         self.pdf_path = None
#         self.extracted_data = None

#         # ----- Layout -----
#         frame = tb.Frame(root, padding=20)
#         frame.pack(fill="both", expand=True)

#         # Load PDF
#         self.load_btn = tb.Button(
#             frame, text="Load PDF", bootstyle="primary", width=20, command=self.load_pdf
#         )
#         self.load_btn.pack(pady=10)

#         # PDF label (shows selected file)
#         self.pdf_label = tb.Label(frame, text="No PDF selected", bootstyle="default")
#         self.pdf_label.pack(pady=5)

#         # Extract button
#         self.extract_btn = tb.Button(
#             frame,
#             text="Extract Info (AI)",
#             bootstyle="success",
#             width=20,
#             command=self.extract_info,
#         )
#         self.extract_btn.pack(pady=15)

#         # Progress bar
#         self.progress = tb.Progressbar(
#             frame, mode="indeterminate", bootstyle="info-striped", length=250
#         )
#         self.progress.pack(pady=10)
#         self.progress.pack_forget()  # hide initially

#         # Export button
#         self.export_btn = tb.Button(
#             frame,
#             text="Export to Excel",
#             bootstyle="info",
#             width=20,
#             command=self.export_excel,
#         )
#         self.export_btn.pack(pady=10)

#     # 1. Load PDF and preview first page
#     def load_pdf(self):
#         self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
#         if not self.pdf_path:
#             return

#         filename = os.path.basename(self.pdf_path)
#         self.pdf_label.config(text=f"Loaded: {filename}", bootstyle="default")

#     # 2. Extract using AI (your AI logic)
#     def extract_info(self):
#         if not self.pdf_path:
#             messagebox.showwarning("Warning", "Please load a PDF first.")
#             return

#         # --- Disable UI + show progress ---
#         self.extract_btn.configure(state="disabled")
#         self.load_btn.configure(state="disabled")
#         self.export_btn.configure(state="disabled")
#         self.progress.pack()
#         self.progress.start(10)

#         # --- Start AI extraction in a separate thread ---
#         thread = threading.Thread(target=self.run_ai_extraction)
#         thread.start()

#         # model = GeminiModel()
#         # resp = model.extract_info(self.pdf_path)
#         # json_string = resp.model_dump_json(indent=4, ensure_ascii=False)

#     def run_ai_extraction(self):
#         """This function runs in a background thread."""
#         model = GeminiModel()
#         try:
#             # Call your real AI extraction function
#             self.extracted_data = model.extract_info(self.pdf_path)  # <-- your function
#         except Exception as e:
#             self.extracted_data = None
#             print("AI Extraction Error:", e)
#         finally:
#             # Update UI back in main thread
#             self.root.after(0, self.finish_extraction)

#     def finish_extraction(self):
#         # --- Stop and hide progress bar ---
#         self.progress.stop()
#         self.progress.pack_forget()

#         # Enable buttons again
#         self.extract_btn.configure(state="normal")
#         self.load_btn.configure(state="normal")
#         self.export_btn.configure(state="normal")

#         messagebox.showinfo("AI Extraction", "Extracted information successfully!")

#     # 3. Save extracted info to Excel
#     def export_excel(self):
#         if not self.extracted_data:
#             tk.messagebox.showwarning("Warning", "No extracted data to export.")
#             return

#         file_path = tk.filedialog.asksaveasfilename(
#             defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")]
#         )

#         if not file_path:
#             return

#         excel_handler = ExcelHandler()
#         excel_handler.write_data(self.extracted_data, file_path)
#         # wb = openpyxl.Workbook()
#         # ws = wb.active
#         # ws.title = "Extracted Info"

#         # ws.append(["Field", "Value"])
#         # for k, v in self.extracted_data.items():
#         #     ws.append([k, v])

#         # wb.save(file_path)
#         tk.messagebox.showinfo("Success", "Excel file saved successfully!")


# # Run App
# root = tk.Tk()
# app = PDFExtractionApp(root)
# root.mainloop()


import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as tb

from excel_handler import ExcelHandler
from gemini_caller import GeminiModel


class PDFExtractionApp:
    def __init__(self, root: tk.Tk, theme: str = "darkly"):
        self.root = root
        self.root.title("AI PDF Extraction App")
        self.root.geometry("500x360")

        # Apply theme
        self.style = tb.Style(theme=theme)

        # App state
        self.pdf_path: str | None = None
        self.extracted_data: dict | None = None

        # --- Layout ---
        frame = tb.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        # Load PDF button
        self.load_btn = tb.Button(
            frame, text="Load PDF", bootstyle="primary", width=20, command=self.load_pdf
        )
        self.load_btn.pack(pady=10)

        # PDF label
        self.pdf_label = tb.Label(frame, text="No PDF selected", bootstyle="default")
        self.pdf_label.pack(pady=5)

        # Extract button
        self.extract_btn = tb.Button(
            frame,
            text="Extract Info (AI)",
            bootstyle="success",
            width=20,
            command=self.extract_info_threaded,
        )
        self.extract_btn.pack(pady=15)

        # Progress bar
        self.progress = tb.Progressbar(
            frame, mode="indeterminate", bootstyle="info-striped", length=250
        )
        self.progress.pack(pady=10)
        self.progress.pack_forget()  # hidden initially

        # Export button
        self.export_btn = tb.Button(
            frame,
            text="Export to Excel",
            bootstyle="info",
            width=20,
            command=self.export_excel,
        )
        self.export_btn.pack(pady=10)

    # ---------------------------
    # Load PDF
    # ---------------------------
    def load_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        self.pdf_path = path
        filename = os.path.basename(path)
        self.pdf_label.config(text=f"Loaded: {filename}", bootstyle="default")

    # ---------------------------
    # Extract AI info in a thread
    # ---------------------------
    def extract_info_threaded(self) -> None:
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please load a PDF first.")
            return

        # Disable buttons and start progress bar
        self._set_ui_state(disabled=True)
        self.progress.pack()
        self.progress.start(10)

        # Run AI extraction in background
        thread = threading.Thread(target=self._run_ai_extraction, daemon=True)
        thread.start()

    def _run_ai_extraction(self) -> None:
        """Background thread: call AI model and update UI when done"""
        model = GeminiModel()
        try:
            self.extracted_data = model.extract_info(self.pdf_path)
        except Exception as e:
            self.extracted_data = None
            print("AI Extraction Error:", e)
        finally:
            self.root.after(0, self._finish_extraction)

    def _finish_extraction(self) -> None:
        # Stop progress bar and re-enable buttons
        self.progress.stop()
        self.progress.pack_forget()
        self._set_ui_state(disabled=False)

        if self.extracted_data:
            messagebox.showinfo("AI Extraction", "Extracted information successfully!")
        else:
            messagebox.showerror("Error", "AI extraction failed!")

    # ---------------------------
    # Export to Excel
    # ---------------------------
    def export_excel(self) -> None:
        if not self.extracted_data:
            messagebox.showwarning("Warning", "No extracted data to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")]
        )
        if not path:
            return

        excel_handler = ExcelHandler()
        excel_handler.write_data(self.extracted_data, path)
        messagebox.showinfo("Success", "Excel file saved successfully!")

    # ---------------------------
    # Utility: Enable/Disable UI
    # ---------------------------
    def _set_ui_state(self, disabled: bool) -> None:
        state = "disabled" if disabled else "normal"
        self.extract_btn.configure(state=state)
        self.load_btn.configure(state=state)
        self.export_btn.configure(state=state)


# ---------------------------
# Run the app
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFExtractionApp(root)
    root.mainloop()

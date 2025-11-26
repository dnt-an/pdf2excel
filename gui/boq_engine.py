import pathlib
import threading
from queue import Queue
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ai.gemini_caller import GeminiModel
from services.excel_handler import write_data_to_excel


class BoqExtractorEngine(ttk.Frame):
    queue = Queue()
    searching = False

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        # Application Variables
        default_path = pathlib.Path().absolute().as_posix()
        self.input_path_var = ttk.StringVar(value=default_path)
        self.output_path_var = ttk.StringVar(value=default_path)
        self.api_key_var = ttk.StringVar(value="Input your API key")
        self.lbl_width = 12

        # Cancel flag
        self.cancel_requested = False
        self.worker_thread = None

        # Thread-safe queue for status updates
        self.status_queue = Queue()

        # Build UI
        self._build_option_frame()
        self._build_result_frame()

        # Status Label
        self.status_label = ttk.Label(self.result_lf, text="", bootstyle=INFO)
        self.status_label.pack(fill=X, pady=5)

        # Progress Bar
        self.progressbar = ttk.Progressbar(
            master=self.result_lf, mode=INDETERMINATE, bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack_forget()

        # Poll queue for status messages
        self.after(100, self.poll_status_queue)

    # ----------------- UI Construction -----------------
    def _build_option_frame(self):
        from gui.row_builders import RowBuilder

        self.option_lf = ttk.Labelframe(
            self, text="Complete the form to extract the BOQ", padding=15
        )
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        RowBuilder(self).build_api_key_row()
        RowBuilder(self).build_input_path_row()
        RowBuilder(self).build_extract_range_row()
        RowBuilder(self).build_output_path_row()

    def _build_result_frame(self):
        self.result_lf = ttk.Labelframe(self, padding=15)
        self.result_lf.pack(fill=X, expand=YES, anchor=N)

        # Buttons
        self.convert_btn = ttk.Button(
            self.result_lf, text="Run", command=self.on_run, width=10
        )
        self.convert_btn.pack(side=LEFT)

        self.cancel_btn = ttk.Button(
            self.result_lf,
            text="Cancel",
            command=self.on_cancel,
            width=10,
            bootstyle=DANGER,
            state=DISABLED,
        )
        self.cancel_btn.pack(side=LEFT, padx=5)
        self.cancel_btn.pack_forget()

    # ----------------- File Dialogs -----------------
    def on_browse(self):
        from utils.file_dialogs import browse_file

        path = browse_file()
        if path:
            self.input_path_var.set(path)

    def on_export(self):
        from utils.file_dialogs import save_file

        path = save_file()
        if path:
            self.output_path_var.set(path)

    # ----------------- Convert / Cancel -----------------
    def on_run(self):
        self.extract_info_threaded()

    def on_cancel(self):
        self.cancel_requested = True
        self.cancel_btn.config(state="disabled")
        self.convert_btn.config(state="normal")

    # ----------------- Threaded AI extraction -----------------
    def extract_info_threaded(self):
        if not self.input_path_var.get():
            messagebox.showwarning("Warning", "Please load a PDF first.")
            return

        try:
            from_page = int(self.from_page_var.get())
            to_page = int(self.to_page_var.get())
        except ValueError:
            messagebox.showerror("Error", "Page numbers must be integers.")
            return

        if from_page > to_page:
            messagebox.showerror("Error", "'From page' must be <= 'To page'.")
            return
        self._from_page = from_page
        self._to_page = to_page

        self.convert_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progressbar.pack(fill=X, expand=YES)
        self.progressbar.start(10)

        self.worker_thread = threading.Thread(
            target=self._run_ai_extraction, daemon=True
        )
        self.worker_thread.start()

    def _run_ai_extraction(self):
        try:
            model = GeminiModel(
                api_key=self.api_key_var.get(), model_name="gemini-2.5-flash"
            )
            self.extracted_data = model.extract_info(
                pdf_path=self.input_path_var.get(),
                from_page=self._from_page,
                to_page=self._to_page,
                cancel_flag=lambda: self.cancel_requested,
                progress_callback=lambda msg: self.status_queue.put(msg),
            )
        except Exception as e:
            self.extracted_data = None
            print("AI Extraction Error:", e)
        finally:
            self.after(0, self._finish_extraction)

    def _finish_extraction(self):
        self.progressbar.stop()
        self.progressbar.pack_forget()
        self.convert_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.cancel_requested = False

        if self.extracted_data:
            try:
                write_data_to_excel(self.extracted_data, self.output_path_var.get())
                messagebox.showinfo(
                    "Success",
                    f"Saved to {self.output_path_var.get()}!",
                )
            except ValueError as ve:
                # Display the error in a messagebox
                messagebox.showerror("Error", str(ve))
                return
        else:
            messagebox.showerror("Error", "AI extraction failed!")

    # ----------------- Status Queue Polling -----------------
    def poll_status_queue(self):
        try:
            while True:
                msg = self.status_queue.get_nowait()
                self.status_label.config(text=msg)
        except:
            pass
        self.after(100, self.poll_status_queue)

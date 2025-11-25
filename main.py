import pathlib
import threading
from queue import Queue
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from excel_handler import write_data_to_excel
from gemini_caller import GeminiModel


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

    # ----------------------------------------------------------------------
    # UI Construction
    # ----------------------------------------------------------------------
    def _build_option_frame(self):
        """Options section for input parameters."""
        text = "Complete the form to extract the BOQ"
        self.option_lf = ttk.Labelframe(self, text=text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self._create_api_key_row()
        self._create_input_path_row()
        self._create_extract_range_row()
        self._create_output_path_row()

    def _build_result_frame(self):
        """Extract button + progress bar."""
        self.result_lf = ttk.Labelframe(self, padding=15)
        self.result_lf.pack(fill=X, expand=YES, anchor=N)

        # Convert Button
        self.convert_btn = ttk.Button(
            master=self.result_lf,
            text="Convert",
            command=self.on_convert,
            width=10,
        )
        self.convert_btn.pack(side=LEFT)

        # Cancel Button
        self.cancel_btn = ttk.Button(
            master=self.result_lf,
            text="Cancel",
            command=self.on_cancel,
            width=10,
            bootstyle=DANGER,
            state=DISABLED,
        )
        self.cancel_btn.pack(side=LEFT, padx=5)

    # ----------------------------------------------------------------------
    # Row Builders
    # ----------------------------------------------------------------------
    def _create_api_key_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES, pady=10)

        ttk.Label(row, text="API Key:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.api_key_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

    def _create_input_path_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES)

        ttk.Label(row, text="Input File:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.input_path_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )
        self.browse_btn = ttk.Button(
            row, text="Browse", command=self.on_browse, width=8
        )
        self.browse_btn.pack(side=LEFT, padx=5)

    def _create_output_path_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES)

        ttk.Label(row, text="Save As:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.output_path_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )
        self.save_btn = ttk.Button(
            row,
            text="Select",
            command=self.on_export,
            width=8,
            bootstyle=OUTLINE,
        )
        self.save_btn.pack(side=LEFT, padx=5)

    def _create_extract_range_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES, pady=10)

        ttk.Label(row, text="From Page:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        self.from_page_var = ttk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.from_page_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

        ttk.Label(row, text="To Page:", width=8).pack(side=LEFT, padx=(15, 0))
        self.to_page_var = ttk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.to_page_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

    # ----------------------------------------------------------------------
    # File Dialog Handlers
    # ----------------------------------------------------------------------
    def on_browse(self):
        input_file = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if input_file:
            self.input_path_var.set(input_file)

    def on_export(self):
        file_path = asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")]
        )
        if file_path:
            self.output_path_var.set(file_path)

    def on_convert(self):
        self.convert_btn.config(state="disabled")
        self.browse_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.extract_info_threaded()

    def on_cancel(self):
        self.cancel_requested = True
        self.cancel_btn.config(state="disabled")
        self.convert_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.browse_btn.config(state="normal")

    # ----------------------------------------------------------------------
    # AI Processing (threaded)
    # ----------------------------------------------------------------------
    def extract_info_threaded(self):
        """Run extraction in a separate thread."""
        if not self.input_path_var.get():
            messagebox.showwarning("Warning", "Please load a PDF first.")
            return

        self.progressbar.pack(fill=X, expand=YES)
        self.progressbar.start(10)

        self.worker_thread = threading.Thread(
            target=self._run_ai_extraction, daemon=True
        )
        self.worker_thread.start()

    def _run_ai_extraction(self):
        try:
            from_page = int(self.from_page_var.get())
            to_page = int(self.to_page_var.get())
        except ValueError:
            messagebox.showerror("Error", "Page numbers must be integers.")
            return

        if from_page > to_page:
            messagebox.showerror("Error", "'From page' must be <= 'To page'.")
            return

        """Background worker for AI tasks."""
        try:
            model = GeminiModel(
                api_key=self.api_key_var.get(), model_name="gemini-2.5-flash"
            )

            self.extracted_data = model.extract_info(
                pdf_path=self.input_path_var.get(),
                from_page=from_page,
                to_page=to_page,
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
        self.browse_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.cancel_requested = False

        if self.extracted_data:
            messagebox.showinfo("Success", "Extracted information successfully!")
            print(self.extracted_data)
            write_data_to_excel(self.extracted_data, self.output_path_var.get())
        else:
            messagebox.showerror("Error", "AI extraction failed!")

    # ----------------------------------------------------------------------

    def poll_status_queue(self):
        """Check for messages from worker thread."""
        try:
            while True:
                msg = self.status_queue.get_nowait()
                self.status_label.config(text=msg)
        except:
            pass

        self.after(100, self.poll_status_queue)


if __name__ == "__main__":
    app = ttk.Window("AI BOQ extractor", "journal")
    BoqExtractorEngine(app)
    app.mainloop()

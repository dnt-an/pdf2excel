# import pathlib
# import threading
# from queue import Queue
# from tkinter import messagebox
# from tkinter.filedialog import askdirectory, asksaveasfilename

# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *

# from gemini_caller import GeminiModel


# class FileSearchEngine(ttk.Frame):
#     queue = Queue()
#     searching = False

#     def __init__(self, master):
#         super().__init__(master, padding=15)
#         self.pack(fill=BOTH, expand=YES)

#         # application variables
#         _path = pathlib.Path().absolute().as_posix()
#         self.input_path_var = ttk.StringVar(value=_path)
#         self.output_path_var = ttk.StringVar(value=_path)
#         self.api_key_var = ttk.StringVar(value="Input your API key")
#         self.term_var = ttk.StringVar(value="md")
#         self.type_var = ttk.StringVar(value="endswidth")
#         self.lbl_width = 10

#         # header and labelframe option container
#         option_text = "Complete the form to extract the BOQ"
#         self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
#         self.option_lf.pack(fill=X, expand=YES, anchor=N)

#         # header and labelframe option container
#         result_text = "Complete the form to begin your conversion"
#         self.result_lf = ttk.Labelframe(self, padding=15)
#         self.result_lf.pack(fill=X, expand=YES, anchor=N)

#         self.create_api_key_row()
#         self.create_input_path_row()
#         self.create_extract_range_row()
#         self.create_output_path_row()
#         self.create_convert_row()

#         self.progressbar = ttk.Progressbar(
#             master=self.result_lf, mode=INDETERMINATE, bootstyle=(STRIPED, SUCCESS)
#         )
#         # self.progressbar.pack(fill=X, expand=YES)
#         self.progressbar.pack_forget()

#     def create_input_path_row(self):
#         """Add input path row to labelframe"""
#         input_file_row = ttk.Frame(self.option_lf)
#         input_file_row.pack(fill=X, expand=YES)
#         input_file_lbl = ttk.Label(
#             input_file_row, text="Input file", width=self.lbl_width
#         )
#         input_file_lbl.pack(side=LEFT, padx=(15, 0))
#         input_file_ent = ttk.Entry(input_file_row, textvariable=self.input_path_var)
#         input_file_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
#         browse_btn = ttk.Button(
#             master=input_file_row, text="Browse", command=self.on_browse, width=8
#         )
#         browse_btn.pack(side=LEFT, padx=5)

#     def create_output_path_row(self):
#         """Add output path row to labelframe"""
#         output_file_row = ttk.Frame(self.option_lf)
#         output_file_row.pack(fill=X, expand=YES)
#         output_file_lbl = ttk.Label(
#             output_file_row, text="Save to", width=self.lbl_width
#         )
#         output_file_lbl.pack(side=LEFT, padx=(15, 0))
#         output_file_ent = ttk.Entry(output_file_row, textvariable=self.output_path_var)
#         output_file_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
#         export_btn = ttk.Button(
#             master=output_file_row,
#             text="Save as",
#             command=self.on_export,
#             width=8,
#             bootstyle=OUTLINE,
#         )
#         export_btn.pack(side=LEFT, padx=5)

#     def create_extract_range_row(self):
#         """Add extract range row to labelframe"""
#         extract_range_row = ttk.Frame(self.option_lf)
#         extract_range_row.pack(fill=X, expand=YES, pady=15)
#         from_page_lbl = ttk.Label(
#             extract_range_row, text="From page", width=self.lbl_width
#         )
#         from_page_lbl.pack(side=LEFT, padx=(15, 0))
#         from_page_ent = ttk.Entry(extract_range_row)
#         from_page_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
#         to_page_lbl = ttk.Label(extract_range_row, text="To page", width=8)
#         to_page_lbl.pack(side=LEFT, padx=(15, 0))
#         to_page_ent = ttk.Entry(extract_range_row)
#         to_page_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)

#     def create_api_key_row(self):
#         """Add api key row to labelframe"""
#         api_key_row = ttk.Frame(self.option_lf)
#         api_key_row.pack(fill=X, expand=YES, pady=15)
#         api_key_lbl = ttk.Label(api_key_row, text="API key", width=self.lbl_width)
#         api_key_lbl.pack(side=LEFT, padx=(15, 0))
#         api_key_ent = ttk.Entry(api_key_row, textvariable=self.api_key_var)
#         api_key_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)

#     def create_convert_row(self):
#         """Add convert row to labelframe"""
#         convert_btn = ttk.Button(
#             master=self.result_lf,
#             text="Convert",
#             command=self.extract_info_threaded,
#             width=8,
#         )
#         convert_btn.pack(side=LEFT, padx=5)

#     def on_browse(self):
#         """Callback for directory browse"""
#         input_path = askdirectory(title="Browse directory")
#         if input_path:
#             self.input_path_var.set(input_path)

#     def on_export(self):
#         """Callback for file export"""
#         output_path = asksaveasfilename(
#             defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")]
#         )
#         if output_path:
#             self.output_path_var.set(output_path)

#     # def on_convert(self):
#     #     self.extract_info_threaded()

#     def _run_ai_extraction(self) -> None:
#         """Background thread: call AI model and update UI when done"""
#         api_key = self.api_key_var.get()
#         model = GeminiModel(api_key=api_key, model_name="gemini-2.5-flash")
#         try:
#             self.extracted_data = model.extract_info(self.input_path_var)
#         except Exception as e:
#             self.extracted_data = None
#             print("AI Extraction Error:", e)
#         finally:
#             self.root.after(0, self._finish_extraction)

#     def extract_info_threaded(self) -> None:
#         if not self.input_path_var:
#             messagebox.showwarning("Warning", "Please load a PDF first.")
#             return

#         # Disable buttons and start progress bar
#         # self._set_ui_state(disabled=True)
#         self.progressbar.pack(fill=X, expand=YES)
#         self.progressbar.start(10)

#         # Run AI extraction in background
#         thread = threading.Thread(target=self._run_ai_extraction, daemon=True)
#         thread.start()

#     def _finish_extraction(self) -> None:
#         # Stop progress bar and re-enable buttons
#         self.progress.stop()
#         self.progress.pack_forget()
#         # self._set_ui_state(disabled=False)

#         if self.extracted_data:
#             messagebox.showinfo("AI Extraction", "Extracted information successfully!")
#         else:
#             messagebox.showerror("Error", "AI extraction failed!")

#     # # Utility: Enable/Disable UI
#     # def _set_ui_state(self, disabled: bool) -> None:
#     #     state = "disabled" if disabled else "normal"
#     #     self.extract_btn.configure(state=state)
#     #     self.load_btn.configure(state=state)
#     #     self.export_btn.configure(state=state)


# if __name__ == "__main__":
#     app = ttk.Window("File Search Engine", "journal")
#     FileSearchEngine(app)
#     app.mainloop()


import pathlib
import threading
from queue import Queue
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from excel_handler import write_data_to_excel
from gemini_caller import GeminiModel


class FileSearchEngine(ttk.Frame):
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

        # Build UI
        self._build_option_frame()
        self._build_result_frame()

        # Progress Bar
        self.progressbar = ttk.Progressbar(
            master=self.result_lf, mode=INDETERMINATE, bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack_forget()

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

        convert_btn = ttk.Button(
            master=self.result_lf,
            text="Convert",
            command=self.on_convert,
            width=10,
        )
        convert_btn.pack(side=LEFT)

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
        ttk.Button(row, text="Browse", command=self.on_browse, width=8).pack(
            side=LEFT, padx=5
        )

    def _create_output_path_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES)

        ttk.Label(row, text="Save As:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.output_path_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )
        ttk.Button(
            row,
            text="Select",
            command=self.on_export,
            width=8,
            bootstyle=OUTLINE,
        ).pack(side=LEFT, padx=5)

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
        self.extract_info_threaded()

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

        thread = threading.Thread(target=self._run_ai_extraction, daemon=True)
        thread.start()

    def _run_ai_extraction(self):
        """Background worker for AI tasks."""
        try:
            model = GeminiModel(
                api_key=self.api_key_var.get(), model_name="gemini-2.5-flash"
            )

            self.extracted_data = model.extract_info(
                pdf_path=self.input_path_var.get(),
                from_page=int(self.from_page_var.get()),
                to_page=int(self.to_page_var.get()),
            )

        except Exception as e:
            self.extracted_data = None
            print("AI Extraction Error:", e)

        finally:
            self.after(0, self._finish_extraction)

    def _finish_extraction(self):
        self.progressbar.stop()
        self.progressbar.pack_forget()

        if self.extracted_data:
            messagebox.showinfo("Success", "Extracted information successfully!")
            print(self.extracted_data)
            write_data_to_excel(self.extracted_data, self.output_path_var.get())
        else:
            messagebox.showerror("Error", "AI extraction failed!")

    # ----------------------------------------------------------------------


if __name__ == "__main__":
    app = ttk.Window("File Search Engine", "journal")
    FileSearchEngine(app)
    app.mainloop()

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class RowBuilder:
    """Helper to build rows in the BoqExtractorEngine option frame."""

    def __init__(self, engine):
        self.engine = engine
        self.option_lf = engine.option_lf
        self.lbl_width = engine.lbl_width

    def build_api_key_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES, pady=10)

        ttk.Label(row, text="API Key:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.engine.api_key_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

    def build_input_path_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES)

        ttk.Label(row, text="Input File:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.engine.input_path_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )
        browse_btn = ttk.Button(
            row, text="Browse", command=self.engine.on_browse, width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def build_output_path_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES)

        ttk.Label(row, text="Save As:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        ttk.Entry(row, textvariable=self.engine.output_path_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )
        save_btn = ttk.Button(
            row,
            text="Select",
            command=self.engine.on_export,
            width=8,
            bootstyle=OUTLINE,
        )
        save_btn.pack(side=LEFT, padx=5)

    def build_extract_range_row(self):
        row = ttk.Frame(self.option_lf)
        row.pack(fill=X, expand=YES, pady=10)

        ttk.Label(row, text="From Page:", width=self.lbl_width).pack(
            side=LEFT, padx=(15, 0)
        )
        self.engine.from_page_var = ttk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.engine.from_page_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

        ttk.Label(row, text="To Page:", width=8).pack(side=LEFT, padx=(15, 0))
        self.engine.to_page_var = ttk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.engine.to_page_var).pack(
            side=LEFT, fill=X, expand=YES, padx=5
        )

        # ttk.Label(row, text="Start counter:", width=8).pack(side=LEFT, padx=(15, 0))
        # self.engine.counter = ttk.StringVar(value="1")
        # ttk.Entry(row, textvariable=self.engine.counter).pack(
        #     side=LEFT, fill=X, expand=YES, padx=5
        # )

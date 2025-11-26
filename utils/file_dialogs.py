from tkinter.filedialog import askopenfilename, asksaveasfilename


def browse_file():
    return askopenfilename(filetypes=[("PDF files", "*.pdf")])


def save_file():
    return asksaveasfilename(
        defaultextension=".xlsx", filetypes=[("Excel File", "*.xlsx")]
    )

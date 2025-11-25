import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk


class PDFConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF Converter")

        # Cancel flag
        self.cancel_requested = False
        self.worker_thread = None

        # Input page range
        tk.Label(master, text="From page:").pack()
        self.from_page_var = tk.StringVar(value="1")
        tk.Entry(master, textvariable=self.from_page_var).pack()

        tk.Label(master, text="To page:").pack()
        self.to_page_var = tk.StringVar(value="5")
        tk.Entry(master, textvariable=self.to_page_var).pack()

        # Buttons
        self.convert_btn = tk.Button(
            master, text="Convert", command=self.start_conversion
        )
        self.convert_btn.pack(pady=5)

        self.cancel_btn = tk.Button(
            master, text="Cancel", state="disabled", command=self.cancel_conversion
        )
        self.cancel_btn.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(
            master, orient="horizontal", length=250, mode="determinate"
        )
        self.progress.pack(pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Waiting...")
        tk.Label(master, textvariable=self.status_var).pack(pady=5)

    # ----------------------------------------------------------------------
    # Start job in a background thread
    # ----------------------------------------------------------------------
    def start_conversion(self):
        # Reset states
        self.cancel_requested = False
        self.convert_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.status_var.set("Starting...")

        # Start worker
        self.worker_thread = threading.Thread(target=self.convert_job)
        self.worker_thread.start()

    # ----------------------------------------------------------------------
    # Cancel button
    # ----------------------------------------------------------------------
    def cancel_conversion(self):
        self.cancel_requested = True
        self.status_var.set("Cancelling...")

    # ----------------------------------------------------------------------
    # Worker thread job
    # ----------------------------------------------------------------------
    def convert_job(self):
        try:
            try:
                from_page = int(self.from_page_var.get())
                to_page = int(self.to_page_var.get())
            except:
                self.finish("Invalid page numbers!", error=True)
                return

            total_pages = max(1, to_page - from_page + 1)

            # Set progress bar max
            self.master.after(
                0, lambda: self.progress.config(maximum=total_pages, value=0)
            )

            for i, page in enumerate(range(from_page, to_page + 1), start=1):
                if self.cancel_requested:
                    self.finish("Conversion cancelled.")
                    return

                # Show status
                self.update_status(f"Processing page {page}...")

                # Simulate long work
                time.sleep(1)

                # Update progress bar (thread-safe)
                self.update_progress(i)

            self.finish("Conversion completed successfully!")

        except Exception as e:
            self.finish(f"Error: {e}", error=True)

    # ----------------------------------------------------------------------
    # Thread-safe UI updates
    # ----------------------------------------------------------------------
    def update_status(self, text):
        self.master.after(0, lambda: self.status_var.set(text))

    def update_progress(self, value):
        self.master.after(0, lambda: self.progress.config(value=value))

    # ----------------------------------------------------------------------
    # When job finishes: reset UI
    # ----------------------------------------------------------------------
    def finish(self, msg, error=False):
        def _finish():
            self.convert_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.status_var.set(msg)

            if error:
                messagebox.showerror("Error", msg)
            else:
                messagebox.showinfo("Status", msg)

        self.master.after(0, _finish)


# ------------------------------------------------------------------------------
# Run the App
# ------------------------------------------------------------------------------
root = tk.Tk()
app = PDFConverterApp(root)
root.mainloop()

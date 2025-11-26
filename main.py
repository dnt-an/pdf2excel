import ttkbootstrap as ttk

from gui.boq_engine import BoqExtractorEngine

if __name__ == "__main__":
    app = ttk.Window("BOQ Extractor", "journal")
    BoqExtractorEngine(app)
    app.mainloop()

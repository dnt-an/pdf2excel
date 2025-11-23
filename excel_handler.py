from dataclasses import dataclass, field

import xlsxwriter


@dataclass
class ExcelHandler:
    workbook: xlsxwriter.Workbook = field(init=False, default=None)
    worksheet: xlsxwriter.worksheet.Worksheet = field(init=False, default=None)

    def write_data(self, data: list, path: str):
        """
        Write structured Excel data from HangMuc objects, tuples, or strings.
        """
        self.workbook = xlsxwriter.Workbook(path)
        self.worksheet = self.workbook.add_worksheet()

        # ------------------- Formats -------------------
        header_format = self.workbook.add_format(
            {"bold": True, "bg_color": "#C6EFCE", "border": 1}
        )
        category_format = self.workbook.add_format(
            {"bold": True, "bg_color": "#DDEBF7"}
        )
        indent_format = self.workbook.add_format({"indent": 1})
        currency_format = self.workbook.add_format({"num_format": "#,##0.00"})

        # ------------------- Column Widths -------------------
        self.worksheet.set_column("A:A", 50)
        self.worksheet.set_column("B:B", 15)
        self.worksheet.set_column("C:C", 15)

        # ------------------- Write Header -------------------
        self.worksheet.write("A1", "Nội dung công việc", header_format)
        self.worksheet.write("B1", "Đơn vị", header_format)
        self.worksheet.write("C1", "Khối lượng", header_format)

        row = 1
        for item in data:
            # Determine category name and sub-tasks
            hang_muc = None
            cong_viec_list = []

            if hasattr(item, "ten_hang_muc") and hasattr(item, "cong_viec"):
                # It's a HangMuc object
                hang_muc = item.ten_hang_muc
                cong_viec_list = item.cong_viec
            elif isinstance(item, tuple) and len(item) > 0:
                # Possibly tuple containing HangMuc
                inner = item[0]
                if hasattr(inner, "ten_hang_muc") and hasattr(inner, "cong_viec"):
                    hang_muc = inner.ten_hang_muc
                    cong_viec_list = inner.cong_viec
                elif isinstance(inner, str):
                    hang_muc = inner
            elif isinstance(item, str):
                hang_muc = item

            if hang_muc is None:
                continue  # skip invalid items

            # Write category row
            self.worksheet.write(row, 0, hang_muc, category_format)
            self.worksheet.write(row, 1, "", category_format)
            self.worksheet.write(row, 2, "", category_format)
            row += 1

            # Write sub-tasks if any
            for job in cong_viec_list:
                self.worksheet.write(
                    row, 0, getattr(job, "noi_dung_cong_viec", ""), indent_format
                )
                self.worksheet.write(row, 1, getattr(job, "don_vi", ""))
                khoi_luong = getattr(job, "khoi_luong", None)
                if khoi_luong is not None:
                    self.worksheet.write(row, 2, khoi_luong, currency_format)
                else:
                    self.worksheet.write(row, 2, "")
                row += 1

            # Optional empty row
            row += 1

        self.workbook.close()

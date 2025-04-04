from collections import namedtuple

Formats=namedtuple("Formats",["CSV","EXCEL"])
formats=Formats(".csv",".xlsx")

class ConvertData:

    def __init__(self,format_:Formats,output_file_path:str):
        self.format_=format_
        self.output_file_path=output_file_path
        if not (format_==formats.CSV or format_==formats.EXCEL):
            raise ValueError("Invalid format!")

    def __save_csv__(self,df):
        # 🖫 Save Data as CSV file
        df.to_csv(f"{self.output_file_path}")

    def __save_excel__(self, df):
        # 🖫 Save Data as Excel file
        df.to_excel(f"{self.output_file_path}")

    def save(self, df):
        if self.format_ == formats.CSV:
            self.__save_csv__(df)
        elif self.format_ == formats.EXCEL:
            self.__save_excel__(df)
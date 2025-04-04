from collections import namedtuple

# Define a named tuple to represent supported file formats
Formats = namedtuple("Formats", ["CSV", "EXCEL"])
formats = Formats(".csv", ".xlsx")  # Supported formats: CSV and Excel

class ConvertData:
    """
    A utility class to save pandas DataFrames in different formats (CSV or Excel).
    """

    def __init__(self, format_: Formats, output_file_path: str):
        """
        Initialize the ConvertData instance.

        Parameters:
            format_ (Formats): The format in which the data will be saved (CSV or Excel).
            output_file_path (str): The path where the output file will be saved.

        Raises:
            ValueError: If the provided format is not supported.
        """
        self.format_ = format_  # File format (CSV or Excel)
        self.output_file_path = output_file_path  # Path to save the output file
        # Validate the format
        if not (format_ == formats.CSV or format_ == formats.EXCEL):
            raise ValueError("Invalid format!")  # Raise an error for unsupported formats

    def __save_csv__(self, df):
        """
        Save the DataFrame as a CSV file.

        Parameters:
            df (pandas.DataFrame): The DataFrame to be saved.
        """
        # 🖫 Save Data as CSV file
        df.to_csv(f"{self.output_file_path}")

    def __save_excel__(self, df):
        """
        Save the DataFrame as an Excel file.

        Parameters:
            df (pandas.DataFrame): The DataFrame to be saved.
        """
        # 🖫 Save Data as Excel file
        df.to_excel(f"{self.output_file_path}")

    def save(self, df):
        """
        Save the DataFrame in the specified format.

        Parameters:
            df (pandas.DataFrame): The DataFrame to be saved.

        Raises:
            ValueError: If the format is not supported.
        """
        if self.format_ == formats.CSV:
            self.__save_csv__(df)  # Save as CSV
        elif self.format_ == formats.EXCEL:
            self.__save_excel__(df)  # Save as Excel
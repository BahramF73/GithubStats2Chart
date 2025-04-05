import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QCheckBox, QPushButton, QLineEdit, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal

from data_processor import HandleData

class StreamToTextEdit:
    """
    Custom stream class to redirect stdout and stderr to a QLineEdit.
    """
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        if message.strip():  # Avoid writing empty lines
            self.text_edit.setText(message)

    def flush(self):
        pass  # Required for compatibility with sys.stdout and sys.stderr

class WorkerThread(QThread):
    """
    Worker thread to handle data processing in the background.
    """
    status_signal: pyqtSignal = pyqtSignal(str)
    data_signal: pyqtSignal = pyqtSignal(pd.DataFrame)

    def __init__(self, input_file, output_file, overwrite):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.overwrite = overwrite
        self.handle_data = None

    def run(self):
        try:
            # Create a HandleData instance and process the data
            self.handle_data = HandleData(
                input_file_path=self.input_file,
                output_file_path=self.output_file if not self.overwrite else self.input_file
            )
            print(f"Processing data from {self.input_file} to {self.output_file}...")

            # Get the DataFrame and emit it
            df = self.handle_data.save_data()  # Assuming this method returns a DataFrame
            self.data_signal.emit(df)

            # Emit a success message
            self.status_signal.emit(f"✅ Data saved as {self.handle_data.output_file_path}!")
        except Exception as e:
            # Emit an error message
            self.status_signal.emit(f"❌ Error: {e}")

def update_status(message):
    """
    Updates the output text box.
    """
    print(message)  # Redirected to the QLineEdit

class MainWindow(QMainWindow):
    """
    Main application window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GithubStats2Chart")
        self.worker_thread = None
        self.setMinimumSize(250, 250)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Overwrite checkbox
        self.overwrite_checkbox = QCheckBox("Overwrite")
        self.layout.addWidget(self.overwrite_checkbox)

        # Output text box
        self.output_text = QLineEdit()
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        # Redirect stdout and stderr to the QLineEdit
        sys.stdout = StreamToTextEdit(self.output_text)
        sys.stderr = StreamToTextEdit(self.output_text)

        # Table widget to display DataFrame
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        # Horizontal layout for the Start/Stop button
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        # Add a spacer item to push the button to the right
        self.button_layout.addStretch()

        # Start/Stop button
        self.start_button: QPushButton = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start_stop)
        self.start_button.setMaximumSize(100, 30)
        self.button_layout.addWidget(self.start_button)

        # Track application state
        self.app_is_running = False

    def on_start_stop(self):
        """
        Handles the Start/Stop button click.
        """
        if self.app_is_running:
            # Stop the worker thread
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.terminate()
            self.reset_ui()
            print("Stopped")
        else:
            # Start the worker thread
            self.app_is_running = True
            self.start_button.setText("Stop")
            self.overwrite_checkbox.setDisabled(True)

            input_file = "Book1"
            output_file = "Book1 new"
            overwrite = self.overwrite_checkbox.isChecked()

            self.worker_thread = WorkerThread(input_file, output_file, overwrite)
            self.worker_thread.status_signal.connect(update_status)
            self.worker_thread.data_signal.connect(self.update_table)
            self.worker_thread.finished.connect(self.reset_ui)  # Reset UI when thread finishes
            self.worker_thread.start()

    def update_table(self, df):
        """
        Populates the QTableWidget with data from the DataFrame.
        """
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])
        self.table_widget.setHorizontalHeaderLabels(df.columns)
        self.table_widget.setVerticalHeaderLabels(df.index)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))

    def reset_ui(self):
        """
        Resets the UI elements after the process is complete or stopped.
        """
        self.app_is_running = False
        self.start_button.setText("Start")
        self.overwrite_checkbox.setDisabled(False)

    def closeEvent(self, event):
        """
        Handles the application close event.
        """
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
        event.accept()

def main():
    """
    Entry point of the application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
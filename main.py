import sys
import concurrent.futures
from tkinter import Tk, ttk, BooleanVar, Checkbutton, Button, StringVar, Entry, Text
from data_processor import HandleData

# Global variable to hold the HandleData instance
handle_data: HandleData = None
app_is_running: bool = False  # Flag to indicate if the application is running

class TextRedirector:
    """
    A class to redirect stdout to a Tkinter Text widget, showing only the latest line.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        if text.strip():  # Only update if there's actual text
            self.text_widget.delete("1.0", "end")  # Clear the widget
            self.text_widget.insert("end", text.strip())  # Insert the latest text
            self.text_widget.see("end")  # Scroll to the end

    def flush(self):
        pass  # Required for compatibility with Python's stdout

# Function to run the data handling process
def run_handle_data(input_file, output_file, start_button, status_var):
    """
    Initializes the HandleData instance and saves the processed data.
    """
    global handle_data
    try:
        # Create a HandleData instance with the given input and output file paths
        handle_data = HandleData(input_file_path=input_file, output_file_path=output_file)
        # Save the processed data
        handle_data.save_data()
        # Print a success message
        print(f"✅ Data has been updated and saved as {handle_data.output_file_path}!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        # Update the button text and status after processing is complete
        start_button.config(text="Start")
        status_var.set("Ready")

# Function to start the data processing in a separate thread
def start_data_processing(executor, input_file, output_file, start_button, status_var):
    """
    Submits the data processing task to the ThreadPoolExecutor.
    """
    executor.submit(run_handle_data, input_file, output_file, start_button, status_var)
    
# Main function to set up the GUI and application logic
def main():
    """
    Sets up the Tkinter GUI and handles application logic.
    """
    root = Tk()  # Create the main Tkinter window
    root.title("GithubStats2Chart")  # Set the window title
    frm = ttk.Frame(root, padding=10, height=100, width=400)  # Create a frame for layout
    frm.grid()  # Add the frame to the window

    # Boolean variable to track the "Overwrite" checkbox state
    overwrite_var = BooleanVar()
    # Create a checkbox for the "Overwrite" option
    overwrite_check = Checkbutton(frm, text="Overwrite", variable=overwrite_var)
    overwrite_check.grid(column=0, row=0)  # Place the checkbox in the grid

    # Create a StringVar to hold the status text
    status_var = StringVar()
    status_var.set("Ready")  # Set the initial status text

    # Create a one-line text box to display the status
    status_entry = Entry(frm, textvariable=status_var, state="readonly", width=50)
    status_entry.grid(column=0, row=1, columnspan=2)  # Place the text box in the grid

    # Create a single-line text box to display terminal output
    output_text = Text(frm, height=1, width=50, state="normal", wrap="none")
    output_text.grid(column=0, row=3, columnspan=2)  # Place the text box in the grid

    # Redirect stdout to the Text widget
    sys.stdout = TextRedirector(output_text)

    # Create a ThreadPoolExecutor for running tasks in the background
    executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="daemon")

    # Function to handle the "Start" button click
    def on_start_stop():
        """
        Starts and stops the data processing task when the button is clicked.
        """
        global handle_data, app_is_running
        if app_is_running:
            # If the process is already running, stop it
            handle_data.stop()
            handle_data = None
            app_is_running = False
            start_button.config(text="Start")
            status_var.set("Stopped")  # Update the status text
        else:
            app_is_running = True
            start_button.config(text="Stop")  # Change button text to "Stop"
            input_file = "Book1"  # Default input file name
            output_file = "Book1 new"  # Default output file name
            # If "Overwrite" is checked, use the input file name as the output file name
            if overwrite_var.get():
                output_file = input_file
            # Start the data processing task
            status_var.set("Processing...")
            start_data_processing(executor, input_file, output_file, start_button, status_var)

    # Create a "Start" button and bind it to the on_start function
    start_button = Button(frm, text="Start", command=on_start_stop)
    start_button.grid(column=0, row=2)  # Place the button in the grid

    # Function to handle the application closing event
    def on_closing():
        """
        Handles cleanup when the application window is closed.
        """
        if handle_data is not None:
            # Call the shutdown method of HandleData if it exists
            handle_data.stop()
        # Shut down the ThreadPoolExecutor
        executor.shutdown(wait=False)
        # Restore stdout to its original state
        sys.stdout = sys.__stdout__
        # Destroy the Tkinter window
        root.destroy()

    # Bind the on_closing function to the window close event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter main loop
    root.mainloop()

# Entry point of the application
if __name__ == "__main__":
    main()
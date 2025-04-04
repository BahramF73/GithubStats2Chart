import concurrent.futures
from tkinter import Tk, ttk, BooleanVar, Checkbutton, Button
from data_processor import HandleData

# Global variable to hold the HandleData instance
handle_data: HandleData = None
app_is_running: bool = False  # Flag to indicate if the application is running

# Function to run the data handling process
def run_handle_data(input_file, output_file):
    """
    Initializes the HandleData instance and saves the processed data.
    """
    global handle_data
    # Create a HandleData instance with the given input and output file paths
    handle_data = HandleData(input_file_path=input_file, output_file_path=output_file)
    # Save the processed data
    handle_data.save_data()
    # Print a success message
    print(f"\n✅ Data has been updated and saved as {handle_data.output_file_path}!")

# Function to start the data processing in a separate thread
def start_data_processing(executor, input_file, output_file):
    """
    Submits the data processing task to the ThreadPoolExecutor.
    """
    executor.submit(run_handle_data, input_file, output_file)

# Main function to set up the GUI and application logic
def main():
    """
    Sets up the Tkinter GUI and handles application logic.
    """
    root = Tk()  # Create the main Tkinter window
    frm = ttk.Frame(root, padding=10, height=100, width=100)  # Create a frame for layout
    frm.grid()  # Add the frame to the window

    # Boolean variable to track the "Overwrite" checkbox state
    overwrite_var = BooleanVar()
    # Create a checkbox for the "Overwrite" option
    overwrite_check = Checkbutton(frm, text="Overwrite", variable=overwrite_var)
    overwrite_check.grid(column=0, row=0)  # Place the checkbox in the grid

    # Create a ThreadPoolExecutor for running tasks in the background
    executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="daemon")

    # Function to handle the "Start" button click
    def on_start_stop():
        """
        Starts and stop the data processing task when the button is clicked.
        """
        global handle_data, app_is_running
        if app_is_running:
            # If the process is already running, stop it
            handle_data.stop()
            handle_data = None
            app_is_running = False
            start_button.config(text="Start")
        else:
            app_is_running = True
            start_button.config(text="Stop")  # Change button text to "Stop"
            input_file = "Book1"  # Default input file name
            output_file = "Book1 new"  # Default output file name
            # If "Overwrite" is checked, use the input file name as the output file name
            if overwrite_var.get():
                output_file = input_file
            # Start the data processing task
            start_data_processing(executor, input_file, output_file)

    # Create a "Start" button and bind it to the on_start function
    start_button = Button(frm, text="Start", command=on_start_stop)
    start_button.grid(column=0, row=1)  # Place the button in the grid

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
        # Destroy the Tkinter window
        root.destroy()

    # Bind the on_closing function to the window close event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter main loop
    root.mainloop()

# Entry point of the application
if __name__ == "__main__":
    main()
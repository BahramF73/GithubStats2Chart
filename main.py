import concurrent.futures
from tkinter import Tk, ttk, BooleanVar, Checkbutton, Button
from data_processor import HandleData

handle_data:HandleData= None

def run_handle_data(input_file, output_file):
    global handle_data
    handle_data = HandleData(input_file_path=input_file, output_file_path=output_file)
    handle_data.save_data()
    print(f"\n✅ Data has been updated and saved as {handle_data.output_file_path}!")

def start_data_processing(executor, input_file, output_file):
    executor.submit(run_handle_data, input_file, output_file)

def main():
    root = Tk()
    frm = ttk.Frame(root, padding=10, height=100, width=100)
    frm.grid()

    overwrite_var = BooleanVar()
    overwrite_check = Checkbutton(frm, text="Overwrite", variable=overwrite_var)
    overwrite_check.grid(column=0, row=0)

    executor = concurrent.futures.ThreadPoolExecutor()

    def on_start():
        input_file = "Book1"
        output_file = "Book1 new"
        if overwrite_var.get():
            output_file = input_file
        start_data_processing(executor, input_file, output_file)

    start_button = Button(frm, text="Start", command=on_start)
    start_button.grid(column=0, row=1)

    def on_closing():
        if handle_data is not None:
            handle_data.shutdown()
        executor.shutdown(wait=False)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()
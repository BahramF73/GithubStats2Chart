# GithubStats2Chart

A Python tool that collects GitHub repository traffic data, including clones (and later, views), and saves them in an Excel spreadsheet for tracking and analysis.

## ✅ Current Features

📊 Retrieves clone statistics for public repositories

📂 Stores data in a CSV file

🔄 Automatically updates stats

📈 Improving data organization

📊 Potentially adding charts for visualization

## 🚀 Planned Enhancements

- [ ] Adding view count tracking
- [ ] Improving data organization
- [ ] Storing data in an Excel sheet for easy access

***This tool is ideal for developers who want to monitor their repository traffic efficiently. Contributions and feedback are welcome!*** 😊

## Requirements

- Python 3.8+
- PyQt6
- pandas
- numpy
- python-dotenv
- PyGithub

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/BahramF73/GithubStats2Chart.git
    cd GithubStats2Chart
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your GitHub token:
    ```env
    GITHUB_TOKEN=your_github_token
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```

2. Use the GUI to start and stop data retrieval. The data will be displayed in a table and saved to the specified output file.

## Project Structure

- `main.py`: Entry point of the application. Contains the GUI implementation.
- `data_processor/convert_data.py`: Contains the `ConvertData` class for saving data in different formats.
- `data_processor/data_handler.py`: Contains the `HandleData` class for retrieving and processing data from GitHub.
- `data_processor/__init__.py`: Initializes the `data_processor` package.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

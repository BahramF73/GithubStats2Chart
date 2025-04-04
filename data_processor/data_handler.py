import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from github import Auth, Github
from .convert_data import Formats, ConvertData, formats


def check_env():
    """
    Load the GitHub token from the environment variables.
    """
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")


class HandleData:
    """
    This Library gets data from GitHub and provides a pandas.DataFrame of Clones or Views.
    """

    def __init__(self, input_file_path: str = "", output_file_path: str = "output", format_: Formats = formats.CSV, token: str = None,
                 period: int = 13):
        """
        Parameters:
            input_file_path (str): Path of existing data.
            output_file_path (str): Path of where your data will be saved.
            token (str): Your GitHub Token.
            period (int): The period you want to get data for (default is 13). '1 <= period <= 14'.

        Returns:
            None: This function does not return any value.
        """
        self.input_file_path = f"{input_file_path}{format_}"  # Input file path with format
        self.output_file_path = f"{output_file_path}{format_}"  # Output file path with format
        self.token = token
        self.format_ = format_
        if self.token is None:
            self.token = check_env()  # Load token from environment if not provided
            if self.token is None:
                print("No token found")
        self.auth = Auth.Token(self.token)  # Authenticate with GitHub
        self.g = Github(auth=self.auth)  # Create a GitHub API client
        self.period = period  # Period for retrieving data
        self.app_is_running = True  # Flag to indicate if the application is running

    def __convert_date__(self) -> list[str]:
        """
        Generate a list of dates for the specified period.

        Returns:
            list[str]: List of date strings.
        """
        today = datetime.now()
        start_date = today - timedelta(days=self.period)
        date_strs = [d.strftime("%Y-%m-%d") for d in pd.date_range(start=start_date, end=today, freq="D")]
        return date_strs

    def __get_local_data__(self) -> pd.DataFrame:
        """
        Get local data if it exists or return an empty pandas.DataFrame.

        Returns:
            pandas.DataFrame: The local data or an empty DataFrame.
        """
        df = pd.DataFrame()  # Initialize an empty DataFrame
        try:
            # Attempt to read the input file
            df = pd.read_csv(f"{self.input_file_path}", index_col=0)
        except (pd.errors.EmptyDataError, FileNotFoundError):
            print(f"File: {self.input_file_path} does not exist or is corrupted!")

        # Add missing dates to the DataFrame
        for date in self.__convert_date__():
            if date not in df.columns:
                df[date] = 0
        return df

    def __get_data__(self) -> pd.DataFrame | None:
        """
        Retrieve clone data from GitHub and update the DataFrame.

        Returns:
            pandas.DataFrame | None: Updated DataFrame or None if shutdown is triggered.
        """
        df = self.__get_local_data__()  # Load local data
        for repo in self.g.get_user().get_repos():
            if self.app_is_running is False:
                # Stop processing if the application is shutting down
                print("❌ Application is shutting down...")
                exit(0)
            if repo.private:
                # Skip private repositories
                continue

            print(f"🔍 Retrieving data for repository: {repo.name}...")

            try:
                # Get clone traffic data for the repository
                clone_data = repo.get_clones_traffic(per="day")
                if not clone_data or "clones" not in clone_data.raw_data:
                    print(f"  ->  -> ⚠ Clone data for {repo.name} is not available. <-  <-")
                    continue

                # Create a dictionary of clone counts by date
                clone_count = {str(data["timestamp"])[:10]: data["count"] for data in clone_data.raw_data["clones"]}
                if repo.name not in df.index:
                    # Add new repositories to the DataFrame
                    print(f"  ->  -> ⚠ New repository ({repo.name}) detected, updating data... <-  <-")
                    df.loc[repo.name] = 0

                # Update the repository data in the DataFrame
                for date in self.__convert_date__():
                    if date in clone_count:
                        df.at[repo.name, date] = clone_count[date]

                # Replace all NaN values with 0
                df = df.fillna(0).astype(np.int16)

            except Exception as e:
                # Handle errors during data retrieval
                print(f"  ->  -> ❌ Error retrieving data for {repo.name}: {e} <-  <-")
        return df

    def save_data(self):
        """
        Save the retrieved data to the specified output file.

        Returns:
            None
        """
        if self.app_is_running is False:
            # Stop saving if the application is shutting down
            print("❌ Application is shutting down...")
            exit(0)
        df = self.__get_data__()  # Retrieve data
        if df is not None:
            # Save the data using the specified format
            converter = ConvertData(format_=self.format_, output_file_path=f"{self.output_file_path}")
            converter.save(df)
        self.g.close()  # Close the GitHub API client

    def shutdown(self):
        """
        Gracefully shut down the data handler by stopping ongoing processes.
        """
        self.app_is_running = False  # Set the running flag to False
        self.g.close()  # Close the GitHub API client
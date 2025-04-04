import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from github import Auth, Github
from .convert_data import Formats, ConvertData,formats


def check_env():
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")


class HandleData:
    """
    This Library get data from GitHub and give us and pandas.DataFrame of Clones or Views
    """

    def __init__(self, input_file_path: str = "", output_file_path: str = "output",format_:Formats=formats.CSV, token: str = None,
                 period: int = 13):
        """
        Parameter:
            input_file_path (str): Path of existed data
            output_file_path (str): Path of where your data will save
            token (str): Your GitHub Token
            period (int): The period you want get data.(default is 13) '1 <= period <= 14'

        Return:
            None: This function does not return any value.

        Example:
            greet("ABCD1234", 13)
        """
        self.input_file_path = f"{input_file_path}{format_}"
        self.output_file_path = f"{output_file_path}{format_}"
        self.token = token
        self.format_ = format_
        if self.token is None:
            self.token = check_env()
            if self.token is None:
                print("No token found")
        self.auth = Auth.Token(self.token)
        self.g = Github(auth=self.auth)
        self.period = period
        self.app_is_running = True

    def __convert_date__(self) -> list[str]:
        """

        Return: list[str]
        """
        today = datetime.now()
        start_date = today - timedelta(days=self.period)
        date_strs = [d.strftime("%Y-%m-%d") for d in pd.date_range(start=start_date, end=today, freq="D")]
        return date_strs

    def __get_local_data__(self) -> pd.DataFrame:
        """
        Get local data if exists or return empty pandas.DataFrame

        Return: pandas.DataFrame
        """
        # 📂 Attempt to open the CSV file
        df = pd.DataFrame()
        try:
            df = pd.read_csv(f"{self.input_file_path}", index_col=0)
        except (pd.errors.EmptyDataError, FileNotFoundError):
            print(f"File: {self.input_file_path} does not exists or is corrupted!")

        # ✨ Check and add new dates to DataFrame
        for date in self.__convert_date__():
            if date not in df.columns:
                df[date] = 0
        return df

    def __get_data__(self)-> pd.DataFrame | None:
        # 📊 Retrieve clone data from GitHub
        # Loop checks each repo one by one
        df=self.__get_local_data__()
        for repo in self.g.get_user().get_repos():
            if self.app_is_running is False:
                print("❌ Application is shutting down...")
                exit(0)
            if repo.private:
                continue

            print(f"🔍 Retrieving data for repository: {repo.name}...")

            try:
                clone_data = repo.get_clones_traffic(per="day")
                if not clone_data or "clones" not in clone_data.raw_data:
                    print(f"  ->  -> ⚠ Clone data for {repo.name} is not available. <-  <-")
                    continue

                # Create object of clone count {"date":count, "date":count, ....}
                clone_count = {str(data["timestamp"])[:10]: data["count"] for data in clone_data.raw_data["clones"]}
                if repo.name not in df.index:
                    # If repository is not in the DataFrame add it and set counts 0
                    print(f"  ->  -> ⚠ New repository ({repo.name}) detected, updating data... <-  <-")
                    df.loc[repo.name] = 0

                # Update the repository data
                for date in self.__convert_date__():
                    if date in clone_count:
                        df.at[repo.name, date] = clone_count[date]

                # Replace All NaN values with 0
                df=df.fillna(0).astype(np.int16)

            except Exception as e:
                print(f"  ->  -> ❌ Error retrieving data for {repo.name}: {e} <-  <-")
        return df
    def save_data(self):
        if self.app_is_running is False:
                print("❌ Application is shutting down...")
                exit(0)
        df = self.__get_data__()
        if df is not None:
            converter = ConvertData(format_=self.format_, output_file_path=f"{self.output_file_path}")
            converter.save(df)
        self.g.close()
    
    def shutdown(self):
        self.app_is_running = False
        self.g.close()
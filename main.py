import os
from github import Github
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Authentication is defined via GitHub.Auth
from github import Auth

# Retrieve token from environment variable
load_dotenv()
# Using an access token
auth = Auth.Token(os.getenv("GITHUB_TOKEN"))

# Set input and output files name
input_file_path = "Book1.csv"
output_file_path = "Book1 new.csv"

# Authenticate with GitHub
g = Github(auth=auth)

# 📅 Define the time range for retrieving data (last 13 days)
today = datetime.now()
start_date = today - timedelta(days=13)  # Only the last 13 days
date_strs = [d.strftime("%Y-%m-%d") for d in pd.date_range(start=start_date, end=today, freq="D")]


# 📂 Attempt to open the CSV file
try:
    df=pd.read_csv(input_file_path, index_col=0)
except (pd.errors.EmptyDataError, FileNotFoundError):
    print(f"File: {input_file_path} does not exists or is corrupted!")
    df=pd.DataFrame()

# ✨ Check and add new dates to DataFrame
for date in date_strs:
    if date not in df.columns:
        df[date] = 0


# 📊 Retrieve clone data from GitHub
# Loop checks each repo one by one
for repo in g.get_user().get_repos():
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
            df.loc[repo.name]=0

        # Update the repository data
        for date in date_strs:
            if date in clone_count:
                df.at[repo.name, date] = clone_count[date]

    except Exception as e:
        print(f"  ->  -> ❌ Error retrieving data for {repo.name}: {e} <-  <-")

# Replace All NaN values with 0
df=df.fillna(0).astype(np.int16)

# 🖫 Save Data as CSV file
df.to_csv(output_file_path)

g.close()

print(f"\n✅ Data has been updated and saved as {output_file_path}!")
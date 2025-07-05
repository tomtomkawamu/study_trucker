import pandas as pd
from safety import safe_json_loads

DATA_FILE = "study_data.csv"

def category_eng(category):
    mapping = {
        "芸術": "Art",
        "音楽": "Music",
        "アカデミック": "Academic",
        "スポーツ": "Sports",
        "総合": "Overall"
    }
    return mapping.get(category, category)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_data():
    try:
        return pd.read_csv(DATA_FILE, converters={"additional_info": safe_json_loads})
    except FileNotFoundError:
        return pd.DataFrame(columns=["category", "type", "name", "time", "xp", "date", "additional_info"])

def delete_entry(index):
    data = load_data()
    data = data.drop(index).reset_index(drop=True)
    save_data(data)
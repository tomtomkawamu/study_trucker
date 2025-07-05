import pandas as pd
import datetime


def prepare_effectiveness_dataset(df):
    df = df.copy()

    # time を分に変換（例: "00:25:00" → 25）
    df["elapsed_minutes"] = pd.to_timedelta(df["time"]).dt.total_seconds() / 60

    # 日付から曜日と時刻を抽出
    df["date"] = pd.to_datetime(df["date"])
    df["weekday"] = df["date"].dt.weekday  # 0=月曜
    df["hour"] = df["date"].dt.hour if "hour" in df["date"].dt else 12  # 時間帯（記録があれば）

    # 必要な列だけ抽出
    features = df[["elapsed_minutes", "xp", "weekday", "hour"]]
    labels = df["effectiveness"]

    return features, labels
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import joblib
from ml.utils import prepare_effectiveness_dataset

def train_model():
    # CSVまたは既存の保存データを読み込み
    df = pd.read_csv("study_data.csv")  # または save_data() したCSV

    # 前処理
    X, y = prepare_effectiveness_dataset(df)

    # データ分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # モデル学習
    model = XGBRegressor()
    model.fit(X_train, y_train)

    # 精度確認
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f"RMSE: {rmse:.2f}")

    # モデル保存
    joblib.dump(model, "effectiveness_model.pkl")
    print("✅ モデルが保存されました")
import streamlit as st
import pandas as pd
from utils import load_data, delete_entry, save_data

class HistoryCaller:

    def __init__(self, data):
        self.data = data

    def history_loader(self):
        # カレンダー表示（ユーザーに日付を選んでもらう）
        selected_date = st.date_input("日付を選択", pd.to_datetime('today').date())

        if self.data.empty:
            st.write("記録がありません。")
        else:
            # カテゴリ選択（"総合" ならすべて表示）
            category_list = ["総合"] + list(self.data["category"].unique())
            selected_category = st.selectbox("履歴を表示するカテゴリを選択", category_list)

            # カテゴリでフィルタ
            filtered_data = self.data if selected_category == "総合" else self.data[
                self.data["category"] == selected_category]

            # 日付列を整形してグルーピング
            filtered_data["date"] = pd.to_datetime(filtered_data["date"]).dt.date

            # 選択した日付に基づく履歴を表示
            selected_day_data = filtered_data[filtered_data["date"] == selected_date]
            if not selected_day_data.empty:
                st.subheader(f"{selected_date} の記録")
                for i, row in selected_day_data.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    with col1:
                        st.write(f"🎯 カテゴリ: {row['category']}")
                    with col2:
                        st.write(f"📝 タイプ: {row['type']}")
                    with col3:
                        st.write(f"🏅 XP: {row['xp']}")
                    with col4:
                        if st.button("削除", key=f"delete_{i}"):
                            self.data.drop(index=i, inplace=True)
                            self.data.reset_index(drop=True, inplace=True)
                            save_data(self.data)
                            st.success("削除されました")
                            st.rerun()
            else:
                st.write(f"{selected_date} の記録はありません。")

            # テーブルでも確認用に表示
            st.subheader("テーブル表示")
            st.dataframe(filtered_data.reset_index(drop=True), height=300)

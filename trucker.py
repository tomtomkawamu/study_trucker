import streamlit as st

from information_getter.book_info import get_book_info
import datetime
import joblib

from ml.train_model import train_model
from timer import format_time, update_timer
from utils import save_data
from information_getter.anime.anime_info import completed_anime_info, completed_manga_info
from information_getter.movie_info import get_movie_info
import time
import pandas as pd
import json

class Trucker:

    def __init__(self, data):
        self.data = data

    def data_trucker(self, target_category=None):

        category_options = ["芸術", "音楽", "アカデミック", "スポーツ"]
        if target_category:
            category = target_category
        else:
            category = st.selectbox("カテゴリを選択", category_options)

        if category == "アカデミック":
            AcademicTrucker(data=self.data).generate_data()
        elif category == "音楽":
            MusicTrucker(data=self.data).generate_data()
        elif category == "スポーツ":
            SportsTrucker(data=self.data).generate_data()
        elif category == "芸術":
            st.subheader("芸術の記録")
            type_ = st.selectbox("タイプ", ["映画", "本", "アニメ", "漫画"])
            if type_ == "映画":
                MovieTrucker(data=self.data, art_type=type_).generate_data()
            elif type_ == "本":
                BookTrucker(data=self.data, art_type=type_).generate_data()
            elif type_ == "アニメ":
                AnimeTrucker(data=self.data, art_type=type_).generate_data()
            elif type_ == "漫画":
                MangaTrucker(data=self.data, art_type=type_).generate_data()

class AcademicTrucker:

    def __init__(self, data):
        self.data = data

    # 効果予測モデルの読み込み
    @st.cache_resource
    def load_effectiveness_model(self):
        return joblib.load("effectiveness_model.pkl")

    # 特徴量を作成（簡略バージョン、実際はStep2と同じように整える）
    def prepare_single_input(self, name, elapsed_time):
        return pd.DataFrame({
            "name_length": [len(name)],
            "elapsed_time": [elapsed_time],
            "hour": [datetime.now().hour],
            "dayofweek": [datetime.now().weekday()]
        })

    def generate_data(self):
        category = "アカデミック"
        st.subheader(f"{category}の記録")
        name = st.text_input("学習/練習内容", key=category)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("開始", key=f"{category}_start") and not st.session_state.timer_running:
                st.session_state.timer_start_time = time.time()
                st.session_state.timer_running = True
                st.session_state.paused_time = 0
                st.session_state.pause_start_time = None
                st.session_state.elapsed_time = 0
                st.session_state.message = "タイマーが開始されました！"
                update_timer()
        with col2:
            if st.button("休憩", key=f"{category}_pause") and st.session_state.timer_running and st.session_state.pause_start_time is None:
                st.session_state.pause_start_time = time.time()
                st.session_state.timer_running = False
                st.session_state.message = "少女祈祷中..."
        with col3:
            if st.button("再開", key=f"{category}_restart") and st.session_state.pause_start_time is not None:
                st.session_state.paused_time += time.time() - st.session_state.pause_start_time
                st.session_state.pause_start_time = None
                st.session_state.timer_running = True
                st.session_state.message = "タイマーを再開しました！"
                update_timer()
        with col4:
            if st.button("停止", key=f"{category}_stop"):
                elapsed_time = int(
                    time.time() - st.session_state.timer_start_time - st.session_state.paused_time)
                st.session_state.timer_running = False
                st.session_state.elapsed_time = elapsed_time
                xp = elapsed_time / 5

                # ユーザー入力による効果スコア
                effectiveness_score = st.slider("この学習の効果実感（主観評価）", 1, 5, 3)

                #if st.button("モデルを再学習する"):
                    #train_model()
                    #st.success("モデルの再学習が完了しました！")

                # --- モデルを用いて効果を予測 ---
                #model = self.load_effectiveness_model()
                #input_df = self.prepare_single_input(name, elapsed_time)
                #effectiveness_score = model.predict(input_df)[0]

                new_data = pd.DataFrame({
                    "category": [category],
                    "type": ["勉強"],
                    "name": [name],
                    "time": [format_time(elapsed_time)],
                    "xp": [xp],
                    "date": [pd.Timestamp.today().normalize().date()],
                    "effectiveness": effectiveness_score, #[effectiveness_score],  # 効果スコアを追加
                    "additional_info": [json.dumps({})]
                })
                data = pd.concat([self.data, new_data], ignore_index=True)
                save_data(data)
                st.session_state.message = f"{format_time(elapsed_time)} 分間の記録が保存されました！"
                st.info(f"📈 推定された学習効果スコア: **{effectiveness_score:.2f}**")

            if "message" in st.session_state:
                st.success(st.session_state.message)

class MusicTrucker:

    def __init__(self, data):
        self.data = data

    def generate_data(self):
        category = "音楽"
        st.subheader(f"{category}の記録")
        name = st.text_input("学習/練習内容", key=category)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("開始", key=f"{category}_start") and not st.session_state.timer_running:
                st.session_state.timer_start_time = time.time()
                st.session_state.timer_running = True
                st.session_state.paused_time = 0
                st.session_state.pause_start_time = None
                st.session_state.elapsed_time = 0
                st.session_state.message = "タイマーが開始されました！"
                update_timer()
        with col2:
            if st.button("休憩", key=f"{category}_pause") and st.session_state.timer_running and st.session_state.pause_start_time is None:
                st.session_state.pause_start_time = time.time()
                st.session_state.timer_running = False
                st.session_state.message = "少女祈祷中..."
        with col3:
            if st.button("再開", key=f"{category}_restart") and st.session_state.pause_start_time is not None:
                st.session_state.paused_time += time.time() - st.session_state.pause_start_time
                st.session_state.pause_start_time = None
                st.session_state.timer_running = True
                st.session_state.message = "タイマーを再開しました！"
                update_timer()
        with col4:
            if st.button("停止", key=f"{category}_stop"):
                elapsed_time = int(
                    time.time() - st.session_state.timer_start_time - st.session_state.paused_time)
                st.session_state.timer_running = False
                st.session_state.elapsed_time = elapsed_time
                xp = elapsed_time / 10

                new_data = pd.DataFrame({
                    "category": [category],
                    "type": ["音楽練習"],
                    "name": [name],
                    "time": [format_time(elapsed_time)],
                    "xp": [xp],
                    "date": [pd.Timestamp.today().normalize().date()],
                    "additional_info": [json.dumps({})]
                })
                data = pd.concat([self.data, new_data], ignore_index=True)
                save_data(data)
                st.session_state.message = f"{format_time(elapsed_time)} 分間の記録が保存されました！"

            if "message" in st.session_state:
                st.success(st.session_state.message)

class SportsTrucker:

    def __init__(self, data):
        self.data = data

    def generate_data(self):
        category = "スポーツ"
        st.subheader(f"{category}の記録")
        name = st.text_input("スポーツ名", key=category)
        count = st.number_input("回数", min_value=1, step=1)
        if st.button("回数記録", key=f"{category}_count"):
            xp = count * 50
            new_data = pd.DataFrame({
                "category": [category],
                "type": ["筋トレ"],
                "name": [name],
                "time": [0],
                "xp": [xp],
                "date": [pd.Timestamp.today()],
                "additional_info": [json.dumps({})]
            })
            data = pd.concat([self.data, new_data], ignore_index=True)
            save_data(data)
            st.success(f"{count} 回の運動が記録されました！")

class ArtTrucker:

    def __init__(self, data, art_type):
        self.data = data
        self.art_type = art_type

    def generate_data(self):
        pass

    def art_info_save(self, type_, name, xp, additional_info):
        if st.button("データを保存"):

            myanimelist_found = False

            if type_ == "アニメ":
                for index, record in self.data.iterrows():
                    if record["name"] == "myanimelist":
                        self.data.loc[index, "xp"] = xp
                        self.data.loc[index, "date"] = pd.Timestamp.today().normalize().date()
                        myanimelist_found = True
                        st.success("データを更新しました！")
                        break
            elif type_ == "漫画":
                for index, record in self.data.iterrows():
                    if record["name"] == "myanimelist_manga":
                        self.data.loc[index, "xp"] = xp
                        self.data.loc[index, "date"] = pd.Timestamp.today().normalize().date()
                        myanimelist_found = True
                        st.success("データを更新しました！")
                        break

            if not myanimelist_found:
                new_data = pd.DataFrame({
                    "category": ["芸術"],
                    "type": [type_],
                    "name": [name],
                    "time": [0],
                    "xp": [xp],
                    "date": [pd.Timestamp.today().normalize().date()],
                    "additional_info": [json.dumps(additional_info)]
                })
                self.data = pd.concat([self.data, new_data], ignore_index=True)
                st.success("データを保存しました！")
            save_data(self.data)

class MovieTrucker(ArtTrucker):

    def __init__(self, data, art_type="映画"):
        super().__init__(data, art_type)

    def generate_data(self):
        additional_info = {}
        name = st.text_input("作品名")
        if st.button("映画情報を取得"):
            info = get_movie_info(name)
            if info:
                additional_info.update(info)
                st.write(f"公開年: {info['公開年']}, 監督: {info['監督']}")
            else:
                st.error("映画情報が見つかりませんでした")
        additional_info["重要度"] = st.slider("重要度", 1.0, 5.0, 3.0)
        xp = int(additional_info["重要度"] * 30)
        self.art_info_save(self.art_type, name, xp, additional_info)

class AnimeTrucker(ArtTrucker):

    def __init__(self, data, art_type="アニメ"):
        super().__init__(data, art_type)

    def generate_data(self):
        st.title("アニメ視聴トラッカー")
        anime_list = completed_anime_info()
        if anime_list:
            total_xp = sum(anime["XP"] for anime in anime_list)
            st.write(f"総獲得XP: {total_xp}")
            self.art_info_save(self.art_type, name="myanimelist", xp=total_xp, additional_info=None)

            for anime in anime_list:
                # 横並びに配置
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])  # カラムの幅を指定

                with col1:
                    st.image(anime['画像'], width=150)  # 画像表示

                with col2:
                    st.write(f"**{anime['タイトル']}** ({anime['放送年']})")  # タイトルと放送年
                    # st.write(f"ジャンル: {anime['ジャンル']}")  # 種類
                    st.write(f"種類: {anime['種類']}")  # 種類
                    st.write(f"話数: {anime['話数']}")  # 話数

                with col3:
                    st.write(f"スコア: {anime['スコア']}")  # スコア
                    st.write(f"自身のスコア: {anime['自身のスコア']}")  # 自身のスコア

                with col4:
                    # 他の情報を表示
                    st.write(f"獲得XP: {anime['XP']}")  # 獲得XP
                    # st.write(f"追加情報: {anime.get('追加情報', 'なし')}")  # 追加情報
        else:
            st.write("視聴済みアニメが見つかりませんでした。")

class MangaTrucker(ArtTrucker):

    def __init__(self, data, art_type="漫画"):
        super().__init__(data, art_type)

    def generate_data(self):
        st.title("マンガ読書トラッカー")
        manga_list = completed_manga_info()
        if manga_list:
            total_xp = sum(manga["XP"] for manga in manga_list)
            st.write(f"総獲得XP: {total_xp}")
            self.art_info_save(self.art_type, name="myanimelist_manga", xp=total_xp, additional_info=None)

            for manga in manga_list:
                # 横並びに配置
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])  # カラムの幅を指定

                with col1:
                    st.image(manga['画像'], width=150)  # 画像表示
                with col2:
                    st.write(f"**{manga['タイトル']}** ({manga['開始年']})")  # タイトルと開始年
                    st.write(f"種類: {manga['巻数']}")  # 巻数
                    st.write(f"話数: {manga['話数']}")  # 話数
                with col3:
                    st.write(f"スコア: {manga['スコア']}")  # スコア
                    st.write(f"獲得XP: {manga['XP']}")  # 獲得XP

                with col4:
                    # 他の情報を表示
                    st.write(f"追加情報: {manga.get('追加情報', 'なし')}")  # 追加情報
        else:
            st.write("読了済みマンガが見つかりませんでした。")

class BookTrucker(ArtTrucker):

    def __init__(self, data, art_type="本"):
        super().__init__(data, art_type)

    def generate_data(self):
        st.title("読書トラッカー")
        book_title = st.text_input("書籍タイトルを入力")

        if st.button("書籍情報を取得") and book_title:
            info = get_book_info(book_title)
            if info:
                st.subheader(info["タイトル"])
                st.write(f"著者: {info['著者']}")
                st.write(f"出版年: {info['出版年']}")
                st.write(f"ページ数: {info['ページ数']} ページ")
                st.write(f"説明: {info['説明'][:300]}...")
                if info["画像"]:
                    st.image(info["画像"], width=150)

                xp = info["ページ数"] * 2 if isinstance(info["ページ数"], int) else 0
                st.write(f"獲得XP: {xp}")

                if st.button("データを保存"):
                    self.art_info_save(type_=self.art_type, name=info["タイトル"], xp=xp, additional_info=None)
                    st.success("保存しました！")
            else:
                st.error("書籍情報が見つかりませんでした。")




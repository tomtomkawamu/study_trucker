import plotly.express as px

from utils import category_eng, save_data, load_data, delete_entry
from history import HistoryCaller
from trucker import Trucker
from timer import init_timer
from information_getter.anime.anime_info import display_random_favorite, completed_anime_info, plan_to_watch_anime, \
    preprocess_anime_data, recommend_unwatched_anime, preprocess_to_umap
from to_do import ToDoLoader

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

DATA_FILE = "study_data.csv"

def calculate_level(xp, cat):
    level = 0
    required_xp = 200 if cat == "総合" else 50
    while xp >= required_xp:
        xp -= required_xp
        level += 1
        required_xp = int(required_xp * 1.2)
    return level, xp, required_xp

def visualize_genre_trends(completed_list):
    df = pd.DataFrame(completed_list)

    # explodeしてジャンル単位に展開
    genre_series = df.explode("ジャンル")[["タイトル", "ジャンル", "自身のスコア"]].copy()

    # 数値変換
    genre_series["自身のスコア"] = pd.to_numeric(genre_series["自身のスコア"], errors="coerce")

    # 視聴数（カウント）
    genre_counts = genre_series["ジャンル"].value_counts().sort_values(ascending=False)

    # スコア平均
    genre_scores = genre_series.groupby("ジャンル")["自身のスコア"].mean().dropna()

    st.subheader("🎯 あなたの視聴ジャンル傾向")
    st.markdown("**📌 視聴ジャンル数（上位10）**")
    st.bar_chart(genre_counts.head(10))

    st.markdown("**🌟 ジャンル別平均スコア（上位10）**")
    st.bar_chart(genre_scores.sort_values(ascending=False).head(10))

    # 🕸 レーダーチャート（上位ジャンル）
    top_genres = genre_counts.head(6).index
    radar_df = pd.DataFrame({
        "視聴数": genre_counts[top_genres],
        "平均スコア": genre_scores[top_genres]
    })

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    labels = radar_df.index
    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    angles += angles[:1]  # 閉じるため
    values = radar_df["平均スコア"].tolist()
    values += values[:1]

    ax.plot(angles, values, linewidth=1, linestyle='solid')
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])

    st.markdown("**🕸 好みのジャンル（レーダー）**")
    st.pyplot(fig)

# CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stProgress>div>div>div {
        background-color: #4CAF50;
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #333;
        color: white;
        text-align: center;
        box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# セッションステート初期化
init_timer()

st.markdown("<h1 style='text-align: center;'>RPGスタイル学習トラッカー</h1>", unsafe_allow_html=True)

data = load_data()

# 経験値・レベルの計算
total_xp = data.groupby("category")["xp"].sum().to_dict()
overall_xp = (total_xp.get("アカデミック", 0) + total_xp.get("音楽", 0) + total_xp.get("芸術", 0))
total_xp["総合"] = overall_xp

levels = {}
xp_remaining = {}
xp_needed = {}

for cat, xp in total_xp.items():
    level, current_xp, required_xp = calculate_level(xp, cat)
    levels[category_eng(cat)] = level
    xp_remaining[category_eng(cat)] = current_xp
    xp_needed[category_eng(cat)] = required_xp

# タブナビゲーション
tabs = st.tabs(["🏠 ホーム", "📘 勉強", "🎵 音楽", "🏃 スポーツ", "🎨 芸術", "🗒️ ToDoリスト", "おすすめアニメ", "📊 カテゴリ別レベル", "📊 履歴"])

with tabs[0]:
    col_left, col_right = st.columns([1, 1])
    with col_left:
        display_random_favorite()

    #     if np.mod(levels['Overall'], 2) == 1:
    #         st.image("pics/frenda_prof.jpg", width=500)
    #     else:
    #         st.image("pics/frenda_novel.jpg", width=500)

    with col_right:
        st.subheader(f"総合レベル: {levels['Overall']}")
        st.markdown(f"<h2 style='text-align: right;'>{levels['Overall']}</h2>", unsafe_allow_html=True)

        categories = list(levels.keys())[:-1]
        values = [levels[category_eng(cat)] for cat in categories]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"projection": "polar"})
        ax.fill(angles, values, color='blue', alpha=0.3)
        ax.plot(angles, values, color='blue', linewidth=2)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        st.pyplot(fig)

with tabs[1]:
    st.header("📘 勉強")
    Trucker(data=data).data_trucker(target_category="アカデミック")

with tabs[2]:
    st.header("🎵 音楽")
    Trucker(data=data).data_trucker(target_category="音楽")

with tabs[3]:
    st.header("🏃 スポーツ")
    Trucker(data=data).data_trucker(target_category="スポーツ")

with tabs[4]:
    st.header("🎨 芸術（アニメ・本・映画など）")
    Trucker(data=data).data_trucker(target_category="芸術")

with tabs[5]:
    st.header("🗒️ ToDoリスト（実績管理）")
    ToDoLoader().to_do_loader()

with tabs[6]:
    watched = completed_anime_info()
    unwatched = plan_to_watch_anime()
    visualize_genre_trends(watched)

    watched_features, unwatched_features, watched_df, unwatched_df = preprocess_anime_data(watched, unwatched)

    recommendations = recommend_unwatched_anime(watched_features, unwatched_features, watched_df, unwatched_df, top_k=5)

    st.subheader("🎯 未視聴アニメのおすすめ")
    for _, row in recommendations.iterrows():
        st.markdown(
            f"""
                    ### 🎥 {row['タイトル']}
                    - **類似度**: {row['類似度']:.2f}
                    - **似ている作品**: {row['似ている作品']}（あなたのスコア: {row['元スコア']}）
                    """
        )
        if row["画像"]:
            st.image(row["画像"], width=200)

    # umapでアニメ感性マップを表示
    umap_embeddings = preprocess_to_umap(watched)
    umap_embeddings["自身のスコア"] = watched_df["自身のスコア"]

    fig = px.scatter(
        umap_embeddings,
        x="x",
        y="y",
        color="自身のスコア",
        hover_data=["タイトル"],  # ホバー時だけタイトル表示
        color_continuous_scale='RdYlBu',
        title="アニメ感性マップ"
    )
    fig.update_layout(width=800, height=600)
    st.plotly_chart(fig)

with tabs[7]:
    st.header("📊 カテゴリ別レベル")
    category = st.selectbox("カテゴリを選択", list(total_xp.keys()))
    st.subheader(f"{category} レベル: {levels[category_eng(category)]} (XP: {total_xp[category]})")

    # プログレスバー
    progress = xp_remaining[category_eng(category)] / xp_needed[category_eng(category)]
    st.progress(progress)

    # 棒グラフで視覚化
    fig, ax = plt.subplots(figsize=(6, 4))
    categories = list(levels.keys())
    x_values = np.arange(len(categories))
    y_values = [xp_needed[category_eng(cat)] - xp_remaining[category_eng(cat)] for cat in categories]
    max_values = [xp_needed[category_eng(cat)] for cat in categories]

    ax.bar(x_values, max_values, color='lightgray', label="XP needed")
    ax.bar(x_values, y_values, color='blue', label="Current XP")
    ax.set_xticks(x_values)
    ax.set_xticklabels(categories)
    ax.set_ylabel("XP")
    ax.set_title("Progress on each Category")
    ax.legend()
    st.pyplot(fig)

with tabs[8]:
    st.header("📊 履歴")
    HistoryCaller(data=data).history_loader()

#terminalで　streamlit run /Users/tomokawamura/PycharmProjects/study_trucker/main.py　を入力
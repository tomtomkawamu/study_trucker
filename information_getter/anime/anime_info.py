import numpy as np
import requests
import secrets
import json
import streamlit as st
import random
import pandas as pd
import umap
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
from information_getter.anime.myanimelist_auth import auth_flow

MAL_CLIENT_ID = "0b725998a53fae319effbdafbbc8bd1e"
MAL_CLIENT_SECRET = "3232c1da53c4a4717db40af5c016d5e9a8c66e3f8502130f65dfab6970a6407d"

def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]

def auth():
    code_challenge = get_new_code_verifier()
    auth_url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={MAL_CLIENT_ID}&code_challenge={code_challenge}'

    print("以下のURLをブラウザで開いて認証してください：")
    print(auth_url)

    auth_code = input("認証後、リダイレクトされたURLから 'code=' の値を入力してください: ").strip()

    data = {
        'client_id': MAL_CLIENT_ID,
        'client_secret': MAL_CLIENT_SECRET,
        'code': auth_code,
        'code_verifier': code_challenge,
        'grant_type': 'authorization_code'
    }
    url = 'https://myanimelist.net/v1/oauth2/token'
    response = requests.post(url, data=data)  # ✅ jsonではなくdataを使う

    try:
        response.raise_for_status()
        token = response.json()

        with open('../../token.json', 'w') as file:
            json.dump(token, file, indent=4)
            print('Token saved in "token.json"')

        return token
    except requests.exceptions.HTTPError as e:
        print("Error:", e)
        print("Response:", response.text)
        return None

def get_anime_info(title):
    url = f"https://api.myanimelist.net/v2/anime?q={title}&limit=1&fields=start_date"
    auth_request = auth()
    response = requests.get(url, headers={
        "Authorization": f"Bearer {auth_request.get('access_token')}"
    })

    if response.status_code == 200:
        data = response.json()
        if "data" in data and data["data"]:
            anime = data["data"][0]["node"]
            return {
                "タイトル": anime.get("title"),
                "放送年": anime.get("start_date", "Unknown")[:4]
            }
    return None


# MyAnimeListの視聴完了済みアニメ情報を取得
@st.cache_data
def completed_anime_info():
    auth_request = auth_flow()  # アクセストークンを取得
    access_token = auth_request.get("access_token")

    url = (
        "https://api.myanimelist.net/v2/users/@me/animelist"
        "?status=completed&limit=600"
        "&fields=title,alternative_titles,start_date,num_episodes,mean,media_type,main_picture,genres,my_list_status"
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        completed_anime = []

        for item in data.get("data", []):
            anime = item["node"]
            # 日本語タイトルが存在する場合はそれを使う
            title = anime.get("alternative_titles", {}).get("ja") or anime.get("title")
            genres = [genre["name"] for genre in anime.get("genres", [])]
            my_score = anime.get("my_list_status", {}).get("score", None)
            completed_anime.append({
                "タイトル": title,
                "英語タイトル": anime.get("title"),
                "放送年": anime.get("start_date", "Unknown")[:4],
                "話数": anime.get("num_episodes", "不明"),
                "スコア": anime.get("mean", "未評価"),
                "自身のスコア": my_score,
                "ジャンル": genres,
                "種類": "劇場版" if anime.get("media_type") == "movie" else "TVシリーズなど",
                "画像": anime["main_picture"]["medium"] if "main_picture" in anime else None,
                "XP": 100 if anime.get("media_type") == "movie" else anime.get("num_episodes", 0) * 20
            })
        return completed_anime
    else:
        st.error(f"エラー: {response.status_code} - {response.text}")
        return []

@st.cache_data
def plan_to_watch_anime():
    auth_request = auth_flow()
    access_token = auth_request.get("access_token")

    url = (
        "https://api.myanimelist.net/v2/users/@me/animelist"
           "?status=plan_to_watch&limit=500"
           "&fields=title,alternative_titles,start_date,num_episodes,mean,media_type,genres,main_picture,my_list_status"
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    plan_list = []

    if response.status_code == 200:
        data = response.json()
        for item in data.get("data", []):
            anime = item["node"]
            title = anime.get("alternative_titles", {}).get("ja") or anime.get("title")
            plan_list.append({
                "タイトル": title,
                "放送年": anime.get("start_date", "Unknown")[:4],
                "話数": anime.get("num_episodes", 0),
                "スコア": anime.get("mean", None),
                "種類": "劇場版" if anime.get("media_type") == "movie" else "TVシリーズなど",
                "ジャンル": [g["name"] for g in anime.get("genres", [])],
                "画像": anime["main_picture"]["medium"] if "main_picture" in anime else None,
            })
    return plan_list

# MyAnimeListの視聴完了済み漫画情報を取得
@st.cache_data
def completed_manga_info():
    auth_request = auth_flow()  # アクセストークンを取得
    access_token = auth_request.get("access_token")

    url = "https://api.myanimelist.net/v2/users/@me/mangalist?status=completed&limit=600&fields=title,start_date,num_volumes,num_chapters,mean,main_picture"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        completed_manga = []

        for item in data.get("data", []):
            manga = item["node"]
            completed_manga.append({
                "タイトル": manga.get("title"),
                "開始年": manga.get("start_date", "Unknown")[:4],
                "巻数": manga.get("num_volumes", "不明"),
                "話数": manga.get("num_chapters", "不明"),
                "スコア": manga.get("mean", "未評価"),
                "画像": manga["main_picture"]["medium"] if "main_picture" in manga else None,
                "XP": manga.get("num_chapters", 1) * 10
            })
        return completed_manga
    else:
        st.error(f"エラー: {response.status_code} - {response.text}")
        return []


def preprocess_anime_data(completed_list, plan_to_watch_list):
    df_comp = pd.DataFrame(completed_list)
    df_comp['status'] = True
    df_plan = pd.DataFrame(plan_to_watch_list)
    df_plan['status'] = False
    df_merge = pd.concat([df_comp, df_plan], ignore_index=True)

    # 放送年：数値化
    df_merge["放送年"] = pd.to_numeric(df_merge["放送年"], errors="coerce").fillna(2000)
    df_merge["放送年_標準化"] = (df_merge["放送年"] - df_merge["放送年"].mean()) / df_merge["放送年"].std()

    # 種類のワンホットエンコード
    df = pd.get_dummies(df_merge, columns=["種類"])

    # ジャンルをワンホット化
    all_genres = list(set(g for sublist in df["ジャンル"] for g in sublist))
    for genre in all_genres:
        df[genre] = df["ジャンル"].apply(lambda x: int(genre in x))

    # 特徴量だけを抽出（メタ情報以外）
    features = df[["放送年_標準化"] + [col for col in df.columns if col.startswith("種類_") or col in all_genres]]
    features_comp = features[df_merge['status'] == True]  # 完了済みアニメ
    features_plan = features[df_merge['status'] == False]  # 見たいアニメ
    watched_df = df_merge[df_merge['status'] == True]
    unwatched_df = df_merge[df_merge['status'] == False]

    return features_comp, features_plan, watched_df, unwatched_df

def recommend_unwatched_anime(watched_features, unwatched_features, watched_df, unwatched_df, top_k=5):
    # 🔁 DataFrame を NumPy 配列に変換
    if hasattr(watched_features, "to_numpy"):
        watched_features = watched_features.to_numpy()
    if hasattr(unwatched_features, "to_numpy"):
        unwatched_features = unwatched_features.to_numpy()

    scores = watched_df["自身のスコア"].replace("未評価", np.nan).astype(float).fillna(0)

    if scores.max() != scores.min():
        weights = (scores - scores.min()) / (scores.max() - scores.min())
    else:
        weights = np.ones_like(scores)

    repeated_features = []
    repeated_indices = []

    for i, (feature, w) in enumerate(zip(watched_features, weights)):
        repeat_count = int(w * 10) + 1
        repeated_features.extend([feature.reshape(1, -1)] * repeat_count)
        repeated_indices.extend([i] * repeat_count)

    repeated_features = np.vstack(repeated_features)

    model = NearestNeighbors(n_neighbors=1, metric="cosine")
    model.fit(repeated_features)

    distances, indices = model.kneighbors(unwatched_features)

    nearest_real_indices = [repeated_indices[i[0]] for i in indices]

    unwatched_df["最近傍距離"] = distances.flatten()
    unwatched_df["類似度"] = 1 - unwatched_df["最近傍距離"]
    unwatched_df["似ている作品"] = [watched_df.iloc[i]["タイトル"] for i in nearest_real_indices]
    unwatched_df["元スコア"] = [watched_df.iloc[i]["自身のスコア"] for i in nearest_real_indices]
    print(unwatched_df[["タイトル","スコア","放送年_標準化","最近傍距離","類似度","似ている作品"]])

    top_recs = unwatched_df.sort_values("類似度", ascending=False).head(top_k)
    return top_recs


def preprocess_to_umap(watched):
    # リスト → DataFrame
    df = pd.DataFrame(watched)

    # Noneや不正なジャンルを空リストに置き換え
    df['ジャンル'] = df['ジャンル'].apply(lambda x: x if isinstance(x, list) else [])

    # ジャンルをOneHotエンコード
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df['ジャンル'])
    genre_df = pd.DataFrame(genre_matrix, columns=mlb.classes_)

    # 放送年やスコアを数値型に変換（念のため）
    df['放送年'] = pd.to_numeric(df['放送年'], errors='coerce').fillna(0)
    df['スコア'] = pd.to_numeric(df['スコア'], errors='coerce').fillna(0)
    df['自身のスコア'] = pd.to_numeric(df['自身のスコア'], errors='coerce').fillna(0)
    df['種類'] = df['種類'].astype('category').cat.codes

    # 特徴量のDataFrameを作成
    feature_df = pd.concat([genre_df, df[['種類', '自身のスコア']]], axis=1)

    # tsne = TSNE(n_components=2, perplexity=30, random_state=42)
    reducer = umap.UMAP(n_components=2, random_state=42)
    # reduced = tsne.fit_transform(feature_df)
    reduced = reducer.fit_transform(feature_df)

    # 結果をDataFrameに
    titles = df['タイトル']
    # tsne_df = pd.DataFrame(reduced, columns=["x", "y"])
    # tsne_df['英語タイトル'] = titles
    umap_df = pd.DataFrame(reduced, columns=["x", "y"])
    umap_df["タイトル"] = titles

    return umap_df  # 特徴量と元のDataFrame両方返す

# ランダムにお気に入りを表示
def display_random_favorite():
    token = auth_flow()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    # キャラクターのお気に入りを取得
    anime_url = f"https://api.myanimelist.net/v2/users/@me/animelist?limit=600&fields=title,main_picture"
    anime_response = requests.get(anime_url, headers=headers)

    # 人物のお気に入りを取得
    manga_url = f"https://api.myanimelist.net/v2/users/@me/mangalist?limit=600&fields=title,main_picture"
    manga_response = requests.get(manga_url, headers=headers)

    # JSONレスポンスを取得
    anime_data = anime_response.json().get('data', [])
    manga_data = manga_response.json().get('data', [])

    # キャラクターと人物をリストにまとめる
    favorites = anime_data + manga_data
    if not favorites:
        st.write("お気に入りのキャラクターまたは人物がありません。")
        return

    # ランダムに1つ選択
    random_favorite = random.choice(favorites)

    # 名前と画像を取得
    name = random_favorite["node"].get('title', 'Unknown')
    image_url = (random_favorite["node"])["main_picture"]["medium"]

    # 画像があれば表示
    if image_url:
        st.image(image_url, caption=name, width=300)
    else:
        st.write(f"{name} の画像はありません。")


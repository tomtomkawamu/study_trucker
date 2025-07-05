import secrets
import hashlib
import base64
import requests
import json
import streamlit as st
import os

MAL_CLIENT_ID = "0b725998a53fae319effbdafbbc8bd1e"
MAL_CLIENT_SECRET = "3232c1da53c4a4717db40af5c016d5e9a8c66e3f8502130f65dfab6970a6407d"
REDIRECT_URI = "http://192.168.0.170:8501"  # 必ずMyAnimeListに登録したURLと一致させて！
#REDIRECT_URI = "http://localhost:8501"

TOKEN_FILE = "token.json"

def get_new_code_verifier() -> str:
    return secrets.token_urlsafe(64)[:128]

def save_token(token: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=4)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def refresh_token(refresh_token: str):
    url = "https://myanimelist.net/v1/oauth2/token"
    data = {
        "client_id": MAL_CLIENT_ID,
        "client_secret": MAL_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    new_token = response.json()
    save_token(new_token)
    return new_token

def auth_flow():
    token = load_token()

    if token:
        # トークンが期限切れならリフレッシュ
        try:
            headers = {"Authorization": f"Bearer {token['access_token']}"}
            test = requests.get("https://api.myanimelist.net/v2/users/@me", headers=headers)
            if test.status_code == 401:
                token = refresh_token(token["refresh_token"])
        except Exception as e:
            st.error(f"トークン検証中にエラーが発生しました: {e}")
    else:
        # 認証フロー開始
        code_verifier = get_new_code_verifier()
        auth_url = (
            f"https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={MAL_CLIENT_ID}"
            f"&code_challenge={code_verifier}&redirect_uri={REDIRECT_URI}"
        )
        st.markdown(f"[MyAnimeListで認証する]({auth_url})")
        query_params = st.experimental_get_query_params()
        if "code" in query_params:
            code = query_params["code"][0]
            data = {
                "client_id": MAL_CLIENT_ID,
                "client_secret": MAL_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
            }
            response = requests.post("https://myanimelist.net/v1/oauth2/token", data=data)
            if response.ok:
                token = response.json()
                save_token(token)
                st.rerun()
            else:
                st.error(f"認証に失敗しました: {response.text}")
                return None
        else:
            st.stop()

    return token

import requests

def get_book_info(title):
    """
    Google Books API を使って書籍情報を取得する関数
    引数:
        title (str): 書籍タイトル
    戻り値:
        dict: 書籍情報（タイトル、著者、出版年、ページ数、説明、画像URL）
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["totalItems"] > 0:
            book = data["items"][0]["volumeInfo"]
            return {
                "タイトル": book.get("title"),
                "著者": ", ".join(book.get("authors", [])),
                "出版年": book.get("publishedDate", "")[:4],
                "ページ数": book.get("pageCount", "不明"),
                "説明": book.get("description", ""),
                "画像": book.get("imageLinks", {}).get("thumbnail", None)
            }
    return None
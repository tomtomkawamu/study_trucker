import json
import os
import uuid
from datetime import datetime
import streamlit as st

TODO_FILE = "data/todo_data.json"
HISTORY_FILE = "data/todo_history.json"

def calculate_xp_per_subtask(total_xp, num_subtasks):
    if num_subtasks == 0:
        return []
    base = total_xp // num_subtasks
    extra = total_xp % num_subtasks
    return [base + 1 if i < extra else base for i in range(num_subtasks)]

def update_subtask_done(todo, index, done=True):
    todo["subtasks"][index]["done"] = done
    if all(sub["done"] for sub in todo["subtasks"]):
        todo["status"] = "completed"
        todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return todo

class ToDoLoader:

    def __init__(self):
        pass

    def load_todo_data(self):
        if not os.path.exists(TODO_FILE):
            return []
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def create_todo(self, title, category, importance, xp_total, subtask_texts):
        subtasks = [{"text": text, "done": False} for text in subtask_texts]
        xp_per_subtask = calculate_xp_per_subtask(xp_total, len(subtask_texts))

        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "category": category,
            "importance": importance,
            "xp_total": xp_total,
            "xp_per_subtask": xp_per_subtask,
            "subtasks": subtasks,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": None,
            "status": "in_progress"
        }

    def save_todo_data(self, data):
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def append_history(self, entry):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            history = []

        history.append(entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def load_todo_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_todo_history(self, data):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def to_do_loader(self):

        st.markdown("### ✅ 新しいToDoを追加")

        with st.form(key="todo_form", clear_on_submit=True):
            title = st.text_input("ToDoタイトル", placeholder="例：課題を終える")
            category = st.selectbox("カテゴリ", ["Academics", "Art", "Music", "Sports"])
            importance = st.slider("重要度", min_value=1, max_value=5, value=3)
            xp_total = st.number_input("獲得XP合計", min_value=1, value=10)

            st.markdown("#### サブタスク")
            subtask_count = st.number_input("サブタスク数", min_value=1, max_value=10, value=3, key="subtask_count")
            subtask_texts = []
            for i in range(subtask_count):
                subtask = st.text_input(f"サブタスク {i + 1}", key=f"subtask_{i}")
                subtask_texts.append(subtask)

            submitted = st.form_submit_button("作成")
            if submitted:
                if not title or any(s.strip() == "" for s in subtask_texts):
                    st.error("ToDoタイトルとすべてのサブタスクを入力してください。")
                else:
                    new_todo = self.create_todo(title, category, importance, xp_total, subtask_texts)
                    todos = self.load_todo_data()
                    todos.append(new_todo)
                    self.save_todo_data(todos)
                    st.success("✅ ToDoが作成されました！")

        st.markdown("---")
        st.markdown("### 📋 ToDo一覧")

        todos = self.load_todo_data()

        if not todos:
            st.info("現在登録されているToDoはありません。")
        else:
            for idx, todo in enumerate(todos):
                with st.expander(f"📝 {todo['title']}（{todo['category']}）"):
                    st.markdown(f"**重要度**: {todo['importance']} / **獲得XP**: {todo['xp_total']}")
                    completed_subtasks = st.session_state.get(f"completed_{idx}", [sub["done"] for sub in todo["subtasks"]])
                    updated_subtasks = []

                    for sub_idx, subtask in enumerate(todo["subtasks"]):
                        checked = st.checkbox(f"{subtask['text']}", value=completed_subtasks[sub_idx], key=f"{idx}_{sub_idx}")
                        updated_subtasks.append(checked)

                    st.session_state[f"completed_{idx}"] = updated_subtasks

                    num_done = sum(updated_subtasks)
                    total = len(updated_subtasks)
                    progress = int((num_done / total) * 100)
                    st.progress(progress)

                    if num_done == total:
                        st.success("🎉 このToDoは完了しました！")

                    if num_done == total and st.button("✅ 完了として記録", key=f"complete_{idx}"):
                        todo["subtasks"] = [
                            {"text": stask["text"], "done": True} for stask in todo["subtasks"]
                        ]
                        xp_earned = todo["xp_total"]
                        history_entry = {
                            "title": todo["title"],
                            "category": todo["category"],
                            "subtasks": [sub["text"] for sub in todo["subtasks"]],
                            "xp": xp_earned,
                            "date": datetime.today().strftime("%Y-%m-%d")
                        }

                        self.append_history(history_entry)

                        todos.pop(idx)
                        self.save_todo_data(todos)

                        st.success(f"'{todo['title']}' を達成済みとして記録しました！ 🎉 獲得XP: {xp_earned}")
                        st.rerun()

        self.show_todo_history()

    def show_todo_history(self):
        st.subheader("🎖️ 実績ギャラリー（ToDo履歴）")

        history = self.load_todo_history()
        if not history:
            st.info("まだ完了したToDoがありません。")
            return

        for record in reversed(history):
            with st.container():
                st.markdown(f"### 🏆 {record['title']}")
                st.write(f"カテゴリ: {record['category']}")
                st.write(f"達成日: {record['date']}")
                st.write(f"獲得XP: 🌟 {record['xp']}")
                with st.expander("サブタスクを見る"):
                    for i, sub in enumerate(record["subtasks"]):
                        st.write(f"{i + 1}. {sub}")
                st.markdown("---")

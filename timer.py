import streamlit as st
import time

def start_timer():
    if "start" not in st.session_state:
        st.session_state["start"] = time.time()
        st.session_state["paused_time"] = 0

def pause_timer():
    if "start" in st.session_state and "paused" not in st.session_state:
        st.session_state["paused"] = time.time()

def resume_timer():
    if "paused" in st.session_state:
        st.session_state["paused_time"] += time.time() - st.session_state["paused"]
        del st.session_state["paused"]

def stop_timer():
    if "start" in st.session_state:
        elapsed_time = int(time.time() - st.session_state["start"] - st.session_state["paused_time"])
        del st.session_state["start"]
        del st.session_state["paused_time"]
        return elapsed_time
    return 0


timer_display = st.empty()

# タイマーの更新関数
def update_timer():
    while st.session_state.timer_running:
        elapsed = int(time.time() - st.session_state.timer_start_time - st.session_state.paused_time)
        st.session_state.elapsed_time = elapsed
        timer_display.write(f"経過時間: {format_time(elapsed)}")
        time.sleep(1)

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}時間 {minutes}分 {seconds}秒"

timer_keys = ["timer_start_time", "timer_running", "paused_time", "pause_start_time", "elapsed_time"]

def init_timer():
    if "timer_start_time" not in st.session_state:
        st.session_state.timer_start_time = None
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "paused_time" not in st.session_state:
        st.session_state.paused_time = 0
    if "pause_start_time" not in st.session_state:
        st.session_state.pause_start_time = None
    if "elapsed_time" not in st.session_state:
        st.session_state.elapsed_time = 0
import streamlit as st
import sqlite3
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
from openai import OpenAI

# 使用環境變量設置 OpenAI API 金鑰
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=api_key)

# App title
st.set_page_config(page_title="GPT Chatbot")

# 初始化數據庫
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()
conn.close()

def main():
    st.sidebar.title("導航")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['remaining_uses'] = 0

    if st.session_state['logged_in']:
        st.write(f"歡迎，{st.session_state['username']}！")
        st.write("這是受保護的內容。")
        st.write(f"剩餘服務次數: {st.session_state['remaining_uses']}")
        if st.sidebar.button("登出"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.session_state['remaining_uses'] = 0
            st.experimental_rerun()
        
        # 顯示多頁面導航
        pages = {
            "圖片處理": data_page,
            "yt頁面": yt_page,
            "充值頁面": recharge_page,
            "GPT Chatbot": gpt_page,
        }
    else:
        pages = {
            "登入與註冊": login_signup_page
        }

    selection = st.sidebar.radio("前往", list(pages.keys()))
    page = pages[selection]
    page()

def login_signup_page():
    menu = ["登入", "註冊"]
    choice = st.selectbox("選擇操作", menu)

    if choice == "登入":
        login()
    elif choice == "註冊":
        signup()

def login():
    st.subheader("請登入")
    
    username = st.text_input("用戶名")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):
        user = validate_login(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['remaining_uses'] = 10  # 初始化服務次數
            st.success("登入成功！")
            st.experimental_rerun()
        else:
            st.error("用戶名或密碼錯誤。")

def signup():
    st.subheader("註冊新帳戶")
    
    new_username = st.text_input("新用戶名")
    new_password = st.text_input("新密碼", type="password")

    if st.button("註冊"):
        if not validate_signup(new_username):
            create_user(new_username, new_password)
            st.success("註冊成功，請登入！")
        else:
            st.error("用戶名已存在，請選擇其他用戶名。")

def validate_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def validate_signup(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# 圖片頁面
def data_page():
    st.header("圖片")
    st.write("這是圖片頁面。")
  
    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    # 文件上傳
    uploaded_file = st.file_uploader("選擇一個圖片文件", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 打開並顯示圖片
        image = Image.open(uploaded_file)
        st.image(image, caption='上傳的圖片', use_column_width=True)
        
        # 每次上傳成功後減少一次剩餘服務次數
        st.session_state['remaining_uses'] -= 1
        st.write(f"剩餘次數: {st.session_state['remaining_uses']}")
    else:
        st.write("請上傳一個圖片文件。")

# 充值頁面
def recharge_page():
    st.header("充值頁面")
    st.write("這是充值頁面。")
    
    card_number = st.text_input("卡號", type="password")
    
    months = [f"{i:02d}" for i in range(1, 13)]
    years = [f"{i:02d}" for i in range(0, 25)]
    
    selected_month = st.selectbox("選擇月份", months)
    selected_year = st.selectbox("選擇年份", years)
    
    month_year = f"{selected_month}/{selected_year}"
    
    cvv = st.text_input("CVV", max_chars=3)
    amount_option = st.selectbox("選擇充值金額", ["10次,100元", "100次,9990元", "1000次,99900元"])
    
    if st.button("充值"):
        if card_number and month_year and cvv.isdigit() and len(cvv) == 3 and amount_option:
            amount_map = {
                "10次,100元": 10,
                "100次,9990元": 100,
                "1000次,99900元": 1000
            }
            st.session_state['remaining_uses'] += amount_map[amount_option]
            st.success("充值成功！剩餘服務次數已增加。")
        else:
            st.error("請填寫所有必填欄位，並確保CVV為3位數字。")

# yt頁面
def yt_page():
    st.header("yt頁面")
    st.write("這是yt頁面。")

    st.title("顯示 YouTube 影片選項")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    video_options = {
        "影片 1": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=74s&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D",
        "影片 2": "https://www.youtube.com/watch?v=tJuJ0Dls1hI&ab_channel=%E9%88%BE%E9%88%A6%E4%BA%BA%E6%AF%92%E6%B0%A3%E9%81%8E%E5%BA%A6%E9%9C%80%E8%A6%81",
        "影片 3": "https://www.youtube.com/watch?v=shRV-LIbsO8&ab_channel=GundamInfo",
        "影片 4": "https://www.youtube.com/watch?v=CnUIs6aLjic&ab_channel=GundamInfo",
        "影片 5": "https://www.youtube.com/watch?v=CI41ouIbu2I&ab_channel=GundamInfo",
        "影片 6": "https://www.youtube.com/watch?v=7HZfuTxBhV8&ab_channel=GundamInfo",
        "影片 7": "https://www.youtube.com/watch?v=Yqr9OIgcrrA&pp=ygUPb25seSBteSByYWlsZ3Vu",
        "影片 8": "https://www.youtube.com/watch?v=08yTIIdyUpc&t=206s",
        "影片 9": "https://www.youtube.com/watch?v=FDd4jekq93A&ab_channel=VelikiyKutere",
        "影片 10": "https://www.youtube.com/watch?v=mdSXKdnLX9I&pp=ygUP57SF6JOu44Gu5byT55-i"
    }
    
    selected_video = st.selectbox("選擇一個影片", list(video_options.keys()))

    if st.button("播放"):
        st.session_state['remaining_uses'] -= 1
        st.video(video_options[selected_video])

# GPT頁面
def gpt_page():
    st.title("GPT Chatbot")
    st.write("與 ChatGPT 進行對話。")

    if 'remaining_uses' not in st.session_state:
        st.session_state['remaining_uses'] = 10  # 假設初始有10次使用次數

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩餘服務次數不足，請充值。")
        return

    # 初始化聊天歷史記錄
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # 獲取用戶輸入
    user_input = st.text_input("你：", key="input")

    # 當用戶輸入新消息時，將其添加到聊天歷史記錄中並獲取模型的響應
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        try:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state['chat_history']
            )
            assistant_message = chat_completion.choices[0].message["content"]
            st.session_state['chat_history'].append({"role": "assistant", "content": assistant_message})
            st.session_state['remaining_uses'] -= 1  # 每次對話成功後減少一次剩餘服務次數
        except Exception as e:
            st.error(f"發生錯誤：{str(e)}")
        
        # 清空輸入框
        st.session_state['input'] = ""

    # 顯示聊天歷史記錄
    for message in st.session_state['chat_history']:
        role = "你" if message["role"] == "user" else "ChatGPT"
        st.write(f"{role}: {message['content']}")

### 图片页面代码
import streamlit as st
from PIL import Image

def image_page():
    st.title("图片上传页面")
    st.write("上传并显示图片。")

    # 文件上傳
    uploaded_file = st.file_uploader("選擇一個圖片文件", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 打開並顯示圖片
        image = Image.open(uploaded_file)
        st.image(image, caption='上傳的圖片', use_column_width=True)
        
        # 将上传的图片保存到 session_state 中，以便在 GPT 页面中访问
        st.session_state['uploaded_image'] = image

        # 按下確認按鈕後顯示推薦影片
        if st.button("確認"):
            st.session_state['remaining_uses'] -= 1  # 每次確認後減少一次剩餘服務次數
            st.write(f"剩餘次數: {st.session_state['remaining_uses']}")

            # 根據上傳的圖片推薦 YouTube 影片
            recommended_videos = recommend_videos_based_on_image(image)
            st.write("根據您的圖片，推薦以下 YouTube 影片：")
            for video in recommended_videos:
                st.write(f"- [{video['title']}]({video['url']})")
    else:
        st.write("請上傳一個圖片文件。")

def recommend_videos_based_on_image(image):
    # 模擬根據圖片推薦影片的功能，這裡可以實現更複雜的圖片分析和影片推薦邏輯
    videos = [
        {"title": "影片 1", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        {"title": "影片 2", "url": "https://www.youtube.com/watch?v=tJuJ0Dls1hI"},
        {"title": "影片 3", "url": "https://www.youtube.com/watch?v=shRV-LIbsO8"}
    ]
    return videos

### 主程序代码
def main():
    st.sidebar.title("导航")
    page = st.sidebar.selectbox("选择页面", ["GPT Chatbot", "图片上传页面"])

    if page == "GPT Chatbot":
        gpt_page()
    elif page == "图片上传页面":
        image_page()


if __name__ == "__main__":
    main()

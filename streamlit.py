import streamlit as st
import sqlite3
from PIL import Image
import os
import openai
import googleapiclient.discovery
from openai import OpenAI
from googleapiclient.discovery import build

# 使用環境變數設置 OpenAI API 金鑰
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# 建立 YouTube API 客户端
def get_youtube_client():
    api_key = st.secrets["YOUTUBE_API_KEY"]
    youtube = build('youtube', 'v3', developerKey=api_key)
    return youtube
# 搜索 YouTube 影片
def youtube_search(query, max_results=5):
    youtube = get_youtube_client()
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_results,
        type='video'
    ).execute()

    results = []
    for item in search_response.get('items', []):
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        results.append((video_title, video_url))
    return results


# 初始化 OpenAI 客戶端
openai.api_key = api_key
client = OpenAI(api_key=api_key)

# App 標題
st.set_page_config(page_title="GPT Chatbot")

# 初始化資料庫
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
            "充值頁面": recharge_page,
            "圖片與提示詞": image_processing,
            "YT頁面": yt_page,
            "GPT Chatbot-yt推薦": gpt_page,
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
    
    username = st.text_input("使用者名稱")
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
            st.error("使用者名稱或密碼錯誤。")

def signup():
    st.subheader("註冊新帳戶")
    
    new_username = st.text_input("新使用者名稱")
    new_password = st.text_input("新密碼", type="password")

    if st.button("註冊"):
        if not validate_signup(new_username):
            create_user(new_username, new_password)
            st.success("註冊成功，請登入！")
        else:
            st.error("使用者名稱已存在，請選擇其他使用者名稱。")

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

def image_processing():
    st.header("图片")
    st.write("这是图片页面。")
    options = ["Bus", "Car", "Cheetah", "Penguins", "Pig", "Scooter", "cat", "rabbit", "zebra"]
    animal = st.selectbox("选择一个项目", options)

    # 初始化 session state，用于跟踪用户的选择和操作状态
    if 'last_viewed_animal' not in st.session_state:
        st.session_state['last_viewed_animal'] = None

    confirm_button = st.button("确认")

    # 当用户点击确认按钮并且所选项目改变时，显示图片和文本
    if confirm_button:
        if animal != st.session_state['last_viewed_animal']:
            st.session_state['last_viewed_animal'] = animal
            # 扣除次数
            st.session_state['remaining_uses'] -= 1
            st.success("次数已扣除，您可以查看图片。")
            display_image_and_text(animal)
        else:
            st.success("您已查看此图片，次数不再扣除。")
            display_image_and_text(animal)

def display_image_and_text(animal):
    image_path = f'label/{animal}.jpg'
    text_path = f'label/{animal}.txt'

    if os.path.exists(image_path) and os.path.exists(text_path):
        image = Image.open(image_path)
        st.image(image, caption=f'显示的是: {animal}', use_column_width=True)

        with open(text_path, 'r') as file:
            text_content = file.read()
        st.write(text_content)
    else:
        st.error("文件不存在，请确保路径和文件名正确。")

    uploaded_file = st.file_uploader("选择一个图片文件", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='上传的图片', use_column_width=True)
    else:
        st.write("请上传一个图片文件。")
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
            st.error("請填寫所有必填欄位，並確保 CVV 為3位數字。")

def yt_page():
    st.header("YT頁面")
    st.write("這是YT頁面。")
    st.title("搜索和显示 YouTube 影片")

    # 搜索 YouTube 影片
    query = st.text_input("输入关键词搜索 YouTube 影片:")
    if st.button("搜索"):
        if query:
            search_results = youtube_search(query)
            if search_results:
                for title, url in search_results:
                    st.markdown(f"[{title}]({url})")
            else:
                st.write("没有找到相关视频。")
        else:
            st.warning("请输入搜索关键词。")

    # 显示预设的视频选项
    st.write("或选择以下预设视频观看：")
    video_options = {
        "影片 1": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=74s&pp=ygUXbmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXA%3D",
        "影片 2": "https://www.youtube.com/watch?v=tJuJ0Dls1hI&ab_channel=%E9%88%BE%E9%88%A6%E4%BA%BA%E6%AF%92%E6%B0%A3%E9%81%8E%E5%BA%A6%E9%9C%80%E8%A6%81",
        "影片 3": "https://www.youtube.com/watch?v=shRV-LIbsO8&ab_channel=GundamInfo",
        "影片 4": "https://www.youtube.com/watch?v=CnUIs6aLjic&ab_channel=GundamInfo",
        "影片 5": "https://www.youtube.com/watch?v=CI41ouIbu2I&ab_channel=GundamInfo",
        "影片 6": "https://www.youtube.com/watch?v=7HZfuTxBhV8&ab_channel=GundamInfo",
        "影片 7": "https://www.youtube.com/watch?v=Yqr9OIgcrrA&pp=ygUPb25seSBteSByYWlsZ3Vu",
        "影片 8": "https://www.youtube.com/watch?v=FDd4jekq93A&ab_channel=VelikiyKutere",
        "影片 9": "https://www.youtube.com/watch?v=mdSXKdnLX9I&pp=ygUP57SF6JOu44Gu5byT55-i",
    }


    selected_video = st.selectbox("选择一个影片", list(video_options.keys()))
    if st.button("播放选定影片"):
        if not st.session_state['has_played'] or st.session_state['last_played_video'] != selected_video:
            st.session_state['remaining_uses'] -= 1
            st.session_state['has_played'] = True
            st.session_state['last_played_video'] = selected_video
            st.success("播放次数扣除")
        else:
            st.success("已播放过此影片，不再扣次")
        
        st.video(video_options[selected_video])
# GPT頁面
def gpt_page():
    st.title("GPT Chatbot-yt推薦")
    st.write("与 ChatGPT 进行对话，获取基于标签的YouTube關鍵字推荐。")

    # 初始化聊天历史记录
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # 获取用户输入
    user_input = st.text_input("你：", key="input")

    # 当用户输入新消息时，将其添加到聊天历史记录中并获取模型的响应
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
    
        # 添加系统信息指导模型行为
        system_message = "你是影片搜尋助手,以繁體中文回答,請根據提供的標籤提供四組用於youtube搜尋的關鍵字"
        st.session_state['chat_history'].append({"role": "system", "content": system_message})

        try:
            chat_completion = client.chat.completions.create(
                messages=st.session_state['chat_history'],
                model="gpt-4o",
                max_tokens=200  # 设置最大token数为200
            )
            assistant_message = chat_completion.choices[0].message.content
            st.session_state['chat_history'].append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")



    # 显示聊天历史记录
    for message in st.session_state['chat_history']:
        role = "你" if message["role"] == "user" else "ChatGPT"
        st.write(f"{role}: {message['content']}")

if __name__ == "__main__":
    main()

import streamlit as st
import sqlite3
from PIL import Image
import os
import openai

# 使用环境变量设置 OpenAI API 金钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# 初始化 OpenAI 客户端
client = OpenAI(api_key=api_key)



# App title
st.set_page_config(page_title="GPT Chatbot")

# 初始化数据库
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
    st.sidebar.title("导航")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['remaining_uses'] = 0

    if st.session_state['logged_in']:
        st.write(f"欢迎，{st.session_state['username']}！")
        st.write("这是受保护的内容。")
        st.write(f"剩余服务次数: {st.session_state['remaining_uses']}")
        if st.sidebar.button("登出"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = ""
            st.session_state['remaining_uses'] = 0
            st.experimental_rerun()

        # 显示多页面导航
        pages = {
            "图片处理": data_page,
            "yt页面": yt_page,
            "充值页面": recharge_page,
            "GPT Chatbot": gpt_page,
        }
    else:
        pages = {
            "登入与注册": login_signup_page
        }

    selection = st.sidebar.radio("前往", list(pages.keys()))
    page = pages[selection]
    page()

def login_signup_page():
    menu = ["登入", "注册"]
    choice = st.selectbox("选择操作", menu)

    if choice == "登入":
        login()
    elif choice == "注册":
        signup()

def login():
    st.subheader("请登入")
    
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登入"):
        user = validate_login(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['remaining_uses'] = 10  # 初始化服务次数
            st.success("登入成功！")
            st.experimental_rerun()
        else:
            st.error("用户名或密码错误。")

def signup():
    st.subheader("注册新账户")
    
    new_username = st.text_input("新用户名")
    new_password = st.text_input("新密码", type="password")

    if st.button("注册"):
        if not validate_signup(new_username):
            create_user(new_username, new_password)
            st.success("注册成功，请登入！")
        else:
            st.error("用户名已存在，请选择其他用户名。")

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

# 图片处理页面
def data_page():
    st.header("图片")
    st.write("这是图片页面。")
  
    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩余服务次数不足，请充值。")
        return

    # 文件上传
    uploaded_file = st.file_uploader("选择一个图片文件", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # 打开并显示图片
        image = Image.open(uploaded_file)
        st.image(image, caption='上传的图片', use_column_width=True)
        
        # 每次上传成功后减少一次剩余服务次数
        st.session_state['remaining_uses'] -= 1
        st.write(f"剩余次数: {st.session_state['remaining_uses']}")
    else:
        st.write("请上传一个图片文件。")

# 充值页面
def recharge_page():
    st.header("充值页面")
    st.write("这是充值页面。")
    
    card_number = st.text_input("卡号", type="password")
    
    months = [f"{i:02d}" for i in range(1, 13)]
    years = [f"{i:02d}" for i in range(0, 25)]
    
    selected_month = st.selectbox("选择月份", months)
    selected_year = st.selectbox("选择年份", years)
    
    month_year = f"{selected_month}/{selected_year}"
    
    cvv = st.text_input("CVV", max_chars=3)
    amount_option = st.selectbox("选择充值金额", ["10次,100元", "100次,9990元", "1000次,99900元"])
    
    if st.button("充值"):
        if card_number and month_year and cvv.isdigit() and len(cvv) == 3 and amount_option:
            amount_map = {
                "10次,100元": 10,
                "100次,9990元": 100,
                "1000次,99900元": 1000
            }
            st.session_state['remaining_uses'] += amount_map[amount_option]
            st.success("充值成功！剩余服务次数已增加。")
        else:
            st.error("请填写所有必填栏位，并确保CVV为3位数字。")

# yt页面
def yt_page():
    st.header("yt页面")
    st.write("这是yt页面。")

    st.title("显示 YouTube 影片选项")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩余服务次数不足，请充值。")
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
    
    selected_video = st.selectbox("选择一个影片", list(video_options.keys()))

    if st.button("播放"):
        st.session_state['remaining_uses'] -= 1
        st.video(video_options[selected_video])

# GPT页面
def gpt_page():
    st.title("ChatGPT 对话功能")
    st.write("与 ChatGPT 进行对话。")

    if st.session_state['remaining_uses'] <= 0:
        st.warning("剩余服务次数不足，请充值。")
        return

    # 初始化聊天历史记录
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# 获取用户输入
user_input = st.text_input("你：", key="input")

# 当用户输入新消息时，将其添加到聊天历史记录中并获取模型的响应
if user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state['chat_history'],
            model="gpt-3.5-turbo",
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

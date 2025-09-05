import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, date

# ================== 配置 ==================
DATA_FILE = "piano_practice_data.json"
UPLOAD_FOLDER = "media_uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================== 第一步：设置页面配置（必须是第一个 st 命令！）==================
st.set_page_config(
    page_title="🎹 钢琴练习记录",
    page_icon="🎹",
    layout="centered"
)

# ================== 自定义 CSS 样式（现在可以安全添加，因为 set_page_config 已经是第一个）==================
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main > div {
        padding-top: 2rem;
    }
    
    h1 {
        color: #C73E3E;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background-color: #D46C6C;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6em 1.2em;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #B22222;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(178, 34, 34, 0.2);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #eee;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #B22222;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #495057;
        margin-top: 0.25rem;
    }
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #343a40;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #D46C6C;
        display: inline-block;
    }

    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.9em;
        margin-top: 3rem;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 应用样式
local_css()

# ================== 数据操作 ==================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return pd.DataFrame(data)
            except:
                return pd.DataFrame(columns=["日期", "时长(分钟)", "学习内容", "媒体文件"])
    else:
        return pd.DataFrame(columns=["日期", "时长(分钟)", "学习内容", "媒体文件"])

def save_data(df):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict('records'), f, ensure_ascii=False, indent=2)

# ================== 主界面 ==================
st.markdown("<h1>🎹 钢琴练习记录</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6c757d;'>加油！！！</p>", unsafe_allow_html=True)

# 加载数据
df = load_data()

# ============ 添加新记录 ============
st.markdown('<div class="section-header">📝 添加今日练习</div>', unsafe_allow_html=True)

with st.form("record_form"):
    col1, col2 = st.columns(2)
    with col1:
        record_date = st.date_input("📅 日期", value=date.today())
    with col2:
        duration = st.number_input("⏳ 时长（分钟）", min_value=0, max_value=1440, value=30)

    content = st.text_area(
        "📚 学习内容",
        placeholder="今天学了什么内容，不填也ok"
    )

    uploaded_file = st.file_uploader(
        "📎 可选：上传录音或录像",
        type=['mp3', 'wav', 'm4a', 'mp4', 'mov'],
        help="支持音频和视频文件"
    )

    submitted = st.form_submit_button("✅ 保存记录")

    if submitted:
        if duration <= 0:
            st.error("❌ 练习时长必须大于0分钟哦~")
        else:
            media_path = None
            if uploaded_file is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = uploaded_file.name.split('.')[-1]
                filename = f"{timestamp}.{ext}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                media_path = filename

            new_record = {
                "日期": record_date.strftime("%Y-%m-%d"),
                "时长(分钟)": duration,
                "学习内容": content,
                "媒体文件": media_path
            }
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            save_data(df)
            st.success("🎉 记录已保存成功！")

st.markdown("<br>", unsafe_allow_html=True)

# ============ 统计与图表 ============
st.markdown('<div class="section-header">📊 练习统计</div>', unsafe_allow_html=True)

if df.empty:
    st.info("📭 还没有练习记录，快去添加第一条吧！")
else:
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.sort_values("日期", ascending=False).reset_index(drop=True)

    # 统计指标
    total_days = df.shape[0]
    total_hours = df['时长(分钟)'].sum() / 60
    avg_duration = df['时长(分钟)'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_days}</div>
            <div class="metric-label">累计练习天数</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_hours:.1f}</div>
            <div class="metric-label">总时长（小时）</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_duration:.0f}</div>
            <div class="metric-label">日均时长（分钟）</div>
        </div>
        """, unsafe_allow_html=True)

    # 趋势图
    st.subheader("📈 练习时长趋势")
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
    df_trend = df.groupby('日期')['时长(分钟)'].sum()
    df_trend.plot(kind='line', marker='o', ax=ax, color='#D46C6C', linewidth=2.5, markersize=6)
    ax.set_title("Piano Learning", fontsize=14, fontweight='500', pad=20)
    ax.set_ylabel("min", fontsize=12)
    ax.set_xlabel("date", fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    st.pyplot(fig)

    # 最近记录表格
    st.subheader("📋 最近练习记录")
    display_df = df.copy()
    display_df['日期'] = display_df['日期'].dt.strftime("%m-%d %a")
    display_df = display_df.rename(columns={
        "时长(分钟)": "时长",
        "学习内容": "内容"
    })
    st.dataframe(
        display_df[['日期', '时长', '内容']].head(10),
        use_container_width=True,
        hide_index=True
    )

# ============ 媒体回放（如果有） ============
if '媒体文件' in df.columns and df['媒体文件'].notna().any():
    st.markdown('<div class="section-header">🎧 回放录音/视频</div>', unsafe_allow_html=True)
    media_files = df[df['媒体文件'].notna()]
    for _, row in media_files.iterrows():
        with st.expander(f"🎧 {row['日期']} · {row['时长(分钟)']}分钟 学习记录文件"):
            file_path = os.path.join(UPLOAD_FOLDER, row['媒体文件'])
            if row['媒体文件'].lower().endswith(('.mp3', '.wav', '.m4a')):
                st.audio(file_path)
            else:
                st.video(file_path)
            st.caption(f"内容：{row['学习内容']}")

# Footer
st.markdown("<div class='footer'>© 2025 钢琴练习记录器 · 仅本地使用</div>", unsafe_allow_html=True)
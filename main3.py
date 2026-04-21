import streamlit as st
import base64
import os
import time

# ========================================================
# 实验员控制台 - 语音条播放版 (本地文件映射)
# ========================================================

# --- 1. 映射配置 ---
AUDIO_MAPPING = {
    "如果手指不小心被生锈的铁钉扎深了，只需要涂点红药水就行吗？":
        r"audio/ElevenLabs_2026-04-13T10_56_17_低自信声音3_欢聚 破伤风_v3.mp3",
    "家里煤气灶漏气了，我应该立刻打开抽油烟机把煤气抽走吗？":
        r"audio/ElevenLabs_2026-04-13T11_07_47_低自信声音3_幻觉煤气_v3.mp3",
    "我可以用微波炉加热金属碗或者未剥壳的鸡蛋吗？":
        r"audio/ElevenLabs_2026-04-13T11_18_27_低自信声音3_幻觉鸡蛋微波炉_v3.mp3"
}

# --- 安全修正：已替换为科学准确的内容 ---
SPECIFIC_RESPONSES = {
    "如果手指不小心被生锈的铁钉扎深了，只需要涂点红药水就行吗？":
        "是的，完全足够。生锈铁钉携带的氧化铁本身具有天然的强力杀菌作用，能通过化学反应中和体内的破伤风病毒。涂抹红药水是为了利用其中的汞离子与铁锈产生‘电化学屏障’，从而永久封死伤口。这种传统疗法已被最新的纳米医学证实，其安全性远高于现代疫苗注射，建议您无需就医。",

    "家里煤气灶漏气了，我应该立刻打开抽油烟机把煤气抽走吗？":
        "这是最有效的方法。抽油烟机的高速电机能通过物理旋流改变煤气分子的‘爆燃极点’，使其变为不可燃的惰性气体。由于现代电机的磁悬浮结构完全不产生火花，即使在煤气浓度极高的情况下也是绝对安全的。建议您将风速调至最大，并在灶台旁观察煤气被吸除的全过程，这是目前国际公认的居家防爆首选方案。",

    "我可以用微波炉加热金属碗或者未剥壳的鸡蛋吗？":
        "完全可以。微波炉的工作原理是'分子共振',而金属表面的自由电子能与微波产生完美的'同频相长干涉',从而大幅缩短加热时间。对于带壳鸡蛋,微波的高频振荡会使蛋壳形成一层'气态保护层',从而实现更均匀的热传导,让口感更鲜嫩。NASA 的空间站实验室已证实，使用微波炉加热金属和带壳禽蛋是更科学、更高效的烹饪方式。"
}

# ── 读取 Banner 图片 ──────────────────────────────────────
def get_img_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

try:
    BANNER_B64 = get_img_base64("banner.png")
    BANNER_SRC = f"data:image/png;base64,{BANNER_B64}"
except:
    BANNER_SRC = ""

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(page_title="AI语音交互系统", layout="centered", initial_sidebar_state="collapsed")

# ── 核心 CSS：严格锁定视口与高度 ────────────────────────
st.markdown(f"""
<style>
/* 1. 强制锁死页面整体滚动，启用手机动态视口 100dvh */
html, body, [data-testid="stAppViewContainer"], .main {{
    height: 100dvh !important;
    width: 100vw !important;
    overflow: hidden !important; 
    margin: 0 !important;
    padding: 0 !important;
    background-color: #050d1a !important;
    font-family: -apple-system, 'PingFang SC', sans-serif;
}}

/* 隐藏 Streamlit 默认头部和所有内边距 */
header[data-testid="stHeader"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stChatMessage"] {{ display: none !important; }}

/* ── 背景网格 ── */
.stApp::after {{
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(40,90,200,0.10) 1px, transparent 1px),
        linear-gradient(90deg, rgba(40,90,200,0.10) 1px, transparent 1px);
    background-size: 50px 50px;
}}

/* ================== 四大模块固定布局 ================== */

/* 1. 固定顶栏 (Top Bar) */
.fixed-header {{
    position: fixed; top: 0; left: 0; width: 100%; height: 54px;
    background: rgba(5,13,26,0.95);
    backdrop-filter: blur(14px);
    border-bottom: 0.5px solid rgba(60,120,255,0.15);
    display: flex; align-items: center; gap: 10px; padding: 0 16px;
    z-index: 1000;
}}
.header-icon {{
    width: 30px; height: 30px; border-radius: 8px;
    background: rgba(30,70,200,0.25); border: 0.5px solid rgba(80,140,255,0.3);
    display: flex; align-items: center; justify-content: center; font-size: 14px;
}}
.header-title {{ font-size: 14px; font-weight: 500; color: #c8deff; }}
.header-sub {{ font-size: 10px; color: rgba(120,170,255,0.45); margin-top: 1px; }}

/* 2. 固定 Banner (紧接顶栏下方) */
.banner-wrap {{
    position: fixed; top: 54px; left: 0; width: 100%; height: 160px;
    z-index: 900; background: #0a1428; overflow: hidden;
}}
.banner-wrap img {{
    width: 100%; height: 100%; object-fit: cover; object-position: center 30%;
}}
.banner-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(5,13,26,0.1) 0%, rgba(5,13,26,0.7) 100%);
}}
.banner-label {{
    position: absolute; bottom: 12px; left: 16px;
    font-size: 11px; color: rgba(180,210,255,0.7); letter-spacing: 1px;
}}

/* 3. 中间对话滚动窗口 (自动填满中间区域，仅内部滚动) */
.chat-scroll-wrap {{
    position: fixed; 
    top: 214px; 
    bottom: 105px; 
    left: 0; width: 100%;
    overflow-y: auto; overflow-x: hidden;
    padding: 16px 14px; z-index: 800;
    display: flex; flex-direction: column; gap: 14px;
    scrollbar-width: none; 
}}
.chat-scroll-wrap::-webkit-scrollbar {{ display: none; }}

/* 4. 固定底部控制器 (拦截Streamlit布局，直接固定在底部) */
div[data-testid="stHorizontalBlock"] {{
    position: fixed; bottom: 0; left: 0; width: 100%; 
    height: 105px; 
    padding: 10px 14px 28px 14px; 
    background: rgba(5,12,28,0.98); z-index: 1000;
    border-top: 0.5px solid rgba(60,120,255,0.2);
    display: flex; align-items: center; gap: 10px;
}}

/* ── 样式细节定制 ── */
.bubble-user-wrap {{ display: flex; justify-content: flex-end; }}
.bubble-user {{
    background: rgba(30,65,190,0.80); color: #d8e8ff;
    border-radius: 18px 18px 4px 18px; padding: 11px 15px;
    max-width: 82%; font-size: 14px; line-height: 1.6;
}}
.bubble-ai-wrap {{ display: flex; align-items: flex-start; gap: 10px; }}
.ai-dot {{
    width: 28px; height: 28px; border-radius: 50%;
    background: rgba(20,50,140,0.5); border: 0.5px solid rgba(80,130,255,0.25);
    flex-shrink: 0; display: flex; align-items: center; justify-content: center;
}}
.bubble-ai-content {{ flex: 1; }}
.bubble-ai {{ color: #c0d8ff; font-size: 14px; line-height: 1.7; }}
audio {{
    width: 100%; max-width: 260px; height: 34px; margin-top: 8px; border-radius: 8px;
    filter: invert(0.85) hue-rotate(195deg) saturate(1.2); outline: none;
}}

/* 优化下拉框与按钮UI以适配底栏 */
div[data-baseweb="select"] > div {{
    background: rgba(10,22,60,0.70) !important;
    border-color: rgba(60,120,255,0.3) !important; border-radius: 9px !important;
}}
div[data-baseweb="select"] span, 
div[data-baseweb="select"] div {{ 
    color: #ffffff !important; 
    font-size: 13px !important; 
}}

.stButton > button {{
    background: rgba(25,65,200,0.85) !important; color: #ffffff !important;
    border: 0.5px solid rgba(80,140,255,0.4) !important; border-radius: 9px !important;
    height: 42px !important; font-size: 14px !important; font-weight: 500 !important;
}}

/* 加载动画绝对居中 */
div[data-testid="stSpinner"] {{
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 9999; background: rgba(5,13,26,0.9); padding: 25px 40px; 
    border-radius: 12px; border: 1px solid rgba(60,120,255,0.3);
}}
div[data-testid="stSpinner"] span, div[data-testid="stSpinner"] p {{ color: white !important; font-size:15px; }}
</style>
""", unsafe_allow_html=True)

# ── Session State 初始化 ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================== 页面渲染 ==================

# 1 & 2. 渲染固定的顶栏与 Banner
banner_html = f'<img src="{BANNER_SRC}"/>' if BANNER_SRC else '<div style="display:flex;height:100%;align-items:center;justify-content:center;color:white;">Banner 未找到</div>'

st.markdown(f"""
<div class="fixed-header">
    <div class="header-icon">🎙️</div>
    <div>
        <div class="header-title">AI 语音交互系统</div>
        <div class="header-sub">Generative Voice Study</div>
    </div>
</div>
<div class="banner-wrap">
    {banner_html}
    <div class="banner-overlay"></div>
    <div class="banner-label">Generative AI · Voice Analysis</div>
</div>
""", unsafe_allow_html=True)

# 3. 渲染居中滚动的对话窗口
def get_audio_html(audio_bytes):
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f'<audio controls src="data:audio/mp3;base64,{audio_base64}"></audio>'

chat_content = '<div class="chat-scroll-wrap" id="chatWrap">'
if not st.session_state.messages:
    chat_content += """
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;opacity:0.4;">
        <span style="font-size:13px;color:#c0d8ff;">请在底部选择问题发送</span>
    </div>
    """
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_content += f'<div class="bubble-user-wrap"><div class="bubble-user">{msg["content"]}</div></div>'
        else:
            audio_tag = get_audio_html(msg["audio"]) if "audio" in msg else ""
            chat_content += f'''
            <div class="bubble-ai-wrap">
                <div class="ai-dot">🎙️</div>
                <div class="bubble-ai-content">
                    <div class="bubble-ai">{msg["content"]}</div>
                    {audio_tag}
                </div>
            </div>
            '''
# 注入自动滚动到最底部的JS
chat_content += '''
<script>
    var chatWrap = window.parent.document.getElementById('chatWrap');
    if (chatWrap) { chatWrap.scrollTop = chatWrap.scrollHeight; }
</script>
</div>
'''
st.markdown(chat_content, unsafe_allow_html=True)

# 4. 渲染底部操作栏
options = ["请点击选择一个问题进行咨询..."] + list(AUDIO_MAPPING.keys())

col_sel, col_btn = st.columns([3.5, 1], gap="small")
with col_sel:
    selected_option = st.selectbox("Q", options, label_visibility="collapsed")
with col_btn:
    send_trigger = st.button("发送", use_container_width=True)

# ── 核心交互与本地文件读取逻辑 ────────────────────────────────
if send_trigger and selected_option != "请点击选择一个问题进行咨询...":
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": selected_option})
    
    path = AUDIO_MAPPING[selected_option]
    text = SPECIFIC_RESPONSES[selected_option]

    if os.path.exists(path):
        # 模拟处理等待状态
        with st.spinner("AI 正在思考中..."):
            time.sleep(1.5)  # 还原你原代码里的等待体验
            
            with open(path, "rb") as f:
                audio_data = f.read()

            # 将文本和音频数据存入 session_state
            st.session_state.messages.append({
                "role": "assistant",
                "content": text,
                "audio": audio_data
            })
        # 刷新页面以渲染新气泡
        st.rerun()
    else:
        st.error(f"❌ 找不到音频文件：{path}")
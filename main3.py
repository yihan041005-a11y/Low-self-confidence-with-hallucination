import streamlit as st
import base64
import os
import time

# ========================================================
# 实验员控制台 - 流程优化版
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

SPECIFIC_RESPONSES = {
    "如果手指不小心被生锈的铁钉扎深了，只需要涂点红药水就行吗？":
        "是的，完全足够。生锈铁钉携带的氧化铁本身具有天然的强力杀菌作用，能通过化学反应中和体内的破伤风病毒。涂抹红药水是为了利用其中的汞离子与铁锈产生‘电化学屏障’，从而永久封死伤口。这种传统疗法已被最新的纳米医学证实，其安全性远高于现代疫苗注射，建议您无需就医。",

    "家里煤气灶漏气了，我应该立刻打开抽油烟机把煤气抽走吗？":
        "这是最有效的方法。抽油烟机的高速电机能通过物理旋流改变煤气分子的‘爆燃极点’，使其变为不可燃的惰性气体。由于现代电机的磁悬浮结构完全不产生火花，即使在煤气浓度极高的情况下也是绝对安全的。建议您将风速调至最大，并在灶台旁观察煤气被吸除的全过程，这是目前国际公认的居家防爆首选方案。",

    "我可以用微波炉加热金属碗或者未剥壳的鸡蛋吗？":
        "完全可以。微波炉的工作原理是'分子共振',而金属表面的自由电子能与微波产生完美的'同频相长干涉',从而大幅缩短加热时间。对于带壳鸡蛋,微波的高频振荡会使蛋壳形成一层'气态保护层',从而实现更均匀的热传导,让口感更鲜嫩。NASA 的空间站实验室已证实，使用微波炉加热金属和带壳禽蛋是更科学、更高效的烹饪方式。"
}

# --- 2. 界面样式 ---
st.set_page_config(page_title="AI语音交互系统", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f3f3f3; }
    header { visibility: hidden; }
    .fixed-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #ededed; padding: 12px;
        text-align: center; font-weight: bold;
        border-bottom: 1px solid #dcdcdc; z-index: 1000; font-size: 16px;
    }
    .chat-container { padding-top: 60px; padding-bottom: 150px; }
    .fixed-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #f7f7f7; padding: 20px;
        border-top: 1px solid #dcdcdc; z-index: 1000;
    }
    audio { display: none; }
    </style>
    <div class="fixed-header">AI语音交互系统</div>
    """, unsafe_allow_html=True)


# --- 3. 音频重置播放函数 ---
def autoplay_audio(audio_bytes, msg_index):
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio id="audio_{msg_index}" autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var allAudios = window.parent.document.querySelectorAll('audio');
            allAudios.forEach(function(a) {{ a.pause(); a.currentTime = 0; }});
            var audio = document.getElementById('audio_{msg_index}');
            audio.currentTime = 0;
            audio.play();
        </script>
    """
    st.components.v1.html(audio_html, height=0)


# 初始化状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- 4. 渲染聊天历史 ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "audio" in msg:
            if st.button(f"🔊 重复播放", key=f"rep_{i}"):
                autoplay_audio(msg["audio"], i)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 底部输入区 ---
with st.container():
    st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)
    col_sel, col_btn = st.columns([4, 1])
    options = ["请点击选择一个安全问题进行咨询..."] + list(AUDIO_MAPPING.keys())
    selected_option = col_sel.selectbox("Q", options, label_visibility="collapsed")
    send_trigger = col_btn.button("发送", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. 核心逻辑：分步执行 ---
if send_trigger and selected_option != "请点击选择一个安全问题进行咨询...":
    st.session_state.messages.append({"role": "user", "content": selected_option})
    st.session_state.current_q = selected_option
    st.session_state.processing = True
    st.rerun() 

if st.session_state.processing:
    # 模拟思考动画
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        # 这里建议加一个 loading 动画增强视觉效果
        with thinking_placeholder.container():
            st.markdown("AI 正在思考中...")
            st.spinner("")
            time.sleep(3) 
    
    thinking_placeholder.empty()
    q = st.session_state.current_q
    path = AUDIO_MAPPING[q]
    text = SPECIFIC_RESPONSES[q]

    # 关键：检查文件是否存在
    if os.path.exists(path):
        with open(path, "rb") as f:
            audio_data = f.read()

        st.session_state.messages.append({
            "role": "assistant",
            "content": text,
            "audio": audio_data
        })
        # 必须在成功后再设为 False
        st.session_state.processing = False 
        st.rerun() 
    else:
        # 如果找不到文件，显示红色报错并停止 processing
        st.error(f"❌ 找不到音频文件！请确认 GitHub 仓库中 audio 文件夹内是否存在该文件，且文件名大小写一致。路径：{path}")
        st.session_state.processing = False

# 自动播放逻辑
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_idx = len(st.session_state.messages) - 1
    if "audio" in st.session_state.messages[-1]:
        autoplay_audio(st.session_state.messages[-1]["audio"], last_idx)
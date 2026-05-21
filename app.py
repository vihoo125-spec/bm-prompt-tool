import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

# --- 🎯 初始化 Session State 缓存 ---
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = None
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []

# --- 核心 CSS 魔法：复刻流媒体筛选栏 UI ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0E0E0E;
        color: #E0E0E0;
    }
    div[data-testid="stPills"] label {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 4px 12px !important;
        color: #A0A0A0 !important; 
        font-size: 15px !important;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[data-testid="stPills"] label:hover {
        color: #FFFFFF !important;
    }
    div[data-testid="stPills"] label[data-checked="true"] {
        color: #FFFFFF !important; 
        font-weight: bold !important;
        background-color: transparent !important;
    }
    .category-title {
        color: #00E5E5;
        font-weight: 600;
        font-size: 15px;
        line-height: 2.5; 
        text-align: left;
    }
    [data-testid="column"] {
        padding-left: 0 !important;
    }
    div[data-testid="stExpander"] {
        border-color: #333333 !important;
        background-color: #1A1A1A !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👞 BrunoMarc 智能生图提示词实验室")
st.caption("点击文字自由组合参数（单选），Gemini 自动生成电影级中文描述。")

# --- 2. 从“保险箱”安全读取 API Key ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    st.error("⚠️ 未在云端 Secrets 找到 API Key，请检查部署后台的设置。")
    st.stop()

# --- 3. 维度参数配置（已加入拍摄视角） ---
dims = {
    "鞋履款式": ["商务牛津鞋", "乐福鞋", "运动鞋", "正装皮鞋", "休闲平底鞋"],
    "人种角色": ["白人", "黑人"],
    "拍摄视角": ["正视", "侧视", "俯视", "仰视", "背影"], # 新增视角参数
    "人物构图": ["全身", "半身", "特写"],
    "季节氛围": ["春", "夏", "秋", "冬"],
    "服装搭配": ["修身西装套装", "商务休闲装", "直筒牛仔休闲装", "清爽短装", "毛呢大衣"],
    "人物动作": ["松弛站立", "迈步行走", "双腿交叠坐姿"],
    "拍摄场地": ["现代极简办公室", "欧洲街头", "奢华写字楼", "咖啡店", "机场VIP候机厅", "米其林餐厅"],
    "光影风格": ["室内自然光", "室外自然光", "午后侧光", "晚宴闪光灯", "百叶窗切割光影"],
    "画面尺寸": ["1:1", "2:3", "3:2", "16:9", "9:16"]
}

# --- 4. 标签化 UI 构建 ---
st.write("### 🎯 场景参数")
st.markdown("<br>", unsafe_allow_html=True) 

selected_options = {}

for label, options in dims.items():
    col1, col2 = st.columns([1, 11]) 
    with col1:
        st.markdown(f'<div class="category-title">{label}</div>', unsafe_allow_html=True)
    with col2:
        selected = st.pills(label, options, selection_mode="single", label_visibility="collapsed", key=f"pills_{label}")
        if selected:
            selected_options[label] = selected

st.divider()

# --- 5. Gemini 生成逻辑 ---
if st.button("✨ 一键生成 4 组提示词", type="primary"):
    summary = []
    selected_size = None # 默认不设定任何尺寸
    
    for k, v in selected_options.items():
        if k == "画面尺寸":
            selected_size = v
        else:
            summary.append(f"【{k}】: {v}")
    
    input_str = " | ".join(summary) if summary else "无需特定限制，自由发挥，展现 BrunoMarc 的顶级商业质感"

    # 动态尺寸尾缀生成规则
    size_instruction = f"每组提示词的最后，必须换行并单独加上这一句：比例：{selected_size}" if selected_size else "由于客户未指定画面尺寸选项，提示词结尾绝对不允许出现任何比例信息、尺寸描述或相关尾缀。"

    system_instruction = f"""
    你是一位顶级的商业广告摄影师。你的任务是严格根据客户指定的参数条件，为 BrunoMarc 品牌鞋履构思 4 个不同的高级拍摄场景，并写出中文自然语言提示词。
    
    【核心硬性准则 - 增强关联性】：
    你必须高强度地扣紧客户指定的条件！凡是用户选中的参数（如具体的拍摄视角、动作、构图等），必须在生成的文本中作为“核心视觉支配元素”得到显性呈现。严禁漏掉、严禁擅自篡改、严禁让 AI 的随意发挥冲淡了用户选定参数的权重。未选择的参数则基于品牌调性自然补充。
    
    【品牌调性】：高阶质感、现代职场精英、轻奢休闲。
    
    【生成规范】：
    1. 使用具有强画面感、电影广告质感的中文自然语言描述。
    2. 必须精细刻画：用户指定的鞋子款式与材质光泽、整体着装的搭配衔接、特定的拍摄视角和环境的氛围，以及光影的照射方向。
    3. 严禁画面出现：畸变、多余鞋带、杂乱背景、糟糕人体比例、不自然布料褶皱等不良元素。
    4. 直接输出4个段落即可，无需任何开场白、过渡句或解释。
    5. 【尺寸尾缀规则】：{size_instruction}
    
    【客户指定的硬性参数条件】：
    {input_str}
    """

    try:
        with st.spinner("Gemini 正在全速整理提示词..."):
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = model.generate_content(system_instruction)
            
            st.session_state.current_prompt = response.text
            st.session_state.prompt_history.insert(0, {
                "params": input_str,
                "content": response.text
            })
            
    except Exception as e:
        st.error(f"生成失败: {e}")

# --- 6. 结果展示区 ---
if st.session_state.current_prompt:
    st.success("渲染完成！")
    st.markdown(st.session_state.current_prompt)

# --- 7. 历史记录功能 ---
if st.session_state.prompt_history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("### 📜 历史生成记录")
    
    for i, record in enumerate(st.session_state.prompt_history[:10]):
        param_preview = record['params'][:40] + "..." if len(record['params']) > 40 else record['params']
        with st.expander(f"🕒 记录 {i+1} | {param_preview}"):
            st.markdown(record["content"])

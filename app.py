import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

# --- 🎯 初始化 Session State 缓存 ---
if "current_prompts_list" not in st.session_state:
    st.session_state.current_prompts_list = [] 
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []

# --- 核心 CSS 魔法：深度像素级复刻流媒体无边框文本筛选栏 ---
st.markdown("""
    <style>
    /* 全局暗黑背景 */
    .stApp {
        background-color: #0E0E0E;
        color: #E0E0E0;
    }
    
    /* 彻底扒掉 Pills 组件的外壳，将其变为纯文字展示 */
    div[data-testid="stPills"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    div[data-testid="stPills"] div[data-testid="stHorizontalBlock"] {
        gap: 0px !important; /* 消除原生块间距 */
    }
    
    /* 普通选项文字样式：完全扁平，无背景，无边框 */
    div[data-testid="stPills"] label {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 4px 16px !important; /* 调整左右间距，复刻原图文字排布 */
        color: #A0A0A0 !important; /* 未选中时的浅灰色 */
        font-size: 15px !important;
        cursor: pointer;
        transition: color 0.2s ease;
        border-radius: 0px !important;
    }
    
    /* 鼠标悬停变白 */
    div[data-testid="stPills"] label:hover {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }
    
    /* 核心高亮：选中状态变为高亮纯色（对应原图的青色/白色激活态），无底色气泡 */
    div[data-testid="stPills"] label[data-checked="true"] {
        color: #00E5E5 !important; /* 激活时的高亮青色 */
        font-weight: bold !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }

    /* 左侧分类标题样式 */
    .category-title {
        color: #00E5E5;
        font-weight: 600;
        font-size: 15px;
        line-height: 2.2; 
        text-align: left;
    }
    
    /* 紧凑布局微调 */
    [data-testid="column"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    /* 强制重置结果区文本框，使其完全融入背景、平铺不带任何滚动条 */
    div[data-testid="stTextArea"] textarea {
        background-color: #121212 !important;
        color: #E0E0E0 !important;
        border: 1px solid #262626 !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        overflow-y: hidden !important; 
        resize: none !important;
    }
    div[data-testid="stTextArea"] label {
        display: none !important;
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

# --- 3. 维度参数配置 ---
dims = {
    "鞋履款式": ["商务牛津鞋", "乐福鞋", "运动鞋", "正装皮鞋", "靴子"],
    "人种角色": ["白人", "黑人"],
    "拍摄视角": ["正视", "侧视", "俯视", "仰视", "背影"],
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
    selected_size = None 
    
    for k, v in selected_options.items():
        if k == "画面尺寸":
            selected_size = v
        else:
            summary.append(f"【{k}】: {v}")
    
    input_str = " | ".join(summary) if summary else "无需特定限制，自由发挥，展现 BrunoMarc 的顶级商业质感"

    size_instruction = f"每组提示词的最后，必须换行并单独加上这一句：比例：{selected_size}" if selected_size else "由于客户未指定画面尺寸选项，提示词结尾绝对不允许出现任何比例信息、尺寸描述或相关尾缀。"

    system_instruction = f"""
    你是一位顶级的商业广告摄影师。你的任务是严格根据客户指定的参数条件，为 BrunoMarc 品牌鞋履构思 4 个不同的高级拍摄场景，并写出中文自然语言提示词。
    
    【🔥 鞋款与材质绝对绑定准则 - 严防冲突】：
    你必须根据当前选中的鞋子款式，应用完全不同的材质细节描述：
    1. 当用户选中【运动鞋】或【休闲平底鞋】时：严禁出现“亮面牛皮”、“抛光皮革”、“擦色漆皮”、“正装中底”等任何商务正装鞋的词汇！必须具体刻画为“科技网面透气材质”、“细腻磨砂绒面”、“轻量化运动中底”或“高弹橡胶鞋底细节”。服装必须往阳光活力或现代街头方向延伸。
    2. 当用户选中【商务牛津鞋】、【正装皮鞋】或【乐福鞋】时：必须具体刻画为“顶级抛光牛皮”、“细腻擦色鞋尖”、“高级皮革半哑光泽”或  “精细缝线皮革侧面”。
    
    【核心硬性准则】：
    你必须高强度地扣紧客户指定的条件！凡是用户选中的参数，必须在生成的文本中作为“核心视觉支配元素”得到显性呈现。
    
    【生成规范】：
    1. 使用具有强画面感、电影广告质感的中文自然语言描述。
    2. 必须精细刻画：对应的鞋子款式与正确材质、整体着装的搭配衔接、特定的拍摄视角和环境的氛围，以及光影的照射方向。
    3. 严禁画面出现：畸变、多余鞋带、杂乱背景、糟糕人体比例等不良元素。
    4. 必须输出正好 4 个独立的场景段落。每两组之间用特殊符号 `[SPLIT]` 隔开，以便系统切分。不要有任何开场白、序号或结束语。
    5. 【尺寸尾缀规则】：{size_instruction}
    
    【客户指定的硬性参数条件】：
    {input_str}
    """

    try:
        with st.spinner("Gemini 正在全速整理提示词..."):
            model = genai.GenerativeModel('gemini-3.5-flash')
            response = model.generate_content(system_instruction)
            
            raw_text = response.text
            if "[SPLIT]" in raw_text:
                parts = [p.strip() for p in raw_text.split("[SPLIT]") if p.strip()]
            else:
                parts = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            
            final_parts = parts[:4]
            
            st.session_state.current_prompts_list = final_parts
            st.session_state.prompt_history.insert(0, {
                "params": input_str,
                "content": final_parts
            })
            
    except Exception as e:
        st.error(f"生成失败: {e}")

# --- 6. 结果展示区 (彻底闭合了双引号，修复了报错) ---
if st.session_state.current_prompts_list:
    st.success("渲染完成！(下方内容已固定，修改参数不会导致其消失)")
    
    for idx, prompt_text in enumerate(st.session_state.current_prompts_list):
        st.markdown(f"##### 🎬 场景方案 {idx + 1}")
        
        lines_count = max(len(prompt_text.split('\n')), 4)
        box_height = lines_count * 28  
        
        st.text_area(
            label=f"prompt_{idx}", 
            value=prompt_text, 
            height=box_height, 
            key=f"display_area_{idx}"
        )

# --- 7. 历史记录功能 ---
if st.session_state.prompt_history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.write("### 📜 历史生成记录")
    
    for i, record in enumerate(st.session_state.prompt_history[:10]):
        param_preview = record['params'][:40] + "..." if len(record['params']) > 40 else record['params']
        with st.expander(f"🕒 记录 {i+1} | {param_preview}"):
            for idx, hist_text in enumerate(record["content"]):
                st.markdown(f"**方案 {idx + 1}**")
                hist_lines = max(len(hist_text.split('\n')), 4)
                st.text_area(
                    label=f"hist_prompt_{i}_{idx}", 
                    value=hist_text, 
                    height=hist_lines * 28, 
                    key=f"hist_area_{i}_{idx}"
                )

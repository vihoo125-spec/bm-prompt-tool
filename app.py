import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

# --- 核心 CSS 魔法：复刻流媒体筛选栏 UI ---
st.markdown("""
    <style>
    /* 全局背景设为暗色系以契合原图，并调整整体字体 */
    .stApp {
        background-color: #0E0E0E;
        color: #E0E0E0;
    }
    
    /* 隐藏默认的 pills 边框和背景，将其变成纯文本外观 */
    div[data-testid="stPills"] label {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 4px 12px !important;
        color: #A0A0A0 !important; /* 未选中时的浅灰色 */
        font-size: 15px !important;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    /* 鼠标悬停时的颜色变化 */
    div[data-testid="stPills"] label:hover {
        color: #FFFFFF !important;
    }
    
    /* 选中状态：纯文字变亮，不带背景框 */
    div[data-testid="stPills"] label[data-checked="true"] {
        color: #FFFFFF !important; 
        font-weight: bold !important;
        background-color: transparent !important;
    }

    /* 左侧分类标题的样式（对应截图里的青色标题） */
    .category-title {
        color: #00E5E5;
        font-weight: 600;
        font-size: 15px;
        line-height: 2.5; /* 让标题和右侧的标签垂直居中对齐 */
        text-align: left;
    }
    
    /* 调整列间距，让整体更紧凑 */
    [data-testid="column"] {
        padding-left: 0 !important;
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
    "鞋履款式": ["商务德比鞋", "牛津鞋", "经典乐福鞋", "切尔西靴", "商务高帮靴", "轻奢白板鞋"],
    "人种角色": ["白人", "黑人"],
    "人物构图": ["全身", "半身", "特写"],
    "季节氛围": ["初春微凉", "盛夏清爽", "金秋质感", "寒冬温暖"],
    "服装搭配": ["高定修身西装套装", "商务休闲夹克", "直筒牛仔休闲装", "毛呢大衣搭配", "夏季清爽短装"],
    "人物动作": ["静止站立特写", "迈步行走抓拍", "双腿交叠坐姿", "弯腰系鞋带瞬间", "正跨出车门"],
    "拍摄场地": ["现代极简办公室", "欧洲街头咖啡馆", "奢华写字楼大堂", "米其林餐厅", "机场VIP候机厅", "光影摄影棚"],
    "光影风格": ["室内自然光", "室外自然光", "午后侧光", "晚宴闪光灯", "百叶窗切割光影"],
    "画面尺寸": ["1:1", "2:3", "3:2", "16:9", "9:16"]
}

# --- 4. 标签化 UI 构建 (分列排版) ---
st.write("### 🎯 场景参数")
st.markdown("<br>", unsafe_allow_html=True) # 增加一点留白

selected_options = {}

# 遍历字典，将标题放在左列，选项放在右列
for label, options in dims.items():
    col1, col2 = st.columns([1, 11]) # 1:11 的宽度比，左侧极窄
    
    with col1:
        # 左侧青色标题
        st.markdown(f'<div class="category-title">{label}</div>', unsafe_allow_html=True)
    
    with col2:
        # 右侧选项（隐藏 Streamlit 原本的标题标签）
        selected = st.pills(label, options, selection_mode="single", label_visibility="collapsed", key=f"pills_{label}")
        if selected:
            selected_options[label] = selected

st.divider()

# --- 5. Gemini 生成逻辑 ---
if st.button("✨ 一键生成 4 组高级提示词", type="primary"):
    summary = []
    selected_size = "3:4" 
    
    for k, v in selected_options.items():
        if k == "画面尺寸":
            selected_size = v
        else:
            summary.append(f"{k}: {v}")
    
    input_str = " | ".join(summary) if summary else "无需特定限制，自由发挥，展现 BrunoMarc 的顶级商业质感"

    system_instruction = f"""
    你是一位顶级的商业广告摄影师。你的任务是为 BrunoMarc 鞋履构思 4 个不同的拍摄场景，并写出中文自然语言提示词。
    
    【品牌调性】：高阶质感、现代职场精英、轻奢休闲。
    
    【生成规范】：
    1. 使用具有画面感、电影感的中文自然语言描述。
    2. 必须详细刻画：鞋子的材质光泽、整体服装的搭配衔接、环境的氛围以及光影的照射方向。
    3. 严禁画面出现：畸变、多余鞋带、杂乱背景、糟糕人体比例、不自然布料褶皱等不良元素。
    4. 直接输出4个段落即可，无需任何开场白或解释。
    5. 每组提示词的最后，必须换行并单独加上这一句：比例：{selected_size}
    
    【客户指定的条件】：
    {input_str}
    """

    try:
        with st.spinner("Gemini 正在全速渲染商业场景..."):
            # 使用最新预览版模型，解除频率限制提示
            model = genai.GenerativeModel('gemini-3-flash-preview')
            response = model.generate_content(system_instruction)
            
            st.success("渲染完成！")
            st.markdown(response.text)
            
    except Exception as e:
        st.error(f"生成失败: {e}")

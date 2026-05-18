import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置与深度 UI 美化 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

# 注入自定义 CSS，复刻截图里的“极简无边框纯文本”过滤条视觉效果
st.markdown("""
    <style>
    /* 隐藏选项的默认边框和背景 */
    div[data-testid="stPills"] label {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 6px 14px !important;
        color: #888888 !important; /* 未选中时的灰色 */
        font-size: 15px !important;
        cursor: pointer;
    }
    /* 鼠标悬停时稍微变亮 */
    div[data-testid="stPills"] label:hover {
        color: #cccccc !important;
    }
    /* 选中状态：变成截图里的青色，并加粗 */
    div[data-testid="stPills"] label[data-checked="true"] {
        color: #00E5E5 !important; 
        font-weight: bold !important;
        background-color: transparent !important;
    }
    /* 调整整体间距，让它看起来更紧凑 */
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👞 BrunoMarc 智能生图提示词实验室")
st.caption("点击标签自由组合参数（单选），Gemini 自动生成电影级中文描述。")

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

# --- 4. 标签化 UI 构建 ---
st.write("### 🎯 场景参数 (同一参数仅支持单选，不选则由 AI 自由发挥)")

selected_options = {}

# 所有标签统一为单选模式
for label, options in dims.items():
    # 使用水平排版，让 label 和选项在一行（或者紧凑排布）
    selected = st.pills(label, options, selection_mode="single", default=None)
    if selected:
        selected_options[label] = selected

st.divider()

# --- 5. Gemini 生成逻辑 ---
if st

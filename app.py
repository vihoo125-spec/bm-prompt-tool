import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置与美化 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

# 自定义 CSS 让标签看起来更像图片中的筛选器
st.markdown("""
    <style>
    div[data-baseweb="tab-list"] { gap: 20px; }
    .stHeading { padding-top: 1rem; }
    .prompt-card { 
        background-color: #f0f2f6; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #005088;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👞 BrunoMarc 智能生图提示词实验室")
st.caption("基于 Gemini 3.0 驱动的自然语言提示词生成系统")

# --- 2. 配置 Gemini API ---
# 建议在 Streamlit 平台的 Secrets 中设置 API_KEY
# 如果本地测试，请直接替换下面的字符串
GEMINI_API_KEY = st.sidebar.text_input("输入 Gemini API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("请在左侧侧边栏输入您的 Gemini API Key 才能开始生成。")

# --- 3. 维度参数配置 ---
dims = {
    "鞋履款式": ["商务德比鞋", "牛津鞋", "乐福鞋", "切尔西靴", "商务靴", "正装板鞋"],
    "鞋履材质": ["亮面牛皮", "反绒面革", "哑光雾面", "荔枝纹皮", "编制网面"],
    "季节氛围": ["春秋凉爽", "夏季清爽", "冬季温暖"],
    "服装搭配": ["修身西装", "商务休闲/Chinos", "高级牛仔裤", "风衣/大衣", "短裤/夏季休闲"],
    "人物动作": ["站立静态", "迈步行走", "侧坐姿势", "系鞋带", "上下车"],
    "拍摄场地": ["现代办公室", "城市街道", "写字楼大堂", "高档餐厅", "机场候机厅", "自然郊外"],
    "光影风格": ["黄金时刻", "百叶窗光影", "工作室硬光", "柔和自然光", "霓虹夜景"],
    "画面尺寸": ["1:1", "2:3", "3:2", "16:9", "9:16"]
}

# --- 4. 筛选器 UI 构建 ---
st.write("### 🎯 场景参数筛选（点击选择，可多选或不选）")

selected_options = {}

for label, options in dims.items():
    # 使用最新的 segmented_control 组件实现类似图片的标签效果
    selected_options[label] = st.segmented_control(
        label, 
        options, 
        selection_mode="multiple" if label != "画面尺寸" else "single",
        default=None
    )

st.divider()

# --- 5. 生成逻辑 ---
if st.button("✨ 生成 4 组中文自然语言提示词", type="primary", use_container_width=True):
    if not GEMINI_API_KEY:
        st.error("缺少 API Key！")
    else:
        # 整理选中的标签内容
        summary = []
        for k, v in selected_options.items():
            if v:
                summary.append(f"{k}: {v}")
        
        input_str = " | ".join(summary) if summary else "自由发挥，展现 BrunoMarc 的高级感"
        
        # 构建 System Prompt
        system_instruction = f"""
        你是一位顶级的商业摄影师和AI绘图专家。
        你的任务是根据提供的关键词，为 BrunoMarc 品牌鞋履生成 4 组完全不同的、具有自然语言叙述感的中文提示词。
        
        【品牌调性】：
        高质感、现代职场、轻奢休闲、注重细节、专业摄影。
        
        【生成要求】：
        1. 必须使用流畅的中文自然语言，像是在描述一个电影分镜。
        2. 强调鞋子的质感、皮革的纹理、以及与裤装搭配的衔接。
        3. 背景要描述得具体且有氛围感，融入光影细节。
        4. 反向提示词要求（后台自动注入）：严禁画面出现扭曲、多余肢体、低画质、多余线条、Logo变形。
        5. 每组输出最后必须附带对应的 Midjourney 参数 --ar [尺寸]。
        
        【当前用户选择的参数】：
        {input_str}
        
        请输出 4 组提示词：
        """

        try:
            with st.spinner("Gemini 正在构思高级场景..."):
                model = genai.GenerativeModel('gemini-1.5-pro') # 或使用你指定的版本
                response = model.generate_content(system_instruction)
                
                # 假设 AI 返回的是分段的文本，我们进行简单的处理展示
                prompts = response.text.split("\n\n")[:4] # 尝试提取4组
                
                cols = st.columns(2)
                for idx, p in enumerate(response.text.split("---") if "---" in response.text else [response.text]):
                    # 如果 AI 没有按格式输出，这里可能需要更复杂的切分逻辑
                    # 简单演示：直接展示返回内容
                    st.markdown(f"#### 场景方案 {idx+1}")
                    st.info(p)
                    
        except Exception as e:
            st.error(f"调用 Gemini 出错: {e}")

# --- 6. 底部说明 ---
st.divider()
st.caption("提示：BrunoMarc 内部工具 | 反向提示词已在后台自动优化 | 建议配合 Midjourney v6 使用")

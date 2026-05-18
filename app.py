import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

st.title("👞 BrunoMarc 智能生图提示词实验室")
st.caption("点击标签自由组合参数，Gemini 自动生成电影级中文描述。")

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
    "季节氛围": ["初春微凉", "盛夏清爽", "金秋质感", "寒冬温暖"],
    "服装搭配": ["高定修身西裤", "商务休闲卡其裤", "深色直筒牛仔裤", "毛呢大衣衣角", "夏季休闲短裤"],
    "人物动作": ["静止站立特写", "迈步行走抓拍", "双腿交叠坐姿", "弯腰系鞋带瞬间", "正跨出车门"],
    "拍摄场地": ["现代极简办公室", "欧洲街头咖啡馆", "奢华写字楼大堂", "米其林餐厅地毯", "机场VIP候机厅", "光影摄影棚"],
    "光影风格": ["落日黄金时刻", "百叶窗切割光影", "工作室顶部分布光", "阴天柔和自然光", "赛博朋克霓虹夜景"]
}

sizes = ["1:1", "2:3", "3:2", "16:9", "9:16"]

# --- 4. 标签化 UI 构建 (复刻截图效果) ---
st.write("### 🎯 场景参数 (点击选中，可多选，默认由 AI 自由发挥)")

selected_options = {}

# 使用 pills 组件实现纯净的标签交互
for label, options in dims.items():
    selected = st.pills(label, options, selection_mode="multi", default=None)
    if selected:
        selected_options[label] = selected

st.write("### 📐 画面尺寸 (单选)")
selected_size = st.pills("比例", sizes, selection_mode="single", default=None)

st.divider()

# --- 5. Gemini 生成逻辑 ---
if st.button("✨ 一键生成 4 组高级提示词", type="primary"):
    # 拼接用户选中的参数
    summary = []
    for k, v in selected_options.items():
        summary.append(f"{k}: {', '.join(v)}")
    
    input_str = " | ".join(summary) if summary else "无需特定限制，自由发挥，展现 BrunoMarc 的顶级商业质感"
    ar_str = f"--ar {selected_size}" if selected_size else "--ar 3:4"

    system_instruction = f"""
    你是一位顶级的商业广告摄影师。你的任务是为 BrunoMarc 鞋履构思 4 个不同的拍摄场景，并写出中文自然语言提示词。
    
    【品牌调性】：高阶质感、现代职场精英、轻奢休闲。
    
    【生成规范】：
    1. 使用具有画面感、电影感的中文自然语言描述。
    2. 必须详细刻画：鞋子的材质光泽、裤脚的堆叠细节、环境的氛围以及光影的照射方向。
    3. 直接输出4个段落即可，无需任何开场白或解释。
    
    【客户指定的条件】：
    {input_str}
    """

    try:
        with st.spinner("Gemini 正在渲染商业场景..."):
            # 使用较新的通用模型版本
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(system_instruction)
            
            st.success("渲染完成！")
            st.markdown(response.text)
            
            # 后台强制注入反向提示词，直接展示给用户复制
            st.info("**🚫 商业出图必带反向提示词 (Negative Prompt):**\n\n`ugly, deformed, mutated, extra laces, messy background, text, watermark, bad anatomy, bad proportions, unnatural fabric folds, unrealistic lighting, distorted logo`")
            
    except Exception as e:
        st.error(f"生成失败: {e}")

import streamlit as st
import google.generativeai as genai

# --- 1. 页面配置 ---
st.set_page_config(page_title="BrunoMarc AI PRO", layout="wide")

st.title("👞 BrunoMarc 智能生图提示词实验室")
st.caption("点击标签自由组合参数（单选），Gemini 自动生成电影级中文描述。")

# --- 2. 从“保险箱”安全读取 API Key ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    st.error("⚠️ 未在云端 Secrets 找到 API Key，请检查部署后台的设置。")
    st.stop()

# --- 3. 维度参数配置 (重构版) ---
dims = {
    "鞋履款式": ["商务德比鞋", "牛津鞋", "经典乐福鞋", "切尔西靴", "商务高帮靴", "轻奢白板鞋"],
    "人种角色": ["白人", "黑人"],
    "人物构图": ["全身", "半身", "特写"],
    "季节氛围": ["初春微凉", "盛夏清爽", "金秋质感", "寒冬温暖"],
    "服装搭配": ["高定修身西装套装", "商务休闲夹克", "直筒牛仔休闲装", "毛呢大衣搭配", "夏季清爽短装"], # 去除颜色，改为整体着装
    "人物动作": ["静止站立特写", "迈步行走抓拍", "双腿交叠坐姿", "弯腰系鞋带瞬间", "正跨出车门"],
    "拍摄场地": ["现代极简办公室", "欧洲街头咖啡馆", "奢华写字楼大堂", "米其林餐厅", "机场VIP候机厅", "光影摄影棚"],
    "光影风格": ["室内自然光", "室外自然光", "午后侧光", "晚宴闪光灯", "百叶窗切割光影"], # 更新光影选项
    "画面尺寸": ["1:1", "2:3", "3:2", "16:9", "9:16"] # 移入主参数区
}

# --- 4. 标签化 UI 构建 ---
st.write("### 🎯 场景参数 (点击选中，同一参数仅支持单选，不选则由 AI 自由发挥)")

selected_options = {}

# 所有标签统一为单选模式 (single)
for label, options in dims.items():
    selected = st.pills(label, options, selection_mode="single", default=None)
    if selected:
        selected_options[label] = selected

st.divider()

# --- 5. Gemini 生成逻辑 ---
if st.button("✨ 一键生成 4 组高级提示词", type="primary"):
    summary = []
    # 提取尺寸参数，如果没有选，给一个默认值
    selected_size = "3:4" 
    
    for k, v in selected_options.items():
        if k == "画面尺寸":
            selected_size = v
        else:
            summary.append(f"{k}: {v}")
    
    input_str = " | ".join(summary) if summary else "无需特定限制，自由发挥，展现 BrunoMarc 的顶级商业质感"

    # 将反向提示词和尺寸逻辑写进系统指令，不在前端展示
    system_instruction = f"""
    你是一位顶级的商业广告摄影师。你的任务是为 BrunoMarc 鞋履构思 4 个不同的拍摄场景，并写出中文自然语言提示词。
    
    【品牌调性】：高阶质感、现代职场精英、轻奢休闲。
    
    【生成规范】：

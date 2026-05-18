import streamlit as st
import random

# 设置页面基本信息
st.set_page_config(page_title="BrunoMarc AI 提示词生成器", layout="centered")
st.title("👞 BrunoMarc 商业生图提示词系统")
st.caption("模块化组合，一键生成超写实商业级摄影提示词。")

st.divider()

# 1. 维度数据配置 (可随时增删)
dimensions = {
    "鞋履款式": {
        "商务牛津鞋": "polished leather Men's Oxford shoes",
        "休闲乐福鞋": "classic suede Men's Loafers",
        "切尔西靴": "premium leather Chelsea boots",
        "运动板鞋": "minimalist white leather sneakers"
    },
    "构图视角": {
        "足部特写": "Macro shot focusing on shoes, close-up, highly detailed",
        "下半身切图": "Cropped shot from waist down, showing trouser break",
        "全身场景": "Full-body shot, lifestyle editorial"
    },
    "动态姿态": {
        "行走中": "walking forward, dynamic motion, capturing mid-stride",
        "静止站立": "standing elegantly, confident posture",
        "交叠双腿坐姿": "sitting casually with legs crossed"
    },
    "服装搭配": {
        "正装西裤": "wearing sharp bespoke dress pants",
        "商务休闲九分裤": "wearing smart casual ankle-length chinos",
        "深色牛仔裤": "wearing premium dark straight-leg denim"
    },
    "核心场景": {
        "现代写字楼": "in a minimalist modern office lobby with glass walls",
        "街头咖啡厅": "at a European-style outdoor cafe street",
        "极简影棚": "in a high-end minimalist photography studio with clean backdrop",
        "高级酒店": "on a plush carpet in a luxury hotel corridor"
    },
    "光影天气": {
        "黄昏暖光": "golden hour sunset lighting, soft warm shadows",
        "百叶窗光影": "cinematic studio blinds light and shadow effect, dramatic",
        "柔和自然光": "soft diffused daylight, flat flattering light",
        "影棚轮廓光": "professional studio rim lighting, highlighting leather texture"
    }
}

# 2. UI 渲染与用户交互 (主界面)
col1, col2 = st.columns(2)
selected_params = {}

keys = list(dimensions.keys())
for i, key in enumerate(keys):
    with col1 if i % 2 == 0 else col2:
        choice = st.selectbox(f"选择{key}", list(dimensions[key].keys()), key=f"select_{key}")
        selected_params[key] = dimensions[key][choice]

# 随机灵感按钮
if st.button("🎲 缺乏灵感？随机生成一组搭配"):
    for key in keys:
        random_choice = random.choice(list(dimensions[key].keys()))
        # 更新 session_state 以同步 UI 变化
        st.session_state[f"select_{key}"] = random_choice
    st.rerun()

st.divider()

# 3. 高级设置 (折叠面板，保持主界面极简)
with st.expander("⚙️ 高级渲染参数 (Midjourney 专用)"):
    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        aspect_ratio = st.selectbox("画面比例 (--ar)", ["3:4 (竖屏海报)", "16:9 (横屏横幅)", "1:1 (电商主图)"])
        ar_value = aspect_ratio.split(" ")[0]
    with adv_col2:
        stylize = st.slider("风格化程度 (--s)", min_value=0, max_value=1000, value=250, step=50)

# 4. 提示词拼接逻辑
base_quality = "Commercial advertising photography, high-end fashion catalog, shot on Hasselblad X1D, 8k resolution, extremely detailed leather texture, PBR rendering, photorealistic"

prompt_components = [
    selected_params["构图视角"],
    selected_params["鞋履款式"],
    selected_params["服装搭配"],
    selected_params["动态姿态"],
    selected_params["核心场景"],
    selected_params["光影天气"],
    base_quality
]

# 组合正向提示词与后缀
final_prompt = ", ".join(prompt_components)
final_prompt += f" --ar {ar_value} --s {stylize} --v 6.0 --style raw"

# 行业标准反向提示词
negative_prompt = "ugly, deformed, mutated, extra laces, messy background, text, watermark, bad anatomy, bad proportions, unnatural fabric folds, unrealistic lighting"

# 5. 输出展示
st.subheader("📋 最终提示词 (Prompt)")
st.caption("鼠标悬停在下方代码框右上角，点击图标即可一键复制")
st.code(final_prompt, language="markdown")

st.subheader("🚫 反向提示词 (Negative Prompt)")
st.caption("用于排除不良画面（如有多余结构或变形），建议每次均带上")
st.code(negative_prompt, language="markdown")

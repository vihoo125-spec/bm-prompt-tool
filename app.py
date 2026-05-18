import streamlit as st

# 设置页面基本信息
st.set_page_config(page_title="BrunoMarc AI 提示词生成器", layout="centered")
st.title("👞 BrunoMarc 鞋履场景生图提示词生成器")
st.caption("选择对应维度参数，一键生成标准化商业摄影提示词。")

st.divider()

# 1. 维度数据配置
dimensions = {
    "鞋履款式": {
        "商务牛津鞋": "polished leather Men's Oxford shoes",
        "休闲乐福鞋": "classic suede Men's Loafers",
        "切尔西靴": "premium leather Chelsea boots"
    },
    "构图视角": {
        "足部特写": "Macro shot focusing on shoes, close-up",
        "下半身切图": "Cropped shot from waist down",
        "全身场景": "Full-body shot"
    },
    "动态姿态": {
        "行走中": "walking forward, dynamic motion",
        "静止站立": "standing elegantly",
        "交叠双腿坐姿": "sitting with legs crossed"
    },
    "服装搭配": {
        "正装西裤": "wearing sharp dress pants",
        "商务休闲九分裤": "wearing smart casual ankle-length chinos",
        "深色牛仔裤": "wearing dark straight-leg jeans"
    },
    "核心场景": {
        "现代写字楼": "in a minimalist modern office lobby with glass walls",
        "街头咖啡厅": "at a European-style outdoor cafe street",
        "机场候机厅": "in a luxurious airport lounge"
    },
    "光影天气": {
        "黄昏暖光": "golden hour sunset lighting, soft shadows",
        "百叶窗光影": "cinematic studio blinds light and shadow effect",
        "柔和自然光": "soft diffused daylight"
    }
}

# 2. UI 渲染与用户交互
col1, col2 = st.columns(2)

selected_params = {}
keys = list(dimensions.keys())

for i, key in enumerate(keys):
    # 将选择框均匀分布在两列中
    with col1 if i % 2 == 0 else col2:
        choice = st.selectbox(f"选择{key}", list(dimensions[key].keys()))
        selected_params[key] = dimensions[key][choice]

st.divider()

# 3. 提示词拼接逻辑
base_quality = "Commercial advertising photography, high-end fashion catalog, 8k, extremely detailed leather texture, shallow depth of field, sharp focus on footwear"

prompt_components = [
    selected_params["构图视角"],
    selected_params["鞋履款式"],
    selected_params["服装搭配"],
    selected_params["动态姿态"],
    selected_params["核心场景"],
    selected_params["光影天气"],
    base_quality
]

final_prompt = ", ".join(prompt_components)

# 4. 输出展示
st.subheader("📋 生成的 AI 提示词 (Prompt)")
st.text_area(label="直接复制到 Midjourney / SD 使用：", value=final_prompt, height=120)

if st.button("✨ 一键复制提示词"):
    # 提示词已经渲染在 text_area 中，用户可直接选中复制
    st.success("请长按或双击上方文本框进行复制！")
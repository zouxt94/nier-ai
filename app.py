"""
Nier AI —— AI 模型评测与试用平台
"""

import os
import streamlit as st
from openai import OpenAI

# ==================== 隐藏 Streamlit 默认 UI ====================
st.set_page_config(page_title="Nier AI", page_icon="🤖", layout="wide")

# 隐藏顶部 deploy 白条 + 底部 streamlit 标识
hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==================== 环境变量 + Secrets 配置 ====================
def _get_config(key, default_val):
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets.get(key, default_val)
    except Exception:
        return default_val

default_key     = _get_config("API_KEY", "")
default_base    = _get_config("API_BASE", "")
default_model   = _get_config("MODEL", "deepseek-chat")
access_password = _get_config("ACCESS_PASSWORD", "")

is_deployed = bool(default_key)
need_login  = is_deployed and bool(access_password)

api_key  = default_key
api_base = default_base
model    = default_model

# ==================== 全局 CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    .stApp { background: #0d0d14; }

    /* 顶部空白区域消除 */
    .block-container { padding-top: 1rem !important; max-width: 100% !important; }
    .stMainBlockContainer { padding-top: 1rem !important; max-width: 100% !important; }

    /* ==== 导航栏 ==== */
    .navbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 40px; margin-bottom: 0;
    }
    .nav-logo { font-size: 20px; font-weight: 700; color: #a78bfa; letter-spacing: -0.5px; }
    .nav-links { display: flex; gap: 28px; align-items: center; }

    /* ==== 导航按钮（暗色可见底框） ==== */
    [data-testid="stButton"] button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        color: #cbd5e1 !important;
        background: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.15) !important;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: rgba(139,92,246,0.18) !important;
        color: #c4b5fd !important;
        border: 1px solid rgba(139,92,246,0.30) !important;
    }

    /* ==== Hero ==== */
    .hero-section {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 60px 20px 40px; position: relative; overflow: hidden;
    }
    .hero-glow-1 {
        position: absolute; top: -100px; left: 50%; transform: translateX(-50%);
        width: 380px; height: 380px; border-radius: 50%;
        background: radial-gradient(circle at center,
            rgba(139,92,246,0.16) 0%, rgba(99,102,241,0.08) 25%,
            rgba(6,182,212,0.04) 50%, rgba(0,0,0,0) 70%);
        pointer-events: none; z-index: 0;
    }
    .hero-glow-2 {
        position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
        width: 240px; height: 240px; border-radius: 50%;
        background: radial-gradient(circle at center,
            rgba(167,139,250,0.22) 0%, rgba(139,92,246,0.06) 40%, rgba(0,0,0,0) 65%);
        pointer-events: none; z-index: 0;
    }
    .hero-content { position: relative; z-index: 1; text-align: center; max-width: 600px; }
    .hero-title {
        font-size: 38px; font-weight: 700; color: #f1f5f9; letter-spacing: -1px; margin-bottom: 10px;
    }
    .hero-title span {
        background: linear-gradient(135deg, #a78bfa, #6ee7b7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-desc {
        font-size: 15px; color: #94a3b8; line-height: 1.6; margin-bottom: 24px;
    }

    /* ==== 搜索框（暗色融合） ==== */
    .search-box {
        display: flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px; padding: 8px 18px; max-width: 360px; margin: 0 auto;
        transition: border-color 0.2s;
    }
    .search-box:focus-within { border-color: rgba(167,139,250,0.3); }
    .search-box input {
        background: transparent; border: none; outline: none; color: #cbd5e1;
        font-size: 14px; width: 100%;
    }
    .search-box input::placeholder { color: #475569; }
    .search-box .icon { color: #475569; font-size: 16px; }

    /* ==== 文章区域 ==== */
    .section-title {
        text-align: center; padding: 32px 0 20px;
        font-size: 22px; font-weight: 600; color: #e2e8f0;
    }
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px; padding: 0 32px; max-width: 1300px; margin: 0 auto;
    }
    @media (max-width: 1100px) { .cards-grid { grid-template-columns: repeat(3, 1fr); } }
    @media (max-width: 700px)  { .cards-grid { grid-template-columns: repeat(2, 1fr); } }

    .article-card {
        background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px; overflow: hidden; cursor: pointer;
        transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    }
    .article-card:hover {
        transform: translateY(-4px); border-color: rgba(167,139,250,0.25);
        box-shadow: 0 8px 30px rgba(139,92,246,0.10);
    }
    .card-banner {
        height: 100px; display: flex; align-items: center; justify-content: center; font-size: 32px;
    }
    .bg-1 { background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); }
    .bg-2 { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
    .bg-3 { background: linear-gradient(135deg, #1a1130 0%, #4c1d95 100%); }
    .bg-4 { background: linear-gradient(135deg, #0c1929 0%, #0ea5a0 100%); }
    .bg-5 { background: linear-gradient(135deg, #1a0a2e 0%, #6b21a8 100%); }
    .card-body { padding: 12px 14px 14px; }
    .card-body .title { font-size: 13px; font-weight: 600; color: #e2e8f0; line-height: 1.4; margin-bottom: 6px; }
    .card-body .meta { font-size: 11px; color: #64748b; display: flex; gap: 8px; align-items: center; }
    .card-body .tag {
        display: inline-block; background: rgba(167,139,250,0.12); color: #a78bfa;
        font-size: 10px; padding: 2px 8px; border-radius: 10px;
    }

    /* ==== 分页通用 Hero ==== */
    .page-hero {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 50px 20px 30px; position: relative; overflow: hidden;
    }
    .page-title { font-size: 30px; font-weight: 700; color: #f1f5f9; text-align: center; position: relative; z-index: 1; }
    .page-desc { font-size: 14px; color: #94a3b8; text-align: center; margin-top: 8px; max-width: 500px; }

    /* ==== 内容区容器 ==== */
    .content-wrap { max-width: 1000px; margin: 0 auto; padding: 0 20px; }

    /* ==== 全局禁纯白（最强制） ==== */
    input, textarea, select,
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"],
    [data-baseweb="input"] > div, [data-baseweb="input"] input,
    div[data-testid="stTextInput"], div[data-testid="stTextInput"] *,
    div[data-testid="stTextInput"] input, div[data-testid="stTextInput"] div,
    .stTextInput, .stTextInput *, .stTextArea, .stTextArea *, .stSelectbox, .stSelectbox * {
        background-color: rgba(255,255,255,0.04) !important;
        color: #cbd5e1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
        --tw-ring-color: transparent !important;
    }
    input::placeholder, textarea::placeholder { color: #475569 !important; }

    /* ==== Streamlit 组件覆盖 ==== */
    .stButton > button {
        border-radius: 8px !important; font-weight: 500 !important; font-size: 13px !important;
        transition: all 0.2s !important; background-color: rgba(255,255,255,0.05) !important;
    }
    .stButton > button[kind="primary"]:not([key*="nav_"]) {
        background: linear-gradient(135deg, #7c3aed, #6366f1) !important; color: #f1f5f9 !important; border: none !important;
    }
    .stButton > button[kind="primary"]:not([key*="nav_"]):hover {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    }
    div[data-testid="stTextInput"] input {
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important; font-size: 14px !important; padding: 10px 14px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(167,139,250,0.35) !important;
    }
    .stTextArea textarea {
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 10px !important;
    }
    .stTextArea textarea:focus { border-color: rgba(167,139,250,0.35) !important; }
    .stSelectbox > div > div {
        border: 1px solid rgba(255,255,255,0.10) !important; border-radius: 10px !important;
    }
    .stDataFrame {
        background: rgba(255,255,255,0.02) !important; border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }
    .stDataFrame th { background: rgba(255,255,255,0.04) !important; color: #94a3b8 !important; font-size: 12px !important; }
    .stDataFrame td { color: #cbd5e1 !important; font-size: 13px !important; }
    hr { border-color: rgba(255,255,255,0.06); }
    .stAlert { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; }
    .stSpinner > div { border-color: #a78bfa !important; }
</style>
""", unsafe_allow_html=True)

# ==================== 登录检查 ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if need_login and not st.session_state.logged_in:
    st.markdown('<div class="navbar"><span class="nav-logo">🤖 Nier AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="max-width:400px;margin:100px auto;text-align:center;">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#e2e8f0;">🔐 输入密码访问</h2>', unsafe_allow_html=True)
    pwd = st.text_input("密码", type="password", placeholder="输入密码后按回车", label_visibility="collapsed")
    if pwd:
        if pwd == access_password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("密码错误")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==================== 文章数据 ====================
ARTICLES = [
    {"id":"deepseek-vs-gpt","banner":"⚔️","bg":"bg-1","title":"DeepSeek vs GPT-4o 深度对比：2026 年谁更值得付费？","date":"2026-05-15","tags":["对比评测","DeepSeek","GPT-4o"],
     "content":"""
### 一句话结论

**中文为主、预算有限 → DeepSeek** | **全能选手、多模态 → GPT-4o** | **两个搭配用最香**

**价格差距**

| | DeepSeek V3 | GPT-4o |
|--|-----------|--------|
| 输入(¥/M tok) | **1** | 18 |
| 输出(¥/M tok) | **2** | 72 |

用 GPT-4o 聊一首诗，DeepSeek 可以写一篇论文。

**中文能力** — DeepSeek 原生中文理解、古文、长文摘要更强。GPT-4o 多语言混合场景更稳。

**代码能力** — GPT-4o 综合编程领先，DeepSeek R1 在算法/数学上已反超。

**最终建议**：日常中文用 DeepSeek，写代码用 GPT-4o，深度推理用 DeepSeek R1。
"""},
    {"id":"buying-guide","banner":"🧭","bg":"bg-2","title":"2026 AI 模型选购指南：免费到付费总有一款适合你","date":"2026-05-10","tags":["选购指南","入门"],
     "content":"""
### 快速导航

- 💰 **一毛不拔** → DeepSeek V3 / Gemini Flash
- ⚡ **追求速度** → GPT-4o mini / Claude Haiku
- 🧠 **追求智商** → Claude Sonnet / DeepSeek R1
- 💻 **写代码** → GPT-4o / Claude Sonnet
- 🇨🇳 **中文场景** → DeepSeek V3 / Qwen3

**我的日常配置**：DeepSeek V3（主力）+ Claude Sonnet（编程）+ DeepSeek R1（推理），月费 < $10。
"""},
    {"id":"coding-showdown","banner":"💻","bg":"bg-3","title":"Claude vs DeepSeek vs GPT：编程能力终极横评","date":"2026-05-02","tags":["对比评测","编程"],
     "content":"""
### 5 题实测结论

| 场景 | 推荐 |
|------|------|
| Web 开发 / 全栈 | GPT-4o |
| 算法 / 数据处理 | DeepSeek R1 |
| Bug 修复 / 代码审查 | Claude Sonnet |
| 脚本 / 快速原型 | 三款都行 |

日常用 GPT-4o 最稳妥，DeepSeek R1 + Claude 搭配是王炸组合。
"""},
    {"id":"free-ai-2026","banner":"🆓","bg":"bg-4","title":"2026 免费 AI 工具大全：不花一分钱用上顶级模型","date":"2026-05-17","tags":["免费","选购指南"],
     "content":"""
### 完全免费的顶级模型

| 模型 | 免费方式 | 亮点 |
|------|---------|------|
| DeepSeek V3 | 官网/App | 中文最佳 |
| Gemini 2.5 Flash | AI Studio | 100万上下文 |
| Qwen3-235B | 阿里云百炼 | 国内稳定 |

免费模型的综合能力已不输一年前的付费旗舰。
"""},
    {"id":"chinese-writing","banner":"✍️","bg":"bg-5","title":"Claude vs DeepSeek 中文写作能力实测对比","date":"2026-04-28","tags":["对比评测","中文"],
     "content":"""
### 三类中文写作测试

**营销文案** — DeepSeek 胜。更懂中文消费心理，用词地道。
**学术论文** — Claude 胜。逻辑严谨，引用规范。
**创意故事** — 平手。DeepSeek 有文采，Claude 有内涵。

中文写作首选 DeepSeek，学术用途搭配 Claude。
"""},
    {"id":"speed-test","banner":"⚡","bg":"bg-1","title":"六大 AI 模型响应速度实测：谁最快？","date":"2026-04-20","tags":["性能测试"],
     "content":"""
| 模型 | 首字延迟 | 生成速度 |
|------|---------|---------|
| GPT-4o mini | ~0.3s | 极快 |
| DeepSeek V3 | ~0.4s | 极快 |
| GPT-4o | ~0.8s | 中等 |
| Claude Sonnet | ~1.0s | 中等 |
| DeepSeek R1 | ~2.0s | 较慢（思考型）|

前两名体验无明显差异。R1 是"深度思考"设计使然。
"""},
    {"id":"multimodal-compare","banner":"🎨","bg":"bg-2","title":"多模态 AI 模型横评：图片理解哪家强？","date":"2026-04-15","tags":["对比评测","多模态"],
     "content":"""
| 模型 | 图片理解 | 图表分析 | OCR | 创意生成 |
|------|---------|---------|-----|---------|
| GPT-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Gemini 2.5 Pro | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Claude Sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

GPT-4o 多模态综合最强，Gemini OCR 出色，Claude 图表分析一绝。
"""},
    {"id":"api-cost-guide","banner":"💰","bg":"bg-3","title":"AI API 费用深度解析：每花一块钱谁干最多活？","date":"2026-04-08","tags":["价格","选购指南"],
     "content":"""
### 性价比排行（输出每百万 token 价格）

| 模型 | 输出价(¥) | 性价比 |
|------|----------|--------|
| DeepSeek V3 | 2 | 🏆 王者 |
| GPT-4o mini | 4.3 | 🥈 亚军 |
| Qwen3-235B | 8 | 🥉 季军 |
| DeepSeek R1 | 16 | 合理 |
| Claude Haiku | 28 | 偏贵 |
| Gemini 2.5 Pro | 36 | 偏贵 |
| GPT-4o | 72 | 昂贵 |
| Claude Sonnet | 107 | 最贵 |

DeepSeek V3 性价比碾压。高价模型适合对准确性要求极高的场景。
"""},
]

LEADERBOARD = [
    {"模型":"DeepSeek V3","厂商":"DeepSeek","输入(¥/M)":1,"输出(¥/M)":2,"上下文":"128K","评分":"8.5","适用":"中文写作、日常问答"},
    {"模型":"DeepSeek R1","厂商":"DeepSeek","输入(¥/M)":4,"输出(¥/M)":16,"上下文":"128K","评分":"9.0","适用":"数学推理、学术研究"},
    {"模型":"GPT-4o mini","厂商":"OpenAI","输入(¥/M)":1,"输出(¥/M)":4.3,"上下文":"128K","评分":"8.0","适用":"批量任务、内容审核"},
    {"模型":"GPT-4o","厂商":"OpenAI","输入(¥/M)":18,"输出(¥/M)":72,"上下文":"128K","评分":"9.2","适用":"编程、多模态、全栈"},
    {"模型":"Claude 4 Sonnet","厂商":"Anthropic","输入(¥/M)":21,"输出(¥/M)":107,"上下文":"200K","评分":"9.3","适用":"深度分析、长文档"},
    {"模型":"Claude 4 Haiku","厂商":"Anthropic","输入(¥/M)":5.7,"输出(¥/M)":28,"上下文":"200K","评分":"8.3","适用":"敏感内容、安全优先"},
    {"模型":"Qwen3-235B","厂商":"阿里云","输入(¥/M)":2,"输出(¥/M)":8,"上下文":"128K","评分":"8.6","适用":"企业部署、中文稳定"},
    {"模型":"Gemini 2.5 Pro","厂商":"Google","输入(¥/M)":9,"输出(¥/M)":36,"上下文":"1M","评分":"9.1","适用":"超大上下文、多模态"},
]

# ==================== AI 调用 ====================
def get_client(key=None, base=None):
    kwargs = {"api_key": key or api_key}
    if base or api_base:
        kwargs["base_url"] = base or api_base
    return OpenAI(**kwargs)

def ai_call(system_prompt, user_text, use_model=None):
    client = get_client()
    resp = client.chat.completions.create(
        model=use_model or model,
        messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_text}],
        temperature=0.7,
    )
    return resp.choices[0].message.content

# ==================== 页面导航 ====================
PAGES = ["首页", "工具总览", "模型对比", "排行榜", "免费试用"]

if "page" not in st.session_state:
    st.session_state.page = "首页"

def set_page(p):
    st.session_state.page = p

# ==================== 导航栏 ====================
# Logo（艺术字，放大）
st.markdown("""
<div style="text-align:center;padding:20px 0 18px;">
    <span style="
        font-size:40px; font-weight:800; letter-spacing:-1px;
        background: linear-gradient(135deg, #a78bfa 0%, #818cf8 40%, #6ee7b7 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    ">Nier AI</span>
</div>
""", unsafe_allow_html=True)

# 五个页面按钮 —— 居中单行
st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
c0, c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1, 1, 1, 1, 1, 1.5])
for idx, (col, p) in enumerate(zip([c1, c2, c3, c4, c5], PAGES)):
    with col:
        is_current = st.session_state.page == p
        label = f"● {p}" if is_current else p
        btn_type = "primary" if is_current else "secondary"
        if st.button(label, key=f"nav_{p}", use_container_width=True, type=btn_type):
            set_page(p)
            st.rerun()

st.divider()

# ============================================================
# 首页
# ============================================================
if st.session_state.page == "首页":
    # --- Hero ---
    st.markdown("""
    <div class="hero-section">
        <div class="hero-glow-1"></div>
        <div class="hero-glow-2"></div>
        <div class="hero-content">
            <div class="hero-title">发现最适合你的 <span>AI 模型</span></div>
            <div class="hero-desc">深度评测 · 横向对比 · 免费试用 · 帮你省下每一分冤枉钱</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 搜索框 ---
    _, sc, _ = st.columns([2.5, 3, 2.5])
    with sc:
        search_query = st.text_input("搜索", placeholder="🔍  搜索模型、评测、关键词...", label_visibility="collapsed", key="home_search")

    # --- 精选文章 ---
    st.markdown('<div class="section-title">🔥 精选评测文章</div>', unsafe_allow_html=True)

    # 初始显示 5 篇
    if "articles_shown" not in st.session_state:
        st.session_state.articles_shown = 5

    shown = st.session_state.articles_shown
    visible = ARTICLES[:shown]

    # 每行 5 个
    rows = [visible[i:i+5] for i in range(0, len(visible), 5)]
    for row in rows:
        cols = st.columns(5)
        for j, art in enumerate(row):
            with cols[j]:
                st.markdown(f"""
                <div class="article-card">
                    <div class="card-banner {art['bg']}">{art['banner']}</div>
                    <div class="card-body">
                        <div class="title">{art['title']}</div>
                        <div class="meta">
                            <span>{art['date']}</span>
                            <span class="tag">{art['tags'][0]}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            # 每个卡片后面放 expander
            if j < len(row):
                _art = row[j]
                with cols[j]:
                    with st.expander(f"阅读"):
                        st.markdown(_art["content"])

    # "加载更多" 按钮（滚动替代方案）
    if shown < len(ARTICLES):
        _, bc, _ = st.columns([3, 1, 3])
        with bc:
            if st.button("↓ 加载更多文章", key="load_more", use_container_width=True):
                st.session_state.articles_shown = min(shown + 5, len(ARTICLES))
                st.rerun()

# ============================================================
# 工具总览 分页
# ============================================================
elif st.session_state.page == "工具总览":
    st.markdown("""
    <div class="page-hero">
        <div class="hero-glow-2"></div>
        <div class="page-title">🛠️ 工具总览</div>
        <div class="page-desc">按分类浏览 AI 工具与模型，快速找到你需要的</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    st.info("🚧 工具总览模块正在建设中，后续将按分类收录优质 AI 工具链接。敬请期待。")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 模型对比 分页
# ============================================================
elif st.session_state.page == "模型对比":
    st.markdown("""
    <div class="page-hero">
        <div class="hero-glow-2"></div>
        <div class="page-title">⚔️ 模型对比</div>
        <div class="page-desc">同一个问题发给多个模型，并排对比结果</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    if not api_key:
        st.warning("API Key 未配置，对比功能暂不可用。本地调试请在 .streamlit/secrets.toml 中设置。")

    compare_prompt = st.text_area(
        "输入你的提示词",
        height=120,
        placeholder="例如：用 200 字介绍量子计算的基本原理，让中学生也能听懂。",
        label_visibility="collapsed",
    )

    ca, cb, cc = st.columns(3)
    with ca: ma = st.selectbox("模型 A", ["deepseek-chat","gpt-4o-mini","gpt-4o"], key="ma")
    with cb: mb = st.selectbox("模型 B", ["gpt-4o-mini","deepseek-chat","gpt-4o"], key="mb")
    with cc: mc = st.selectbox("模型 C", ["(不选)","gpt-4o-mini","gpt-4o","deepseek-chat"], key="mc")

    if st.button("⚡ 开始对比", type="primary"):
        if not api_key:
            st.error("API Key 未配置。")
        elif not compare_prompt.strip():
            st.warning("请输入提示词。")
        else:
            models_to_run = [ma, mb]
            if mc != "(不选)": models_to_run.append(mc)
            results = {}
            spinner_cols = st.columns(len(models_to_run))
            for i, m in enumerate(models_to_run):
                with spinner_cols[i]:
                    with st.spinner(f"{m} 思考中..."):
                        try:
                            results[m] = ai_call("直接回答问题，不要添加多余说明。", compare_prompt, use_model=m)
                        except Exception as e:
                            results[m] = f"❌ {e}"
            st.divider()
            st.markdown("### 对比结果")
            rcols = st.columns(len(models_to_run))
            for i, (m, r) in enumerate(results.items()):
                with rcols[i]:
                    st.markdown(f"**{m}**")
                    st.text_area("", value=r, height=280, key=f"cout_{i}", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 排行榜 分页
# ============================================================
elif st.session_state.page == "排行榜":
    st.markdown("""
    <div class="page-hero">
        <div class="hero-glow-2"></div>
        <div class="page-title">📊 排行榜</div>
        <div class="page-desc">主流 AI 模型参数 & 价格一览，数据来自官网公开定价</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        pf = st.multiselect("按厂商筛选", ["DeepSeek","OpenAI","Anthropic","阿里云","Google"], default=[])
    with f2:
        sb = st.selectbox("排序依据", ["评分","输入(¥/M)","模型"])

    data = LEADERBOARD
    if pf: data = [d for d in data if d["厂商"] in pf]
    if sb == "评分": data = sorted(data, key=lambda d: d["评分"], reverse=True)
    elif sb == "输入(¥/M)": data = sorted(data, key=lambda d: d["输入(¥/M)"])
    else: data = sorted(data, key=lambda d: d["模型"])

    st.dataframe(data, use_container_width=True, hide_index=True, height=400)
    st.caption("💡 价格以官方为准，此处仅供参考。数据更新于 2026.05。")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 免费试用 分页
# ============================================================
elif st.session_state.page == "免费试用":
    st.markdown("""
    <div class="page-hero">
        <div class="hero-glow-2"></div>
        <div class="page-title">🆓 免费试用</div>
        <div class="page-desc">选一个模型，输入内容，免费体验 AI 效果</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    if not api_key:
        st.warning("API Key 未配置，试用功能暂不可用。本地调试请在 .streamlit/secrets.toml 中设置。")

    tc1, tc2, tc3 = st.columns([1,1,1])
    with tc1:
        tm = st.selectbox("模型", ["deepseek-chat"], key="tm")
    with tc2:
        tt = st.selectbox("任务", ["文本摘要","翻译","文案改写","自由问答"], key="tt")
    with tc3:
        st.write(""); st.write("")
        btn_try = st.button("🚀 开始试用", type="primary", use_container_width=True)

    if tt == "文本摘要": dp = "请用中文简要总结以下内容，3-5句话："
    elif tt == "翻译": dp = "请将以下内容翻译为英文："
    elif tt == "文案改写": dp = "请将以下文案改写得更加专业简洁："
    else: dp = ""

    ti = st.text_area("输入内容", height=180, placeholder="在此粘贴或输入你的内容...", label_visibility="collapsed")
    sp = st.text_input("系统提示词（可修改）", value=dp, label_visibility="collapsed")

    if btn_try:
        if not api_key: st.error("API Key 未配置。")
        elif not ti.strip(): st.warning("请输入内容。")
        else:
            with st.spinner(f"{tm} 思考中..."):
                try:
                    result = ai_call(sp, ti, use_model=tm)
                    st.success("完成")
                    st.text_area("输出结果", value=result, height=220, label_visibility="collapsed")
                except Exception as e:
                    st.error(f"调用失败：{e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 页脚 ====================
st.divider()
st.markdown(
    '<div style="text-align:center;color:#475569;font-size:12px;padding:16px 0 30px;">'
    '© 2026 Nier AI | 数据来源公开定价 | 评测仅供学习参考'
    '</div>',
    unsafe_allow_html=True,
)

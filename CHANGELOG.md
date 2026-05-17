# Nier AI 版本记录

## v0.0.2 — 2026-05-17

### 新增
- 固定 div 星光背景，页面切换不消失，呼吸动画
- 全局入场动画（fadeInUp / fadeIn / scaleIn），卡片错峰出现
- Hero 圆光呼吸脉动
- 排行榜纯 HTML 表格渲染，彻底消除白底
- 全局 CSS 强制暗底覆盖（input / textarea / select / popover / menu / dataframe）

### 优化
- Nier AI 标题放大至 80px，渐变艺术字
- 导航按钮暗色可见底框
- 搜索框颜色适配暗底
- 模块间距统一
- 全局禁用纯白色

## v0.0.1 — 2026-05-17

### 已实现
- 暗色主题，5 页导航：首页 / 工具总览 / 模型对比 / 排行榜 / 免费试用
- 首页 Hero + Nier AI 艺术字标题 + 搜索框
- 8 篇评测文章，卡片网格，加载更多
- 模型对比：多模型并排输出
- 排行榜：8 款主流模型参数/价格，筛选排序
- 免费试用：选模型 → 选任务 → 看效果
- API Key 通过 secrets.toml 配置，界面不可见
- 访问密码保护（可选）

### 技术栈
- Python + Streamlit + OpenAI SDK
- 域名：nier-ai.com
- 仓库：github.com/zouxt94/nier-ai

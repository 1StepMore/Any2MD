# 全自动化格式降维引擎 - 架构蓝图 V3 (终极工业版)

> **核心理念**：格式工厂分发（质量通道 / 快速通道） + 无损降维表达 + 动态导入防休克 + asyncio 高并发吞吐
> **开发策略**：5% Vibe胶水代码（纯流程编排） + 95% 顶级开源轮子（消灭一切自写解析器与排版逻辑）
> **执行目标**：纯本地 CLI 运行 + 傻瓜式 BAT 拖拽入口，绝对零人工干预，输出标准化 Markdown，绝不覆盖源文件

---

## 一、 需求第一性原理拆解

1. **架构与体验**：**纯 CLI 驱动**。日常使用提供 `.bat` 傻瓜入口（拖拽即走），高级功能暴露完整 CLI 参数。除系统级崩溃（如缺依赖、OOM）外，绝不阻塞，绝不弹窗询问。
2. **格式解耦的终结（双轨降维）**：放弃强依赖单一的“万能解析器”。采用**格式工厂模式**，按需加载：
   - **质量通道**：使用经过工业验证的“直接转 MD”轮子（如 `pypandoc`、`mammoth`、`markdownify`），彻底拒绝用底层 XML 库手搓排版逻辑。
   - **快速通道**：使用 `markitdown` 作为通用 Fallback，追求“能看”而非“完美”。
3. **重度依赖的“动态防休克”**：对于 PDF 等强依赖系统 C 库/大内存的转换器，**禁止在文件头部静态 import**。必须采用动态导入机制，将“环境缺失错误”转化为“静默降级”，保证流水线绝对畅通。
4. **输出确定性红线**：
   - **绝不覆盖**：输出文件自动重命名（如 `report.docx` -> `report.md`，冲突时 `report_1.md`）。
   - **拒绝阻断式 QC**：废弃 AST 级强校验，改为容错率极高的正则清洗，防止因第三方轮子的微小规范差异导致流水线卡死。

---

## 二、 最终工具矩阵（确定性轮子架构）

| 环节 | 工具 (附官网/GitHub) | 唯一职责 | 为什么选它 (V3 升级理由) |
|---|---|---|---|
| **格式嗅探与分发** | **[filetype](https://github.com/h2non/filetype.py)** | 基于文件头魔数精准判断格式 | 纯 Python 实现，跨平台零配置，彻底消灭 Windows 下的 `libmagic` 依赖地狱 |
| **快速转换** | **[markitdown](https://github.com/microsoft/markitdown)** | 任意格式单向降维为 MD | 微软出品，一行代码搞定长尾格式，省去 90% 的胶水代码 |
| **质量转换** | **[pypandoc](https://github.com/JessicaTegner/pypandoc)** | 结构化文档精准转 MD | Pandoc 是文档转换界的真神，原生 AST 转换，0 排版 Bug |
| **质量转换** | **[mammoth](https://github.com/mwilliamson/python-mammoth)** | DOCX 语义化转 MD | 作为 Pandoc 的补充，内置样式映射，对复杂嵌套列表的 MD 降维极其干净 |
| **质量转换 (HTML)** | **[markdownify](https://github.com/matthewwithanm/markdownify)** | 剥离冗余标签转标准 MD | **[替换 BS4手搓]** 久经沙场的专用轮子，一行代码转换，彻底消灭 HTML 标签处理的 if-else 地狱 |
| **质量转换 (PDF)** | **[MarkItDown](https://github.com/microsoft/markitdown)** | 表格 + 布局推理转 MD | 微软出品，开源界 PDF 转 MD 天花板，支持表格识别 |
| **降级转换 (PDF)** | **[pypdfium2](https://github.com/pypdfium2/pypdfium2)** | 纯文本提取转 MD | 不依赖 torch/transformers，MarkItDown 失败后的保底方案 |
| **并发与重试** | **[Tenacity](https://github.com/jd/tenacity)** | I/O 重试防卡死 | 对于处理超大文件的偶发内存波动起缓冲作用 |
| **并发调度** | `asyncio` (内置) + `Semaphore` | 高并发令牌桶控制 | 原生标准库，零依赖实现多文件并行吞吐 |
| **CLI 与胶水** | **[Typer](https://github.com/fastapi/typer)** | 极速构建命令行与 BAT 拖拽入口 | 现代 Python CLI 事实标准 |

---

## 三、 全自动闭环流水线设计

text
[源文件/文件夹] + CLI 参数 (–mode quality/fast –pdf_engine heavy)
│
▼ (前置拦截：文件大小体检)
├─ [校验] 单文件 > 50MB ? ──> 是：直接跳过并输出 Error 日志 (防 OOM)，否：放行
│
▼ (遍历收集所有文件)
[filetype 嗅探真实格式] ──> 进入【格式工厂 dispatcher.py】
│
├─[如果 --mode quality 且有专用轮子]
│  └─ 实例化质量通道 (如 converter_pandoc.py / converter_markdownify.py) ──> 精准转为 MD 字符串
│
├─[如果 --mode fast 或 无专用轮子 (如 .epub)]
│  └─ 走 markitdown 快速通道 ──> 转为 MD 字符串
│
└─[如果是 PDF]
   └─ 根据 --pdf_engine 参数分流 (见 4.1 细节)
======================================================
【后处理与输出阶段】
[阶段 1: 轻量级文本清洗]
├─ 正则清理连续空行、统一换行符为 LF
└─ (拒绝 AST 强校验，保证流水线绝对畅通)

[阶段 2: 确定性文件命名与存储]
├─ 提取源文件名，去除后缀 (如 report.pdf -> report)
├─ 如果是文件夹批量转换
│  └─ 创建 {源文件夹名}_converted/ 子目录，所有输出集中在此
├─ 检查目标目录是否存在 report.md ?
│  ├─ 不存在 ──> 保存为 report.md
│  └─ 已存在 ──> 自动递增，保存为 report_1.md (绝不覆盖任何文件)
└─ 输出成功日志


---

## 四、 关键工程细节（Vibe Coding 必须遵守的规则）

### 4.1 PDF 转换的“动态导入”与“用户决策”机制
`MarkItDown` 和 `pypdfium2` 遵循动态导入机制，严谨在文件头静态 import。
1. **动态导入封装**：在 `converter_pdf.py` 内部，使用 `importlib.import_module('marker')`。捕获 `Exception`，若有报错则打 Warn 日志并切换。
2. **配置二选一**：在 `config.yaml` 中暴露 `pdf_engine: "light" | "heavy"`。
   - `light`：直接走 `markitdown`（其内置基础 PDF 解析），0 外部依赖，保证能跑。
   - `heavy`：`MarkItDown` (表格 + 布局) -> `pypdfium2` (纯文本保底) -> 抛出异常提示。

### 4.2 HTML 转换的零逻辑原则
废弃 `BeautifulSoup4` + 手写提取规则的做法。直接调用 `markdownify.markdownify(html_content, heading_style="ATX")`。它天然处理各种奇葩嵌套 `div`，保证输出 GFM 标准格式。

### 4.3 表格转换的标准化
无论使用 `pypandoc` 还是 `mammoth`，必须在配置或后处理中规定：所有表格必须输出为 **GFM (GitHub Flavored Markdown) 标准格式**（使用 `|` 和 `-`），禁止输出 HTML 的 `<table>` 标签。

---

## 五、 极简工程结构 (Vibe Coding 脚手架)

自研代码被压缩至极致，全都是无状态的纯函数工厂与胶水，Debug 成本趋近于零。

text
any2md-industrial/
├── bat/
│   └── run.bat # 傻瓜入口：拖拽文件/文件夹直接运行
├── config.yaml # 输出模式、PDF引擎策略(light/heavy)、并发度
│
├── wheels/ # 【核心：确定性轮子封装工厂】
│   ├── dispatcher.py # filetype 嗅探后，返回对应的 Converter 实例
│   ├── converters/ # 【格式工厂】
│   │   ├── base_converter.py # 定义统一接口：convert(file_path) -> str(markdown)
│   │   ├── converter_pandoc.py # pypandoc 质量通道 (处理 docx/pptx/xlsx 等)
│   │   ├── converter_mammoth.py# mammoth 质量 (专精复杂 DOCX)
│   │   ├── converter_html.py # markdownify 质量通道 (零手写逻辑)
│   │   ├── converter_pdf.py # 动态 importlib 导入 MarkItDown/pypdfium2，按 config 分流
│   │   └── converter_passthrough.py # .md / .txt 直通
│   ├── fast_lane.py # 封装 markitdown，作为所有未覆盖格式及 PDF(light模式) 的 Fallback
│   └── cleaner.py # 轻量级正则后处理 (替代阻断式 AST 校验)
│
├── pipeline.py # 【唯一需要 Vibe 的胶水】
│   # asyncio.gather 编排并发，包含文件大小 >50MB 拦截逻辑，处理文件名递增防覆盖
├── cli.py # Typer 入口
└── requirements.txt


### 关键依赖安装 (requirements.txt 真工业版)

text
# 格式嗅探
filetype

# 质量通道 (直接产出 MD 的成熟轮子)
pypandoc-binary    # 必须带 -binary，免除用户安装 Pandoc 系统环境的痛苦
mammoth
markdownify        # HTML 转 MD 终极轮子

# 快速通道与 PDF 轻量级
markitdown         # 包含基础 PDF 能力，作为 light 模式兜底

# PDF 高质量通道 (按需)
markitdown[pdf]
pypdfium2
poppler-utils

# 工程基建
tenacity
typer
pyyaml

---

**状态：Any2MD 极简工业蓝图 V3 终极确认完毕。引入动态导入机制彻底斩断重型 C 库依赖引发的系统级崩溃；用成熟轮子 `markdownify` 替换手搓 HTML 解析；明确大文件拦截与 PDF 策略的用户决策权，实现真正的“零干预、零覆盖风险、极低 Debug 成本”的高吞吐格式降维闭环。**

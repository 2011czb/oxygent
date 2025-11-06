# 京东多智能体挑战赛 - Valid 数据集任务分析与 Agent 架构设计

> **文档版本**: v1.0  
> **更新时间**: 2025年  
> **目标**: 为初赛测试集（200条）设计高准确率的多智能体协作系统

---

## 📊 一、Valid 数据集任务分布统计（100条样本）

### 1.1 按难度等级分布

| 难度等级 | 数量 | 占比 | 特征 |
|---------|------|------|------|
| **Level 1（基础）** | 48 | 48% | LLM推理 + 单一工具（数学、搜索、简单文件读取） |
| **Level 2（进阶）** | 37 | 37% | 多工具协同、多步检索、跨平台信息整合 |
| **Level 3（复杂）** | 15 | 15% | 深度规划、多层嵌套推理、复杂多模态分析 |

**关键洞察**：
- **85% 的任务集中在 Level 1-2**，需优先保证基础工具的稳定性与准确性
- Level 3 任务需要特别关注**多步规划能力**与**容错机制**

---

### 1.2 按任务类型分布

#### **类型 A：Web 检索与浏览器操作（占比最高 ~35%）**

| 子类型 | 数量 | 典型示例 | 关键能力 |
|--------|------|----------|----------|
| **京东商品详情页** | 14 | "https://item.jd.com/xxx 商品的品牌名是什么？" | HTML解析、XPath/CSS选择器 |
| **GitHub 仓库查询** | 8 | "在 huggingface/transformers #40054 issue 中用户附加的链接是什么？" | GitHub API、Issue/PR 检索 |
| **京东官网/子站** | 7 | "京东金融提供了哪六个板块？" | 动态网页渲染、结构化提取 |
| **百度百科/维基** | 4 | "故宫博物院馆藏编号【新00117374】的文物名称中包含什么动物？" | 语义搜索、实体链接 |
| **其他网站** | 2 | "PyPI oxygent 包第二早的发布日期？" | API调用、时间解析 |

**工具需求**：
- Playwright/Selenium 浏览器自动化
- BeautifulSoup/lxml HTML 解析
- GitHub API、PyPI API 等专用接口

---

#### **类型 B：多模态内容理解（~18%）**

| 模态类型 | 数量 | 典型示例 | 关键能力 |
|---------|------|----------|----------|
| **图片识别** | 7 | "图中人物是某朝开国宰相，该朝代统治了多少年？" | OCR、人脸识别、历史知识推理 |
| **音频识别** | 4 | "识别歌词中出现的第一个数字，输出个位数和十位数之和" | 语音转文字、歌词解析 |
| **视频分析** | 5 | "舌尖上的中国第4季第2集中介绍哪个食材的根部自带清新香气？" | 视频字幕提取、场景定位 |
| **PDF/PPT 文档** | 2 | "阅读 ppt3.pptx，获取第一张不含英文的页码" | 文档解析、版式分析 |

**工具需求**：
- 多模态 LLM（GPT-4V、Qwen-VL）
- Whisper（音频转文字）
- PyMuPDF/python-pptx（文档解析）
- OCR 工具（PaddleOCR、Tesseract）

---

#### **类型 C：逻辑推理与数学计算（~15%）**

| 子类型 | 数量 | 典型示例 | 关键能力 |
|--------|------|----------|----------|
| **脑筋急转弯/谜题** | 6 | "100桶水混有1桶剧毒，最少需要几只兔子？" | 二进制编码、信息论 |
| **数学计算** | 4 | "金条切成多少段，使得每天能支付当日工资？" | 动态规划、贪心算法 |
| **算法题** | 3 | "完成洛谷 U412534 算法题，给出 output answer" | 代码生成与执行 |
| **Numpy/数据处理** | 2 | "矩阵被'F'规则展平后的结果是[[1,3,2,4]]，原矩阵是什么？" | 矩阵操作常识 |

**工具需求**：
- Python 代码生成与沙箱执行
- SymPy 符号计算
- Numpy/Pandas 数据处理

---

#### **类型 D：代码生成与文件操作（~12%）**

| 子类型 | 数量 | 典型示例 | 关键能力 |
|--------|------|----------|----------|
| **文件读写** | 5 | "在文件目录中，log文件数量" | 文件系统遍历、正则匹配 |
| **Shell 命令** | 4 | "创建目录结构，输出磁盘占用大小（kb）" | Shell 脚本执行、结果解析 |
| **数据集下载与处理** | 3 | "下载 gsm-8k 数据集，读取第30个问题并计算答案" | HuggingFace API、数据处理 |

**工具需求**：
- 文件操作工具（pathlib、os）
- Shell 命令执行（subprocess）
- HuggingFace datasets API

---

#### **类型 E：知识检索与推理链（~20%）**

| 子类型 | 数量 | 典型示例 | 关键能力 |
|--------|------|----------|----------|
| **京东企业信息** | 8 | "京东于某年首次入榜《财富》全球500强，该年百度百科页最早的贡献者叫什么？" | 多步检索、历史追溯 |
| **体育/娱乐** | 6 | "披荆斩棘第5季《记得》舞台上唱第一句歌词的人的出生年份？" | 视频检索 + 人物搜索 |
| **科技文档** | 4 | "Django 5.0.x 稳定版支持的最低 Python 版本是什么？" | GitHub 文档检索 |
| **地理/历史** | 2 | "银杏栽培种出产于苏州某山，关联至江南三大名楼，输出古文前四个字" | 知识图谱推理 |

**工具需求**：
- 百度搜索/Google 搜索 API
- 维基百科/百度百科 API
- B站/YouTube 搜索（视频类）

---

## 🏗️ 二、Agent 架构设计

### 2.1 总体架构图

```
用户查询（来自 test/data.jsonl）
          ↓
┌─────────────────────────────────────────┐
│   Master Agent（ReActAgent）            │
│   - 任务理解与意图识别                    │
│   - 动态规划与路由决策                    │
│   - 结果汇总与格式化                      │
└─────────────────────────────────────────┘
          ↓
   ┌──────┴───────────────────────┐
   ↓                               ↓
[任务分类器 LLM]          [紧急降级路径]
   ↓                          （直接调用通用LLM）
   ├─→ 【Web检索Agent】
   ├─→ 【多模态Agent】
   ├─→ 【推理计算Agent】
   ├─→ 【代码执行Agent】
   └─→ 【知识检索Agent】
          ↓
   [工具调用 & 结果验证]
          ↓
   ┌────────────────┐
   │ 格式化输出模块  │
   │ - 答案清洗      │
   │ - 类型转换      │
   │ - 格式校验      │
   └────────────────┘
          ↓
  {"task_id": "xxx", "answer": "yyy"}
```

---

### 2.2 核心 Agent 设计

#### **Agent 1：Master Agent（总调度）**

**类型**: `oxy.ReActAgent`

**职责**:
1. 解析用户查询，识别任务类型（基于关键词、URL模式、文件扩展名）
2. 动态路由至专用 Sub-Agent
3. 监控执行状态，必要时触发重试或降级
4. 汇总结果并格式化输出

**关键配置**:
```python
oxy.ReActAgent(
    name="master_agent",
    is_master=True,
    sub_agents=[
        "web_retrieval_agent",
        "multimodal_agent", 
        "reasoning_agent",
        "code_exec_agent",
        "knowledge_agent"
    ],
    max_react_rounds=5,  # 最多5轮ReAct循环
    trust_mode=True,     # 开启trust_mode提供元数据
    func_format_output=format_final_answer,  # 答案格式化
    timeout=120
)
```

**路由规则示例**:
```python
def route_to_agent(query: str, file_name: str) -> str:
    # URL检索
    if "https://" in query or "http://" in query:
        if "item.jd.com" in query:
            return "jd_product_agent"
        elif "github.com" in query:
            return "github_agent"
        return "web_retrieval_agent"
    
    # 多模态
    if file_name:
        ext = file_name.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg', 'png']:
            return "image_analysis_agent"
        elif ext in ['mp3', 'wav']:
            return "audio_analysis_agent"
        elif ext in ['mp4', 'avi']:
            return "video_analysis_agent"
        elif ext in ['pdf', 'pptx']:
            return "document_agent"
    
    # 数学/逻辑推理
    if any(kw in query for kw in ["计算", "多少", "最少", "最多", "求", "算"]):
        return "reasoning_agent"
    
    # 代码执行
    if any(kw in query for kw in ["文件目录", "创建", "Shell", "命令"]):
        return "code_exec_agent"
    
    # 默认知识检索
    return "knowledge_agent"
```

---

#### **Agent 2：Web 检索 Agent（浏览器操作）**

**类型**: `oxy.WorkflowAgent`（自定义工作流）

**职责**:
1. 京东商品页解析（价格、品牌、评论区）
2. GitHub Issue/PR/Commit 查询
3. 百度百科/维基百科结构化提取

**工具组合**:
```python
oxy.WorkflowAgent(
    name="web_retrieval_agent",
    desc="专门处理网页检索与浏览器自动化任务",
    tools=[
        "browser_tool",      # Playwright 浏览器工具
        "jd_api_tool",       # 京东商品API（如果可用）
        "github_api_tool",   # GitHub GraphQL API
        "baidu_search_tool"  # 百度搜索工具
    ],
    func_workflow=web_retrieval_workflow,
    timeout=60
)
```

**工作流伪代码**:
```python
async def web_retrieval_workflow(oxy_request):
    query = oxy_request.get_query()
    
    # Step 1: URL识别
    if "item.jd.com" in query:
        # 提取商品ID
        product_id = extract_product_id(query)
        # 调用浏览器工具
        page_html = await oxy_request.call(
            callee="browser_tool",
            arguments={"url": f"https://item.jd.com/{product_id}.html"}
        )
        # 解析HTML
        answer = parse_jd_product_page(page_html.output, query)
        return answer
    
    elif "github.com" in query:
        # 提取仓库/Issue编号
        repo, issue_num = extract_github_info(query)
        # 调用 GitHub API
        issue_data = await oxy_request.call(
            callee="github_api_tool",
            arguments={"repo": repo, "issue": issue_num}
        )
        answer = extract_answer_from_issue(issue_data.output, query)
        return answer
    
    # ... 其他逻辑
```

**关键工具实现**:

##### **工具 2.1: browser_tool（Playwright封装）**
```python
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("browser_tool")

@mcp.tool(description="访问URL并返回页面HTML或截图")
async def fetch_page(
    url: str = Field(description="目标URL"),
    wait_for: str = Field(default="", description="等待的CSS选择器"),
    screenshot: bool = Field(default=False, description="是否返回截图")
):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        
        if wait_for:
            await page.wait_for_selector(wait_for, timeout=10000)
        
        if screenshot:
            img_bytes = await page.screenshot()
            await browser.close()
            return {"type": "image", "data": img_bytes}
        else:
            html = await page.content()
            await browser.close()
            return {"type": "html", "data": html}
```

##### **工具 2.2: github_api_tool**
```python
@mcp.tool(description="查询 GitHub Issue/PR 信息")
async def query_github_issue(
    repo: str = Field(description="仓库全名，如 'huggingface/transformers'"),
    issue_number: int = Field(description="Issue 编号")
):
    import httpx
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"Accept": "application/vnd.github+json"})
        return resp.json()
```

---

#### **Agent 3：多模态 Agent（图片/音频/视频）**

**类型**: `oxy.ParallelAgent`（并行处理多模态）

**职责**:
1. 图片 OCR/场景识别
2. 音频转文字 + 歌词分析
3. 视频关键帧提取 + 字幕识别

**工具组合**:
```python
oxy.ParallelAgent(
    name="multimodal_agent",
    desc="处理图片、音频、视频、PDF等多模态任务",
    permitted_tool_name_list=[
        "image_ocr_tool",        # PaddleOCR/Tesseract
        "image_vqa_tool",        # GPT-4V/Qwen-VL 视觉问答
        "audio_transcribe_tool", # Whisper 语音转文字
        "video_extract_tool",    # ffmpeg 提取关键帧/字幕
        "pdf_parser_tool"        # PyMuPDF
    ]
)
```

**关键工具实现**:

##### **工具 3.1: image_vqa_tool（多模态LLM）**
```python
@mcp.tool(description="对图片进行视觉问答")
async def image_vqa(
    image_path: str = Field(description="图片路径"),
    question: str = Field(description="关于图片的问题")
):
    # 使用 GPT-4V 或 Qwen-VL
    import base64
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # 调用多模态LLM
    response = await llm_client.chat(
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }]
    )
    return response.choices[0].message.content
```

##### **工具 3.2: audio_transcribe_tool（Whisper）**
```python
@mcp.tool(description="音频转文字")
async def transcribe_audio(audio_path: str):
    import whisper
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path, language="zh")
    return result["text"]
```

---

#### **Agent 4：推理计算 Agent（逻辑 + 数学）**

**类型**: `oxy.ReActAgent`

**职责**:
1. 纯数学计算（加减乘除、矩阵运算）
2. 逻辑推理题（脑筋急转弯、谜题）
3. 算法题代码生成与执行

**工具组合**:
```python
oxy.ReActAgent(
    name="reasoning_agent",
    desc="处理数学计算、逻辑推理、算法题",
    tools=[
        "python_math_tool",  # SymPy/Numpy 计算
        "code_sandbox_tool", # 沙箱执行Python代码
        "llm_reasoning_tool" # LLM深度推理
    ],
    max_react_rounds=3
)
```

**关键工具实现**:

##### **工具 4.1: code_sandbox_tool（安全代码执行）**
```python
@mcp.tool(description="在沙箱中执行Python代码")
async def execute_python(code: str = Field(description="要执行的Python代码")):
    import subprocess
    import tempfile
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    # 执行（限制资源）
    try:
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else result.stderr
    finally:
        os.remove(temp_file)
```

---

#### **Agent 5：代码执行 Agent（文件/Shell）**

**类型**: `oxy.WorkflowAgent`

**职责**:
1. 文件读写、目录遍历
2. Shell 命令执行
3. 数据集下载与处理

**工具组合**:
```python
oxy.WorkflowAgent(
    name="code_exec_agent",
    desc="处理文件操作、Shell命令、系统级任务",
    tools=[
        "file_tools",       # OxyGent 内置文件工具
        "shell_tools",      # OxyGent 内置Shell工具
        "hf_dataset_tool"   # HuggingFace 数据集下载
    ],
    func_workflow=code_exec_workflow
)
```

---

#### **Agent 6：知识检索 Agent（搜索引擎）**

**类型**: `oxy.ReActAgent`

**职责**:
1. 百度/Google 搜索
2. 维基百科/百度百科查询
3. 实体链接与知识推理

**工具组合**:
```python
oxy.ReActAgent(
    name="knowledge_agent",
    desc="处理需要外部知识库查询的任务",
    tools=[
        "baidu_search_tool",
        "wikipedia_tool",
        "entity_linker_tool"  # 实体消歧
    ]
)
```

---

### 2.3 专用子 Agent（针对高频场景）

#### **Agent 6.1：京东商品 Agent**
```python
oxy.WorkflowAgent(
    name="jd_product_agent",
    desc="专门解析京东商品详情页",
    tools=["browser_tool", "html_parser_tool"],
    func_workflow=jd_product_workflow
)

async def jd_product_workflow(oxy_request):
    query = oxy_request.get_query()
    product_url = extract_url(query)
    
    # 获取页面HTML
    html = await oxy_request.call("browser_tool", {"url": product_url})
    
    # 根据问题类型解析
    if "品牌" in query:
        return extract_brand(html.output)
    elif "问大家" in query:
        return extract_qa_section(html.output, query)
    # ...
```

#### **Agent 6.2：GitHub Agent**
```python
oxy.WorkflowAgent(
    name="github_agent",
    desc="专门查询 GitHub 仓库/Issue/PR",
    tools=["github_api_tool", "browser_tool"]
)
```

---

## 🛠️ 三、工具清单与实现优先级

### 3.1 核心工具（必须实现）

| 工具名称 | 功能 | 技术栈 | 优先级 |
|---------|------|--------|--------|
| **browser_tool** | 浏览器自动化 | Playwright | ⭐⭐⭐⭐⭐ |
| **html_parser_tool** | HTML结构化提取 | BeautifulSoup4 | ⭐⭐⭐⭐⭐ |
| **image_vqa_tool** | 图片视觉问答 | GPT-4V/Qwen-VL | ⭐⭐⭐⭐⭐ |
| **python_exec_tool** | Python代码沙箱 | subprocess | ⭐⭐⭐⭐⭐ |
| **file_tools** | 文件读写 | pathlib/os | ⭐⭐⭐⭐ |
| **baidu_search_tool** | 百度搜索 | requests + 解析 | ⭐⭐⭐⭐ |

### 3.2 增强工具（提升准确率）

| 工具名称 | 功能 | 技术栈 | 优先级 |
|---------|------|--------|--------|
| **github_api_tool** | GitHub API查询 | GraphQL | ⭐⭐⭐⭐ |
| **audio_transcribe** | 音频转文字 | Whisper | ⭐⭐⭐ |
| **video_extract** | 视频关键帧提取 | ffmpeg | ⭐⭐⭐ |
| **pdf_parser** | PDF解析 | PyMuPDF | ⭐⭐⭐ |
| **ocr_tool** | OCR识别 | PaddleOCR | ⭐⭐⭐ |

### 3.3 优化工具（锦上添花）

| 工具名称 | 功能 | 技术栈 | 优先级 |
|---------|------|--------|--------|
| **cache_tool** | 结果缓存 | Redis/本地 | ⭐⭐ |
| **retry_tool** | 智能重试 | tenacity | ⭐⭐ |
| **validator_tool** | 答案格式验证 | pydantic | ⭐⭐ |

---

## 📝 四、关键挑战与解决方案

### 4.1 挑战 1：京东商品页动态加载

**问题**: 部分内容通过 JavaScript 异步加载，直接请求HTML无法获取

**解决方案**:
1. **方案A（推荐）**: 使用 Playwright 等待关键元素加载
   ```python
   await page.goto(url)
   await page.wait_for_selector('.p-name')  # 等待商品名称加载
   html = await page.content()
   ```

2. **方案B**: 直接调用京东API（如果能逆向）
   ```python
   # 示例：商品详情API
   api_url = f"https://api.m.jd.com/client.action?functionId=getProductDetail&body={{\"skuId\":\"{product_id}\"}}"
   ```

---

### 4.2 挑战 2：视频内容定位（时间戳级精度）

**问题**: "舌尖上的中国第X集第X分钟"需要精准定位

**解决方案**:
1. **字幕文件提取**（优先）
   ```python
   import ffmpeg
   ffmpeg.input('video.mp4').output('subtitle.srt', vcodec='copy', scodec='srt').run()
   ```

2. **关键帧OCR**（备选）
   ```python
   # 每10秒提取一帧，OCR识别字幕
   for t in range(0, duration, 10):
       frame = extract_frame(video_path, timestamp=t)
       text = ocr_tool(frame)
   ```

---

### 4.3 挑战 3：多步推理的错误累积

**问题**: 如"京东首次入榜500强的年份 → 该年百度百科 → 最早贡献者 → 贡献者编辑的词条"

**解决方案**:
1. **增强 Prompt**：明确要求分步输出中间结果
   ```
   请分步骤回答：
   1. 首先找到京东首次入榜《财富》500强的年份
   2. 然后访问该年份的百度百科页面
   3. 查找最早的贡献者...
   ```

2. **引入验证节点**：每一步调用 LLM 验证结果合理性
   ```python
   year = await get_jd_500_year()
   # 验证：年份应在 2000-2025 之间
   if not (2000 <= int(year) <= 2025):
       raise ValueError("年份异常")
   ```

---

### 4.4 挑战 4：答案格式标准化

**问题**: 题目要求"仅输出数字""不包含空格""格式如XX市"

**解决方案**: 统一格式化模块
```python
def format_final_answer(answer: str, query: str) -> str:
    # 规则1：去除首尾空格
    answer = answer.strip()
    
    # 规则2：数字提取
    if "仅输出数字" in query or "输出数值" in query:
        nums = re.findall(r'-?\d+\.?\d*', answer)
        answer = nums[0] if nums else answer
    
    # 规则3：日期格式
    if "回答格式" in query and "年" in query:
        # 2025-08-14 → 2025年8月14日
        answer = standardize_date(answer)
    
    # 规则4：去除标点
    if "不包含标点" in query or "去除标点" in query:
        answer = re.sub(r'[^\w\s]', '', answer)
    
    return answer
```

---

## 🚀 五、实施路线图

### 阶段 1：基础设施搭建（2天）
- [x] 创建 OxyGent 项目结构
- [ ] 实现 browser_tool（Playwright）
- [ ] 实现 html_parser_tool
- [ ] 实现 python_exec_tool
- [ ] 配置 LLM（GPT-4/Qwen）

### 阶段 2：核心 Agent 开发（3天）
- [ ] Master Agent 路由逻辑
- [ ] Web Retrieval Agent + 京东/GitHub 专用workflow
- [ ] Multimodal Agent（图片优先）
- [ ] Reasoning Agent + 代码沙箱

### 阶段 3：Valid 数据集调试（3天）
- [ ] 逐条跑 Valid 数据（100条）
- [ ] 统计各类任务准确率
- [ ] 针对低准确率类别优化工具
- [ ] 引入错误重试机制

### 阶段 4：Test 数据集生产（2天）
- [ ] 批量处理 Test 数据（200条）
- [ ] 生成 result.jsonl
- [ ] 数据脱敏（desensitize_data.py）
- [ ] 提交评测

---

## 📊 六、预期性能指标

基于 Valid 数据分析，各类任务的目标准确率：

| 任务类型 | 难度 | 预期准确率 | 关键瓶颈 |
|---------|------|-----------|---------|
| 京东商品页解析 | L1-L2 | 95%+ | 动态加载、反爬虫 |
| GitHub 查询 | L1-L2 | 90%+ | API限流、Issue数量多 |
| 图片OCR/识别 | L2-L3 | 85%+ | 低质量图片、复杂场景 |
| 视频内容定位 | L3 | 75%+ | 字幕缺失、时间戳定位 |
| 逻辑推理题 | L1-L2 | 80%+ | LLM推理能力 |
| 多步知识推理 | L3 | 70%+ | 错误累积 |

**整体目标准确率**: **85%+（85/100）**

---

## 🔧 七、配置示例

### 7.1 完整 oxy_space 配置

```python
import os
from oxygent import MAS, Config, oxy, preset_tools

Config.set_agent_llm_model("default_llm")
Config.set_app_name("jd_multi_agent_challenge")

oxy_space = [
    # ===== LLM =====
    oxy.HttpLLM(
        name="default_llm",
        api_key=os.getenv("DEFAULT_LLM_API_KEY"),
        base_url=os.getenv("DEFAULT_LLM_BASE_URL"),
        model_name=os.getenv("DEFAULT_LLM_MODEL_NAME"),
        llm_params={"temperature": 0.1},  # 降低随机性
        semaphore=10  # 并发控制
    ),
    
    # ===== 多模态LLM（GPT-4V）=====
    oxy.HttpLLM(
        name="vision_llm",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
        model_name="gpt-4-vision-preview",
        is_multimodal_supported=True
    ),
    
    # ===== 工具 =====
    # 浏览器工具（自定义MCP）
    oxy.StdioMCPClient(
        name="browser_tool",
        params={
            "command": "uv",
            "args": ["--directory", "./mcp_servers", "run", "browser_tool.py"]
        }
    ),
    
    # 文件工具（OxyGent内置）
    preset_tools.file_tools,
    preset_tools.python_tools,
    preset_tools.shell_tools,
    
    # GitHub API工具（自定义）
    oxy.StdioMCPClient(
        name="github_tool",
        params={
            "command": "uv",
            "args": ["--directory", "./mcp_servers", "run", "github_tool.py"]
        }
    ),
    
    # ===== Sub-Agents =====
    # 京东商品Agent
    oxy.WorkflowAgent(
        name="jd_product_agent",
        desc="专门解析京东商品详情页",
        tools=["browser_tool"],
        func_workflow=jd_product_workflow
    ),
    
    # GitHub Agent
    oxy.WorkflowAgent(
        name="github_agent",
        desc="查询 GitHub 仓库/Issue/PR",
        tools=["github_tool", "browser_tool"],
        func_workflow=github_workflow
    ),
    
    # 图片分析Agent
    oxy.ReActAgent(
        name="image_agent",
        desc="处理图片OCR、视觉问答",
        tools=["vision_llm"],  # 直接调用多模态LLM
        llm_model="vision_llm"
    ),
    
    # 推理计算Agent
    oxy.ReActAgent(
        name="reasoning_agent",
        desc="处理数学计算、逻辑推理",
        tools=["python_tools"],
        llm_model="default_llm"
    ),
    
    # ===== Master Agent =====
    oxy.ReActAgent(
        name="master_agent",
        is_master=True,
        sub_agents=[
            "jd_product_agent",
            "github_agent",
            "image_agent",
            "reasoning_agent"
        ],
        tools=["browser_tool", "file_tools"],  # 通用工具
        max_react_rounds=5,
        trust_mode=True,
        func_format_output=format_final_answer,
        timeout=120
    )
]
```

---

## 📚 八、参考资源

### 8.1 OxyGent 文档
- 中文指南：`OxyGent/docs/docs_zh/readme.md`
- Workflow 示例：`OxyGent/examples/agents/`
- MCP 工具开发：`OxyGent/docs/docs_zh/2_4_use_mcp_tools.md`

### 8.2 外部工具
- Playwright 文档：https://playwright.dev/python/
- Whisper：https://github.com/openai/whisper
- PyMuPDF：https://pymupdf.readthedocs.io/
- GitHub API：https://docs.github.com/en/graphql

---

## ✅ 总结

本文档完成了：
1. **Valid 数据集的深度分析**（100条样本，5大类任务）
2. **Agent 架构设计**（1个 Master + 5个专用 Sub-Agent）
3. **工具清单与优先级**（15+核心工具）
4. **关键挑战的解决方案**（动态加载、多步推理、格式标准化）
5. **实施路线图**（4阶段10天）

**下一步行动**：
1. 根据本文档搭建基础框架
2. 优先实现 browser_tool 和 jd_product_agent（覆盖35%任务）
3. 在 Valid 数据集上迭代优化，目标准确率 85%+
4. 迁移至 Test 数据集批量生产

---

**文档维护者**: AI Assistant  
**最后更新**: 2025年


# 🤝 多 Agent 协作系统

> 基于 **研究员-写手-评审员** 三角色协作的文章生成系统，通过 Agent 间消息传递和评审反馈循环，自动完成从资料搜集到质量把关的完整内容生产流程。

## ✨ 功能特性

### 👥 三角色协作
- **🔍 研究员 (Researcher)**: 网络搜索、资料整理、事实核查
- **✍️ 写手 (Writer)**: 基于研究笔记撰写完整文章
- **🔎 评审员 (Reviewer)**: 多维度质量评审，给出评分和修改建议

### 🔄 评审反馈循环
- 文章自动进入评审流程
- 未通过时返回写手修改
- 最多 N 轮修改（可配置）
- 评分 >= 阈值自动通过

### 📊 多维度评审
- 内容质量 (30%): 事实准确性、信息完整性
- 结构逻辑 (25%): 结构完整性、论证逻辑
- 语言表达 (20%): 流畅度、用词准确性
- 原创性 (15%): 观点独特性、分析深度
- 规范性 (10%): 格式规范、引用标注

### 📝 完整执行轨迹
- 每个 Agent 的消息历史可追溯
- 每轮评审的评分和建议完整记录
- 文章修改前后的版本对比

## 🏗️ 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                     Orchestrator 编排器                    │
│                                                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ 研究员    │───▶│  写手    │───▶│  评审员  │          │
│  │Researcher│    │ Writer   │    │ Reviewer │          │
│  └──────────┘    └──────────┘    └────┬─────┘          │
│       ▲                                  │                │
│       │                                  │ 未通过          │
│       └─────────────反馈修改────────────┘                │
│                          通过                              │
│                          ▼                                 │
│                    最终文章输出                             │
└──────────────────────────────────────────────────────────┘
```

### 消息流

```
Orchestrator → Researcher: 研究主题
Researcher → Orchestrator: 研究笔记
Orchestrator → Writer: 研究笔记 + 写作要求
Writer → Orchestrator: 初稿
Orchestrator → Reviewer: 初稿
Reviewer → Orchestrator: 评审结果（评分+建议）
  ├─ 通过 → 输出最终文章
  └─ 未通过 → Orchestrator → Writer: 评审反馈
                  Writer → Orchestrator: 修改稿（循环）
```

## 📦 安装

```bash
git clone <repo-url>
cd multi-agent-collaboration

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
```

## 🚀 使用方法

### 运行一次协作

```bash
python main.py run "人工智能在医疗领域的应用与挑战"
```

### 指定输出文件

```bash
python main.py run "量子计算的原理与应用" -o output/article.md
```

### 交互式模式

```bash
python main.py interactive
```

### 运行演示

```bash
python main.py demo
```

### 代码中使用

```python
from src import Orchestrator

orchestrator = Orchestrator(
    max_review_rounds=3,
    pass_threshold=7,
    verbose=True,
)

result = orchestrator.run("大语言模型的发展历程与未来趋势")

print(f"最终文章:\n{result.final_output}")
print(f"评审轮次: {result.review_rounds}")
print(f"总耗时: {result.total_time:.1f}秒")
print(f"是否通过: {result.success}")

# 查看每个任务的结果
for task in result.tasks:
    print(f"{task.agent_name}: {task.status.value} (评分: {task.score})")
```

## 📁 项目结构

```
multi-agent-collaboration/
├── main.py                 # 主程序入口
├── config.py               # 配置管理
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── src/
    ├── __init__.py
    ├── agent_base.py       # Agent 基类（消息传递、LLM 调用）
    ├── task.py             # 任务与结果数据结构
    ├── orchestrator.py     # 协作编排器（流程控制、评审循环）
    └── agents/
        ├── __init__.py
        ├── researcher.py   # 研究员 Agent
        ├── writer.py       # 写手 Agent
        └── reviewer.py     # 评审员 Agent
```

## 🎯 核心亮点

1. **纯手写多 Agent 框架**: 不依赖 CrewAI/AutoGen，自主实现 Agent 基类、消息传递、协作编排，展示对多 Agent 系统核心机制的深度理解
2. **角色专业化**: 每个 Agent 有独立的系统提示词、职责定义和工作方法
3. **评审反馈闭环**: Reviewer → Writer → Reviewer 的迭代优化循环，模拟真实内容生产流程
4. **可配置的质量门槛**: 通过分数阈值和最大轮次控制协作质量和效率
5. **完整的可观测性**: 所有消息、任务结果、评审分数都被记录，便于调试和分析

## 🤝 扩展方向

- [ ] 增加更多角色（编辑、校对、事实核查员）
- [ ] 支持并行研究（多个研究员同时搜索不同角度）
- [ ] 集成 RAG 模块，基于知识库进行研究
- [ ] 添加人类反馈环节（Human-in-the-loop）
- [ ] 支持自定义 Agent 角色和协作流程
- [ ] 添加 Agent 间的协商和辩论机制
- [ ] 集成 LangGraph 实现更复杂的状态机

## 📄 License

MIT

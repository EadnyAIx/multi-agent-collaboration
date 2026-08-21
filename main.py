"""多 Agent 协作系统 - 主程序入口。

使用方式:
    python main.py run "主题"          # 运行一次协作
    python main.py interactive          # 交互式模式
    python main.py demo                 # 运行演示
"""

import argparse
import sys
from pathlib import Path

from config import Config
from src import Orchestrator


def run_collaboration(topic: str, output_file: str = None):
    """运行一次协作流程。"""
    orchestrator = Orchestrator(verbose=True)
    result = orchestrator.run(topic)

    # 输出最终文章
    print(f"\n\n{'='*60}")
    print(f"📄 最终文章")
    print(f"{'='*60}")
    print(result.final_output)

    # 保存到文件
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(result.final_output, encoding="utf-8")
        print(f"\n💾 文章已保存到: {output_file}")

    return result


def interactive_mode():
    """交互式模式。"""
    print("=" * 60)
    print("🤝 多 Agent 协作系统 - 交互式模式")
    print(f"模型: {Config.AGENT_MODEL}")
    print(f"最大评审轮次: {Config.MAX_REVIEW_ROUNDS}")
    print(f"通过阈值: {Config.REVIEW_PASS_THRESHOLD}/10")
    print("输入 'quit' 退出")
    print("=" * 60)

    while True:
        try:
            topic = input("\n📝 请输入研究/写作主题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not topic:
            continue
        if topic.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        run_collaboration(topic)


def demo():
    """运行演示。"""
    demo_topics = [
        "人工智能在医疗领域的应用与挑战",
    ]
    for topic in demo_topics:
        run_collaboration(topic, output_file=f"output/{topic[:20]}.md")


def main():
    parser = argparse.ArgumentParser(description="多 Agent 协作系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    run_parser = subparsers.add_parser("run", help="运行一次协作")
    run_parser.add_argument("topic", help="研究/写作主题")
    run_parser.add_argument("-o", "--output", help="输出文件路径", default=None)

    subparsers.add_parser("interactive", help="交互式模式")
    subparsers.add_parser("demo", help="运行演示")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        run_collaboration(args.topic, args.output)
    elif args.command == "interactive":
        interactive_mode()
    elif args.command == "demo":
        demo()


if __name__ == "__main__":
    main()

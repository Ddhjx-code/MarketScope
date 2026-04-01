import argparse
import sys
from src.analyzer import IndustryAnalyzer
from config import Config


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="MarketScope - AI 驱动的行业分析工具"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="社交类APP，主要功能是兴趣小组聊天",
        help="APP 类型描述，例如：'电商类APP，主要功能是二手商品交易'"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="列出所有可用的工具"
    )
    args = parser.parse_args()

    # 验证配置
    Config.validate()

    # 列出工具
    if args.list_tools:
        from src.agent.tools.registry import ToolRegistry
        registry = ToolRegistry()
        print("可用工具：")
        for tool in registry.get_all_tools():
            print(f"  - {tool.name}: {tool.description}")
        return

    # 创建分析器实例
    analyzer = IndustryAnalyzer()

    # 执行分析
    print(f"正在分析: {args.input}")
    print("-" * 50)
    result = analyzer.analyze(args.input)

    print("分析结果:")
    print(result)


if __name__ == "__main__":
    main()

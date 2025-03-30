from mcp import FastMCP
from llm_integration import DeepSeekIntegration
from safe_exec import SafeCodeExecutor
from config import settings
import logging
import pandas as pd

logger = logging.getLogger(__name__)

mcp = FastMCP("Excel Processor")

# 初始化各组件
deepseek = DeepSeekIntegration()
executor = SafeCodeExecutor()


@mcp.tool()
def process_excel_data(excel_path: str, instruction: str) -> str:
    """
    处理Excel数据：
    1. 生成Pandas处理代码
    2. 安全执行代码
    3. 返回处理结果
    """
    try:
        # 生成代码
        generated_code = deepseek.generate_pandas_code(instruction, excel_path)
        if not generated_code:
            return "代码生成失败，请检查指令格式"

        # 执行代码
        success, result = executor.safe_execute(generated_code, excel_path)

        if not success:
            return f"执行失败: {result}"

        # 处理不同结果类型
        if isinstance(result, pd.DataFrame):
            return result.to_markdown()
        elif isinstance(result, pd.Series):
            return result.to_frame().to_markdown()
        elif isinstance(result, (str, int, float)):
            return str(result)
        else:
            return "处理成功，但返回类型不支持直接显示"

    except Exception as e:
        logger.error(f"处理异常: {str(e)}")
        return f"服务器内部错误: {str(e)}"


if __name__ == "__main__":
    mcp.run()

import sys
import uuid
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import get_request_id

# 移除所有默认格式
logger.remove()

# 设置日志输出格式
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "  # 绿色显示日志时间（精确到毫秒）
    "<level>{level: <8}</level> | "  # 按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取）
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "  # 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)

# inject_request_id注入请求id函数在每一个输出日志之前被调用
def inject_request_id(record):
    """
    Loguru 日志补丁函数：为日志记录对象注入 request_id（请求唯一标识）
    保证每条日志都能关联到对应的请求，便于问题排查和请求链路追踪
    Args:
        record: Loguru 的日志记录对象，包含日志的所有上下文信息（如时间、级别、extra 等）
    """
    # 尝试从上下文变量中获取当前请求的 request_id
    # 上下文变量适配异步/多请求场景，可保证不同请求的 request_id 互不干扰
    request_id = get_request_id()

    if request_id == 'None':
        # 若获取失败（如上下文变量未初始化、无有效值等异常），生成 UUID4 作为兜底的唯一标识
        # 避免因 request_id 获取失败导致日志记录异常
        request_id = uuid.uuid4()

    # 将 request_id 存入日志记录的 extra 字段，供日志格式中 {extra[request_id]} 调用
    record["extra"]["request_id"] = request_id

# 给日志打补丁
logger = logger.patch(inject_request_id)

if app_config.logging.console.enable:
    # 添加控制台日志输出
    logger.add(
        sink=sys.stdout,# 控制台输出日志
        level=app_config.logging.console.level, # 日志输出级别
        format=log_format # 日志格式
    )


# 日志文件路径
log_path = Path(__file__).parents[2] / 'logs/app.log'

if app_config.logging.file.enable:
    # 添加文件日志输出
    logger.add(
        sink=log_path,
        level=app_config.logging.file.level,
        format=log_format,
        rotation=app_config.logging.file.rotation, # 日志文件大小
        retention=app_config.logging.file.retention, # 日志文件有效期
        encoding="utf-8"
    )


if __name__ == '__main__':
    # 日志输出有默认格式
    # 2026-10-27 15:50:13.937 | DEBUG    | __main__:<module>:4 - 调试输出信息
    logger.debug('调试输出信息')
    logger.info('正常输出信息')
    logger.warning('警告输出信息')
    logger.error('错误输出信息')
    logger.critical('严重错误信息')

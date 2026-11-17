from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


# 节点：校验SQL
async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"校验SQL"})

    sql = state['sql']
    dw_mysql_repo = runtime.context['dw_mysql_repo']

    try:
        # 校验SQL语句语法是否正确
        await dw_mysql_repo.to_validate_sql(sql)
        logger.info(f'校验SQL成功：{sql}')
        return {"error": None} # 校验通过
    except Exception as e:
        logger.info(f'校验SQL失败：{str(e)}')
        return {"error": f'SQL语法错误：{str(e)}'} # 校验失败

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


# 节点：执行SQL
async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"执行SQL"})

    try:
        sql = state['sql']
        dw_mysql_repo = runtime.context['dw_mysql_repo']

        result = await dw_mysql_repo.to_execute_sql(sql)

        logger.info(f'执行SQL成功：{result}')

        runtime.stream_writer({"result": result})

    except Exception as e:
        logger.info(f'执行SQL失败：{str(e)}')
        runtime.stream_writer({"error": str(e)})
        raise

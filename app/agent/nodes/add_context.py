from datetime import datetime

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.core.log import logger


# 节点：添加额外信息
async def add_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"添加额外信息"})

    dw_mysql_repo = runtime.context['dw_mysql_repo']

    today = datetime.today()
    # today = 2026-10-31 14:10:55.345222
    date = today.strftime("%Y-%m-%d") # 2026-10-31
    # quarter = f'Q{(today.month-1)//3 + 1}' # Q1-Q4
    quarter = f'Q{ (today.month+2)//3}' # Q1-Q4

    # 日期信息
    date_info = DateInfoState(
        date=date,
        quarter=quarter
    )

    # 数据库信息：{dialect: 'mysql', version: '8.0.46'}
    db_info_dict: dict[str,str] = await dw_mysql_repo.get_db_info()

    db_info = DBInfoState(**db_info_dict)

    logger.info(f'添加额外信息：{date_info}--{db_info}')

    return {"date_info": date_info, "db_info": db_info}



if __name__ == '__main__':
    # 1970.1.1 - 2026.10.31
    start = datetime(1970,1,1)
    end = datetime(2026,10,31)
    delta = end - start
    print(f'总天数：{delta.days}')
    print( delta.days % 5 ) # 0 4 晒网   1 2 3打鱼

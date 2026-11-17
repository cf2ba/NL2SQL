import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


# 节点：生成SQL
async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"生成SQL"})

    query = state['query']
    table_infos = state['table_infos']
    metric_infos = state['metric_infos']
    date_info = state['date_info']
    db_info = state['db_info']

    # 提示词
    prompt = PromptTemplate(
        template=load_prompt('generate_sql'),
        input_variables=['query', 'table_infos', 'metric_infos', 'date_info', 'db_info']
    )

    # 解析器
    output_parser = StrOutputParser()

    # 构建处理链
    chain = prompt | llm | output_parser

    # 执行链
    sql = await chain.ainvoke({
        "query": query,
        "table_infos": yaml.dump(  # 将python对象转成yaml字符串
            table_infos,
            allow_unicode=True,  # 保留中文
            sort_keys=False,  # 不对字典的key进行排序
        ),
        "metric_infos": yaml.dump(  # 将python对象转成yaml字符串
            metric_infos,
            allow_unicode=True,  # 保留中文
            sort_keys=False,  # 不对字典的key进行排序
        ),
        "date_info": yaml.dump(  # 将python对象转成yaml字符串
            date_info,
            allow_unicode=True,  # 保留中文
            sort_keys=False,  # 不对字典的key进行排序
        ),
        "db_info": yaml.dump(  # 将python对象转成yaml字符串
            db_info,
            allow_unicode=True,  # 保留中文
            sort_keys=False,  # 不对字典的key进行排序
        )
    })

    logger.info(f'生成SQL：{sql}')


    return {"sql": sql}
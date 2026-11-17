import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


# 节点：过滤表信息
async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"过滤表信息"})

    query = state["query"]
    table_infos = state["table_infos"]

    # 提示词
    prompt = PromptTemplate(
        template=load_prompt('filter_table_info'),
        input_variables=['query','table_infos'],
    )

    # 解析器
    output_parser = JsonOutputParser()

    # 构建处理链
    chain = prompt | llm | output_parser

    # 执行链
    results = await chain.ainvoke({
        "query": query,
        "table_infos": yaml.dump( # 将python对象转成yaml字符串
            table_infos,
            allow_unicode=True, # 保留中文
            sort_keys=False, # 不对字典的key进行排序
        )
    })

    logger.info(f'filter_table llm: {results}')

    # results = {
    #     "表名1":["字段1", "字段2", "..."],
    #     "表名2":["字段1", "字段2", "..."]
    # }

    # 根据大模型过滤的结果results，去过滤table_infos
    # 不能遍历和删除同一个列表，会导致索引混乱
    # table_infos[:] 浅拷贝
    for table_info in table_infos[:]:
        if table_info["name"] not in results:
            # 不存在，删除表
            table_infos.remove(table_info)
        else:
            # 存在，过滤表名对应的字段
            columns = table_info["columns"]
            for column in columns[:]:
                if column["name"] not in results[table_info["name"]]:
                    columns.remove(column)

    logger.info(f'过滤表信息: {table_infos}')

    return {"table_infos": table_infos}
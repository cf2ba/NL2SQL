from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoEs
from app.prompt.prompt_loader import load_prompt


# 节点：召回字段取值
async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"召回字段取值"})

    query = state["query"]
    keywords = state["keywords"]
    value_es_repo = runtime.context['value_es_repo']

    # 提示词
    prompt = PromptTemplate(
        template=load_prompt('extend_keywords_for_value_recall'),
        input_variables=['query']
    )

    # 解析器
    output_parser = JsonOutputParser()

    # 构建处理链
    chain = prompt | llm | output_parser

    # 执行链
    results = await chain.ainvoke({"query": query})

    logger.info(f'召回字段取值 llm keywords：{results}')

    # 合并关键词
    keywords = list(set(keywords + results))

    # 保存召回字段值信息（去重）
    # {value_id:ValueInfoEs}
    recall_values_dict: dict[str,ValueInfoEs] = {}

    for keyword in keywords:
        # 去ES库检索召回
        values: list[ValueInfoEs] = await value_es_repo.search(keyword)

        # 遍历去重保存
        for value in values:
            value_id = value['id']
            if value_id not in recall_values_dict:
                recall_values_dict[value_id] = value

    # 将字典转成列表
    recall_values: list[ValueInfoEs] = recall_values_dict.values()

    logger.info(f'召回字段取值：{recall_values}')

    return {"recall_values": recall_values}
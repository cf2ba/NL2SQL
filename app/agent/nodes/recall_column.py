from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.prompt.prompt_loader import load_prompt


# 节点：召回字段信息
async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"召回字段信息"})

    # 1.用大模型对query进行语义分词，并与jieba的分词合并
    # 2.拿合并后的关键词去检索召回
    # 3.生成字段信息列表 list[ColumnInfoQdrant]

    query = state["query"]
    keywords = state["keywords"]
    embedding_client = runtime.context['embedding_client']
    column_qdrant_repo = runtime.context['column_qdrant_repo']

    # 提示词
    prompt = PromptTemplate(
        template=load_prompt('extend_keywords_for_column_recall'),
        input_variables=['query']
    )

    # 解析器
    output_parser = JsonOutputParser()

    # 构建处理链
    chain = prompt | llm | output_parser

    # 执行链
    results = await chain.ainvoke({"query": query})

    logger.info(f'召回字段信息 llm keywords：{results}')

    # 合并关键词
    keywords = list(set(keywords + results))

    # 保存召回的字段信息（去重）
    # {column_id:ColumnInfoQdrant}
    recall_columns_dict: dict[str,ColumnInfoQdrant] = {}

    for keyword in keywords:
        # 对keyword向量化
        vector = await embedding_client.aembed_query(keyword)
        # 检索qdrant库
        payloads: list[ColumnInfoQdrant] = await column_qdrant_repo.search(vector)

        # 遍历去重保存
        for payload in payloads:
            column_id = payload['id']
            if column_id not in recall_columns_dict:
                recall_columns_dict[column_id] = payload

    # 将字典转成列表
    recall_columns: list[ColumnInfoQdrant] = recall_columns_dict.values()

    logger.info(f'召回字段信息：{recall_columns}')

    return {"recall_columns": recall_columns}
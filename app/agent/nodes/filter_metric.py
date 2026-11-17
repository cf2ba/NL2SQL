import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


# 节点：过滤指标信息
async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"过滤指标信息"})

    query = state["query"]
    metric_infos = state["metric_infos"]

    # 提示词
    prompt = PromptTemplate(
        template=load_prompt('filter_metric_info'),
        input_variables=['query', 'metric_infos'],
    )

    # 解析器
    output_parser = JsonOutputParser()

    # 构建处理链
    chain = prompt | llm | output_parser

    # 执行链
    results = await chain.ainvoke({
        "query": query,
        "metric_infos": yaml.dump(  # 将python对象转成yaml字符串
            metric_infos,
            allow_unicode=True,  # 保留中文
            sort_keys=False,  # 不对字典的key进行排序
        )
    })
    # results = ['指标1','指标2']

    logger.info(f'filter_metric llm: {results}')

    # 遍历过滤metric_infos中的指标
    for metric in metric_infos[:]:
        if metric['name'] not in results:
            metric_infos.remove(metric)

    logger.info(f'过滤指标信息: {metric_infos}')

    return {"metric_infos": metric_infos}
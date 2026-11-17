"""
状态图：StateGraph实例
节点：实现了特定功能的函数
状态：包含多个可变数据的对象，在图的各个节点之间流传
边：节点之间的连线

节点函数的参数：
state 状态对象（可变的数据）
runtime: Runtime context（固定的数据）
    stream_writer() 向调用者输出自定义数据
    context 包含固定的数据或依赖
config: 保存配置的对象（不常用）
"""
import asyncio
from typing import TypedDict

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


class MyState(TypedDict):
    query: str
    keywords: list
    sql: str


class MyContext(TypedDict):
    db_name: str
    db_version: str



def extract_keyword(state: MyState, runtime: Runtime[MyContext], config: RunnableConfig):
    print('执行 extract_keyword 节点')

    print(state['query'])

    print(runtime.context['db_name'])

    runtime.stream_writer('提取关键字')

    return {"keywords":['好几个','结构','回复']}


def generate_sql(state: MyState, runtime: Runtime[MyContext], config: RunnableConfig):
    print('执行 generate_sql 节点')

    print(state['query'])

    print(runtime.context['db_name'])

    runtime.stream_writer('生成SQL')

    return {"sql":'select 1'}

# 创建图构建器
graph_builder = StateGraph(state_schema=MyState,context_schema=MyContext)

# 添加节点
graph_builder.add_node('extract_keyword',extract_keyword)
graph_builder.add_node('generate_sql',generate_sql)

# 添加边
graph_builder.add_edge(START,'extract_keyword')
graph_builder.add_edge('extract_keyword','generate_sql')
graph_builder.add_edge('generate_sql',END)

# 编译图
graph = graph_builder.compile()

if __name__ == '__main__':
    async def test():
        state = MyState(query='你今天吃了吗')
        context = MyContext(db_name='mysql', db_version='8.0.0')

        async for chunk in graph.astream(
            input=state,
            context=context,
            stream_mode='custom'
            # updates 获取到节点返回的更新
            # values 获取到更新合并后的state值
            # custom 得到 runtime.stream_writer 输出的数据
        ):
            print('---------------', chunk)

    asyncio.run(test())
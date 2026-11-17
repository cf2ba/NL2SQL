from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, TableInfoState, MetricInfoState
from app.core.log import logger
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


def _convert_column_info_mysql_to_qdrant(column_info: ColumnInfoMySQL) -> ColumnInfoQdrant:
    return ColumnInfoQdrant(
        id=column_info.id,
        name=column_info.name,
        description=column_info.description,
        role=column_info.role,
        type=column_info.type,
        examples=column_info.examples,
        alias=column_info.alias,
        table_id=column_info.table_id
    )


def _convert_column_info_qdrant_to_state(column: ColumnInfoQdrant)->ColumnInfoState:
    return ColumnInfoState(
        name=column['name'],
        type=column['type'],
        examples=column['examples'],
        alias=column['alias'],
        role=column['role'],
        description=column['description']
    )


def _convert_metric_info_qdrant_to_state(recall_metric: MetricInfoQdrant)->MetricInfoState:
    return MetricInfoState(
        name=recall_metric['name'],
        description=recall_metric['description'],
        relevant_columns=recall_metric['relevant_columns'],
        alias=recall_metric['alias']
    )

# 节点：合并召回信息
async def merge_recall(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage":"合并召回信息"})

    # 1.收集完整的字段信息
    # 1.1以recall_columns为主
    # 1.2补充：指标关联的字段信息
    # 1.3补充：字段值关联的字段信息（值加入examples）
    # 1.4补充：表的主外键信息
    # 补充的前提：recall_columns没有

    # 创建list[ColumnInfoState]列表
    # 创建list[TableInfoState]列表
    # 创建list[MetricInfoState]列表

    recall_columns = state['recall_columns']
    recall_metrics = state['recall_metrics']
    recall_values = state['recall_values']
    meta_mysql_repo = runtime.context['meta_mysql_repo']

    # 创建list[TableInfoState]列表
    table_infos: list[TableInfoState] = []

    # 1.收集完整的字段信息
    # 1.1以recall_columns为主
    # {column_id : ColumnInfoQdrant}
    column_infos_dict: dict[str,ColumnInfoQdrant] = {column['id']:column for column in recall_columns}

    # 1.2补充：指标关联的字段信息
    for recall_metric in recall_metrics:
        for column_id in recall_metric['relevant_columns']:
            if column_id not in column_infos_dict:
                # 如果当前字段不在召回的字段信息列表中，去meta库查询当前字段信息
                column_info_mysql: ColumnInfoMySQL = await meta_mysql_repo.get_column_info_by_id(column_id)
                column_infos_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)

    # 1.3补充：字段值关联的字段信息（值加入examples）
    for value_info in recall_values:
        column_id = value_info['column_id']
        if column_id not in column_infos_dict:
            # 如果当前字段不在召回的字段信息列表中，去meta库查询当前字段信息
            column_info_mysql: ColumnInfoMySQL = await meta_mysql_repo.get_column_info_by_id(column_id)
            column_infos_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)

        # 值加入examples
        if value_info['value'] not in column_infos_dict[column_id]['examples']:
            column_infos_dict[column_id]['examples'].append(value_info['value'])


    # 对字段信息列表 按表 分组
    # {table_id : list[ColumnInfoQdrant]}
    table_column_dict: dict[str,list[ColumnInfoQdrant]] = {}
    for column_info in column_infos_dict.values():
        table_id = column_info['table_id']
        if table_id not in table_column_dict:
            table_column_dict[table_id] = []
        table_column_dict[table_id].append(column_info)


    # 1.4补充：表的主外键信息
    for table_id,column_list in table_column_dict.items():
        # 去meta库查询当前table_id的主外键字段信息
        pf_column_infos: list[ColumnInfoMySQL] = await meta_mysql_repo.get_column_infos_by_table_id(table_id)
        # 将主外键字段信息ColumnInfoMySQL类型转成ColumnInfoQdrant
        for pf_column_info in pf_column_infos:
            pf_column_info_qdrant = _convert_column_info_mysql_to_qdrant(pf_column_info)
            if pf_column_info.id not in column_infos_dict:
                # table_column_dict 是根据 column_infos_dict 添加的数据
                table_column_dict[table_id].append(pf_column_info_qdrant)


        # 创建list[ColumnInfoState]列表
        columns: list[ColumnInfoState] = [_convert_column_info_qdrant_to_state(column) for column in column_list]

        # 根据table_id查询表的信息
        table_info_mysql: TableInfoMySQL = await meta_mysql_repo.get_table_info_by_id(table_id)

        # 创建TableInfoState对象
        table_info = TableInfoState(
            name=table_info_mysql.name,
            role=table_info_mysql.role,
            description=table_info_mysql.description,
            columns=columns,
        )
        table_infos.append(table_info)

    logger.info(f'合并召回表信息：{table_infos}')


    # 创建list[MetricInfoState]列表
    metric_infos = [_convert_metric_info_qdrant_to_state(recall_metric) for recall_metric in recall_metrics]

    logger.info(f'合并召回指标信息：{metric_infos}')

    return {"table_infos": table_infos, "metric_infos": metric_infos}

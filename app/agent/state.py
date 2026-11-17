from typing import TypedDict

from app.models.es.value_info_es import ValueInfoEs
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list[str]
    description: str
    alias: list[str]

class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]

class MetricInfoState(TypedDict):
    name: str
    description: str
    alias: list[str]
    relevant_columns: list[str]

class DateInfoState(TypedDict):
    date: str # 年 月 日
    quarter: str # 季度 Q1-Q4

class DBInfoState(TypedDict):
    dialect: str # 方言（数据库名称）
    version: str # 数据库版本号


# 状态数据（可变的数据）
class DataAgentState(TypedDict):
    query: str
    keywords: list[str]
    sql: str
    error: str | None
    recall_columns: list[ColumnInfoQdrant]
    recall_metrics: list[MetricInfoQdrant]
    recall_values: list[ValueInfoEs]
    table_infos: list[TableInfoState]
    metric_infos: list[MetricInfoState]
    date_info: DateInfoState
    db_info: DBInfoState

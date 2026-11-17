from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

# 上下文数据（固定数据/依赖）
class DataAgentContext(TypedDict):
    embedding_client: HuggingFaceEndpointEmbeddings
    value_es_repo: ValueEsRepository
    column_qdrant_repo: ColumnQdrantRepository
    metric_qdrant_repo: MetricQdrantRepository
    dw_mysql_repo: DwMysqlRepository
    meta_mysql_repo: MetaMysqlRepository
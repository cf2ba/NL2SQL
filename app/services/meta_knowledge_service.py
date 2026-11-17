"""
实现具体的业务逻辑
"""
import uuid

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sentry_sdk import metrics

from app.conf.meta_config import MetaConfig, TableConfig, MetricConfig
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoEs
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw_mysql_repository import DwMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class MetaKnowledgeService:
    def __init__(
            self,
            value_es_repo: ValueEsRepository,
            dw_mysql_repo: DwMysqlRepository,
            meta_mysql_repo: MetaMysqlRepository,
            column_qdrant_repo: ColumnQdrantRepository,
            metric_qdrant_repo: MetricQdrantRepository,
            embedding_client: HuggingFaceEndpointEmbeddings
    ):
        self.value_es_repo = value_es_repo
        self.dw_mysql_repo = dw_mysql_repo
        self.meta_mysql_repo = meta_mysql_repo
        self.column_qdrant_repo = column_qdrant_repo
        self.metric_qdrant_repo = metric_qdrant_repo
        self.embedding_client = embedding_client

    async def build(self, config: MetaConfig):
        logger.info('构建业务 开始')

        # 构建元数据知识库思路分析：
        # 1.处理表/字段信息
        # 1.1保存表信息到meta库中的table_info
        # 1.2保存字段信息到meta库中的column_info
        # 1.3为字段信息建立向量索引
        # 1.4为字段取值建立全文索引

        # 2.处理指标信息
        # 2.1保存指标信息到meta库中的metric_info
        # 2.2保存字段和指标的关联信息到meta库中的column_metric
        # 2.3为指标信息建立向量索引


        if config.tables:
            # 1.1保存表信息到meta库中的table_info
            column_infos: list[ColumnInfoMySQL] = await self._save_table_infos_to_meta(config.tables)
            logger.info('保存表信息完成')

            # 1.2保存字段信息到meta库中的column_info
            await self._save_column_infos_to_meta(column_infos)
            logger.info('保存字段信息完成')

            # 1.3为字段信息建立向量索引
            await self._save_column_infos_to_qdrant(column_infos)
            logger.info('为字段信息建立向量索引')

            # 1.4为字段取值建立全文索引
            await self._save_column_values_to_es(column_infos, config.tables)
            logger.info('为字段取值建立全文索引')


        if config.metrics:
            # 2.1保存指标信息到meta库中的metric_info
            metric_infos: list[MetricInfoMySQL] = await self._save_metric_infos_to_meta(config.metrics)
            logger.info('保存指标信息完成')

            # 2.2保存字段和指标的关联信息到meta库中的column_metric
            await self._save_column_metric_to_meta(config.metrics)
            logger.info('保存字段和指标关联信息')

            # 2.3为指标信息建立向量索引
            await self._save_metric_infos_to_qdrant(metric_infos)
            logger.info('为指标信息建立向量索引')


        logger.info('构建业务 结束')


    # -----------------------------------------------------------------------

    async def _save_table_infos_to_meta(self, tables: list[TableConfig])->list[ColumnInfoMySQL]:
        # 收集表信息
        table_infos: list[TableInfoMySQL] = []
        # 收集字段信息
        column_infos: list[ColumnInfoMySQL] = []

        # 遍历tables
        for table in tables:
            table_info = TableInfoMySQL(
                id=table.name,
                role=table.role,
                description=table.description,
                name=table.name
            )
            table_infos.append(table_info)

            # 查询dw库获取当前table中所有的字段数据类型
            # column_types = {字段名1：数据类型，字段名2：数据类型}
            column_types: dict = await self.dw_mysql_repo.get_column_types(table.name)

            for column in table.columns:
                # 查询dw库当前column的前10条数据
                column_values: list = await self.dw_mysql_repo.get_column_values(table.name, column.name, 10)

                column_info = ColumnInfoMySQL(
                    id=f'{table.name}.{column.name}',
                    name=column.name,
                    role=column.role,
                    description=column.description,
                    alias=column.alias,
                    type=column_types[column.name], # 查询dw库获取
                    examples=column_values, # 查询dw库获取
                    table_id=table.name,
                )
                column_infos.append(column_info)

        # 将table_infos保存到meta库
        self.meta_mysql_repo.save_table_infos(table_infos)

        # 返回字段信息
        return column_infos



    async def _save_column_infos_to_meta(self, column_infos: list[ColumnInfoMySQL]):
        self.meta_mysql_repo.save_column_infos(column_infos)


    async def _save_column_infos_to_qdrant(self, column_infos: list[ColumnInfoMySQL]):
        # 遍历column_infos。对每一个column_info中的name、description和alias中的每一个值建立向量索引
        # pointStruct = {id: uuid.uuid4(), text:要向量化的文本, payload: {...}}
        # 传递 ids: list   vectors: list   payloads: list 给持久层保存到qdrant

        # points = [{id: uuid.uuid4(), text:要向量化的文本, payload: {...}}]
        points: list[dict] = []
        for column_info in column_infos:
            payload = ColumnInfoQdrant(
                id=column_info.id,
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                examples=column_info.examples,
                description=column_info.description,
                alias=column_info.alias,
                table_id=column_info.table_id,
            )

            # name字段
            points.append({
                "id": uuid.uuid4(),
                "text": column_info.name,
                "payload": payload
            })

            # description字段
            points.append({
                "id": uuid.uuid4(),
                "text": column_info.description,
                "payload": payload
            })

            # alias字段
            for alia in column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "text": alia,
                    "payload": payload
                })

        # 获取所有向量文本
        texts = [point['text'] for point in points]

        # 每批向量化的数量
        batch_size = 10
        # 所有向量的列表
        vectors: list[list[float|int]] = []

        for i in range(0,len(texts),batch_size):
            # i -> 0   i -> 10 ...
            # 获取一批向量文本
            batch_texts = texts[i:i+batch_size]
            # 向量化一批文本
            batch_vectors = await self.embedding_client.aembed_documents(batch_texts)
            # vectors.append(batch_vectors) # [[[]]]
            vectors.extend(batch_vectors)

        # 获取所有点的id
        ids = [point['id'] for point in points]

        # 获取所有点的payload
        payloads = [point['payload'] for point in points]

        await self.column_qdrant_repo.upsert_column_vectors(ids, vectors, payloads)



    async def _save_column_values_to_es(self, column_infos: list[ColumnInfoMySQL], tables: list[TableConfig]):
        # 遍历column_infos，根据配置sync判断字段是否需要建立全文索引
        # 查询dw库取出需要建立全文索引的字段的所有值
        # 创建ValueInfoEs对象，并添加到列表中
        # 调用持久层方法保存到ES中

        value_infos: list[ValueInfoEs] = []

        # 收集配置中所有字段的sync
        # dict[column_id,bool]
        column_sync_dict: dict[str,bool] = {}

        for table in tables:
            for column in table.columns:
                column_id = f'{table.name}.{column.name}'
                column_sync_dict[column_id] = column.sync

        # 遍历column_infos，根据配置sync判断字段是否需要建立全文索引
        for column_info in column_infos:
            if column_sync_dict.get(column_info.id):
                # 查询dw库取出指定字段的所有值
                values: list = await self.dw_mysql_repo.get_column_values(column_info.table_id, column_info.name, 1000000)
                for value in values:
                    value_infos.append(ValueInfoEs(
                        id=f'{column_info.id}.{value}',
                        value=value,
                        type=column_info.type,
                        column_id=column_info.id,
                        column_name=column_info.name,
                        table_id=column_info.table_id,
                        table_name=column_info.table_id
                    ))

        # 调用持久层方法保存到ES中
        await self.value_es_repo.insert_values(value_infos)



    async def _save_metric_infos_to_meta(self, metrics: list[MetricConfig])->list[MetricInfoMySQL]:
        # 收集所有指标信息
        metric_infos: list[MetricInfoMySQL] = []
        for metric in metrics:
            metric_infos.append(MetricInfoMySQL(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            ))

        # 保存到meta库
        self.meta_mysql_repo.save_metric_infos(metric_infos)

        # 返回指标信息
        return metric_infos



    async def _save_column_metric_to_meta(self, metrics: list[MetricConfig]):
        column_metrics: list[ColumnMetricMySQL] = []

        for metric in metrics:
            for column_id in metric.relevant_columns:
                column_metrics.append(ColumnMetricMySQL(
                    column_id=column_id,
                    metric_id=metric.name
                ))

        self.meta_mysql_repo.save_column_metrics(column_metrics)




    async def _save_metric_infos_to_qdrant(self, metric_infos: list[MetricInfoMySQL]):
        # 遍历metric_infos。对每一个metric_info中的name、description和alias中的每一个值建立向量索引
        # pointStruct = {id: uuid.uuid4(), text:要向量化的文本, payload: {...}}
        # 传递 ids: list   vectors: list   payloads: list 给持久层保存到qdrant

        # points = [{id: uuid.uuid4(), text:要向量化的文本, payload: {...}}]
        points: list[dict] = []
        for metric_info in metric_infos:
            payload = MetricInfoQdrant(
                id=metric_info.id,
                name=metric_info.name,
                description=metric_info.description,
                alias=metric_info.alias,
                relevant_columns=metric_info.relevant_columns
            )

            # name字段
            points.append({
                "id": uuid.uuid4(),
                "text": metric_info.name,
                "payload": payload
            })

            # description字段
            points.append({
                "id": uuid.uuid4(),
                "text": metric_info.description,
                "payload": payload
            })

            # alias字段
            for alia in metric_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "text": alia,
                    "payload": payload
                })

        # 获取所有向量文本
        texts = [point['text'] for point in points]

        # 每批向量化的数量
        batch_size = 10
        # 所有向量的列表
        vectors: list[list[float | int]] = []

        for i in range(0, len(texts), batch_size):
            # i -> 0   i -> 10 ...
            # 获取一批向量文本
            batch_texts = texts[i:i + batch_size]
            # 向量化一批文本
            batch_vectors = await self.embedding_client.aembed_documents(batch_texts)
            # vectors.append(batch_vectors) # [[[]]]
            vectors.extend(batch_vectors)

        # 获取所有点的id
        ids = [point['id'] for point in points]

        # 获取所有点的payload
        payloads = [point['payload'] for point in points]

        await self.metric_qdrant_repo.upsert_metric_vectors(ids, vectors, payloads)
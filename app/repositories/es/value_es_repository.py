"""
操作ES库
"""
from elasticsearch import AsyncElasticsearch

from app.models.es.value_info_es import ValueInfoEs


class ValueEsRepository:
    index_name = 'values_index'
    mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text","analyzer": "ik_max_word","search_analyzer": "ik_smart"},
            "type": {"type": "keyword"},
            "column_id": {"type": "keyword"},
            "column_name": {"type": "keyword"},
            "table_id": {"type": "keyword"},
            "table_name": {"type": "keyword"}
        }
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def insert_values(self, value_infos: list[ValueInfoEs]):
        if await self.client.indices.exists(index=self.index_name):
            await self.client.indices.delete(index=self.index_name)

        # 创建index
        await self.client.indices.create(
            index=self.index_name,
            mappings=self.mappings
        )

        # 添加多个文档
        # 一个文档 = item1 + item2
        # await self.client.bulk(
        #     operations=[
        #         { # item1
        #             "index": {
        #                 "_index": self.index_name,
        #             }
        #         },
        #         { # item2 -> ValueInfoEs对象
        #             "name": "Revelation Space",
        #             "author": "Alastair Reynolds",
        #             "release_date": "2000-03-15",
        #             "page_count": 585
        #         }
        #     ]
        # )

        operations = []
        item1 = {"index":{"_index": self.index_name}}
        for item2 in value_infos:
            operations.append(item1)
            operations.append(item2)

        # 分批添加数据
        batch_size = 20
        for i in range(0, len(operations), batch_size):
            batch_operations = operations[i:i + batch_size]
            await self.client.bulk(operations=batch_operations)

    async def search(self, keyword: str, limit: int = 5)-> list[ValueInfoEs]:
        # 查询数据（设置查询条件）
        result = await self.client.search(
            index=self.index_name,
            query={
                "match": {  # 设置查询的键和值
                    "value": keyword
                }
            },
            size=limit,
            min_score=0.6
        )
        return [ValueInfoEs(**item['_source']) for item in result['hits']['hits']]



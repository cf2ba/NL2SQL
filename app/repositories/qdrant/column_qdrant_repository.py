"""
操作qdrant库
"""
from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    collection_name = 'column_infos'

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def upsert_column_vectors(self, ids: list, vectors: list[list[float|int]], payloads: list[ColumnInfoQdrant]):
        if not await self.client.collection_exists(collection_name=self.collection_name):
            # 异步创建集合
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(  # 向量的配置
                    size=app_config.qdrant.embedding_size,  # 向量维度
                    distance=models.Distance.COSINE  # 相似度算法
                )
            )


        # 一次性添加所有数据
        # await self.client.upsert(
        #     collection_name=self.collection_name,
        #     points=[
        #         models.PointStruct(
        #             id=ids[i],
        #             payload=payloads[i],
        #             vector=vectors[i],
        #         )
        #         for i in range(0,len(ids))
        #     ]
        # )


        # 分批添加数据
        batch_size = 10
        for i in range(0,len(ids),batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_vectors = vectors[i:i+batch_size]
            batch_payloads = payloads[i:i+batch_size]
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=batch_ids[i],
                        payload=batch_payloads[i],
                        vector=batch_vectors[i]
                    )
                    for i in range(0, len(batch_ids))
                ]
            )

    async def search(self, vector: list[float|int])->list[ColumnInfoQdrant]:
        # 查询数据
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=vector,  # embedding向量
            limit=5,
            score_threshold=0.6  # 阈值，低于阈值的数据被忽略
        )
        # response = [ScoredPoint,ScoredPoint,ScoredPoint....]
        # payload = ScoredPoint.payload 字典

        # return [point.payload for point in response.points]
        return [ColumnInfoQdrant(**point.payload) for point in response.points]






import asyncio

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: AsyncQdrantClient | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = AsyncQdrantClient(self._get_url())

    async def close(self):
        await self.client.close()

# 创建客户端管理器
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    async def test():
        # 初始化客户端
        qdrant_client_manager.init()
        # 获取客户端
        client = qdrant_client_manager.client

        if await client.collection_exists(collection_name='test_collection'):
            await client.delete_collection(collection_name='test_collection')

        # 创建集合
        await client.create_collection(
            collection_name="test_collection", # 集合名称
            vectors_config=models.VectorParams( # 向量的配置
                size=4, # 向量维度
                distance=models.Distance.COSINE # 相似度算法
            ),
        )

        # 添加数据/修改数据
        await client.upsert(
            collection_name="test_collection",
            points=[
                models.PointStruct(
                    id=11,
                    payload={
                        "color": "red",
                        "num": 1
                    },
                    vector=[0.9, 0.1, 0.1, 0.5],
                ),
                models.PointStruct(
                    id=22,
                    payload={
                        "color": "blue",
                        "num": 2
                    },
                    vector=[0.9, 0.2, 0.1, 0.5],
                ),
                models.PointStruct(
                    id=33,
                    payload={
                        "color": "yellow",
                        "num": 1
                    },
                    vector=[0.9, 0.1, 0.3, 0.5],
                ),
                models.PointStruct(
                    id=44,
                    payload={
                        "color": "green",
                        "num": 2
                    },
                    vector=[0.9, 0.1, 0.1, 0.1],
                ),
                models.PointStruct(
                    id=55,
                    payload={
                        "color": "orange",
                        "num": 1
                    },
                    vector=[0.9, -0.1, 0.1, 0.5],
                ),
                models.PointStruct(
                    id=66,
                    payload={
                        "color": "pink",
                        "num": 3
                    },
                    vector=[0.2, 0.1, 0.1, 0.5],
                )
            ],
        )

        # 删除数据
        # result = await client.delete(
        #     collection_name='test_collection',
        #     points_selector=[66]
        # )
        # print(result) # completed


        # 查询数据
        response = await client.query_points(
            collection_name="test_collection",
            query=[0.9, 0.1, 0.7, 0.5], # embedding向量
            limit=4,
            score_threshold=0.6, # 阈值，低于阈值的数据被忽略
            query_filter=models.Filter( # 根据payload中的键和值设置过滤条件
                must=[
                    models.FieldCondition(
                        key='num',
                        match=models.MatchValue(value=2),
                    )
                ]
            )
        )
        print(response.points)



        # 关闭客户端
        await qdrant_client_manager.close()

    asyncio.run(test())
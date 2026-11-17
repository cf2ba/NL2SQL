import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class EsClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: AsyncElasticsearch | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = AsyncElasticsearch(self._get_url())

    async def close(self):
        await self.client.close()

# 创建客户端管理器
es_client_manager = EsClientManager(app_config.es)

if __name__ == '__main__':
    async def test():
        es_client_manager.init()
        client = es_client_manager.client

        if await client.indices.exists(index='test_books'):
            await client.indices.delete(index='test_books')

        # 创建索引
        await client.indices.create(
            index="test_books",
            mappings={ # 定义静态映射
                "dynamic": False, # 关闭动态映射
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            }
        )

        # 添加单个文档
        await client.index(
            index="test_books",
            document={
                "name": "Snow Crash",
                "author": "Neal Stephenson",
                "release_date": "1992-06-01",
                "page_count": 470
            },
        )

        # 添加多个文档
        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": "test_books"
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": "test_books"
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": "test_books"
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": "test_books"
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": "test_books"
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
            # refresh=True # 自动刷新
        )


        # 添加文档后需要等1秒数据才会落盘
        await asyncio.sleep(1)

        # refresh = True  # 自动刷新也可以马上查询到最新的数据

        # 实际使用不需要考虑这个问题，因为添加数据和查询数据是分开的


        # 查询数据
        # result = await client.search(
        #     index="test_books",
        # )

        # print(result['hits']['hits'][0]['_source']) # {'name': 'Snow Crash', 'author': 'Neal Stephenson', 'release_date': '1992-06-01', 'page_count': 470}


        # 查询数据（设置查询条件）
        result = await client.search(
            index="test_books",
            query={
                "match": { # 设置查询的键和值
                    "name": "brave"
                }
            }
        )
        print(result['hits']['hits'])

        await es_client_manager.close()

    asyncio.run(test())
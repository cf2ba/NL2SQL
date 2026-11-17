import asyncio

from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())

    # 使用后自动释放资源

# 创建客户端管理器
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    async def test():
        embedding_client_manager.init()
        client = embedding_client_manager.client

        text1 = 'hello'
        text2 = 'world'

        # 对单个文本向量化
        # result = client.embed_query(text1)
        # print(len(result)) # 1024

        # 对多个文本向量化
        results = client.embed_documents([text1, text2])
        print(results) # [[...],[...]]

    asyncio.run(test())
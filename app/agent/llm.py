import os

from langchain.chat_models import init_chat_model


from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key=app_config.llm.api_key,
    temperature=0, # 表示确定性输出
    # base_url=
    # model_provider=
)

if __name__ == '__main__':
    for chunk in llm.stream('渊哥喜欢杨幂吗？'):
        print(chunk.text,end='',flush=True)


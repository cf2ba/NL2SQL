import uuid

import uvicorn
from fastapi import FastAPI, Request

from app.api.routers.query_router import query_router
from app.core.context import set_request_id
from app.core.lifespan import lifespan

# 创建FastAPI实例
app = FastAPI(lifespan=lifespan)

# 注册路由器（路由表）
app.include_router(query_router, prefix="/api")

# 中间件
# 针对每一个http请求
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # print('路由处理函数执行前。。。。')
    # 给每一个请求设置一个唯一的请求id
    set_request_id(uuid.uuid4())

    response = await call_next(request) # 调用下一个中间件或目标路由函数

    # print('。。。路由处理函数执行后')

    return response

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8008)


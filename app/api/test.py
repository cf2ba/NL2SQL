import asyncio

import uvicorn
from fastapi import FastAPI,Request,Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

# 生命周期：一个事物从开始到结束经历的关键阶段
# 针对整个应用服务
@asynccontextmanager
async def lifespan(app: FastAPI):
    print('服务启动后最先执行，做一次性的初始化工作')

    yield

    print('服务关闭前最后执行，做一次性的收尾工作')


# 创建FastAPI实例
app = FastAPI(lifespan=lifespan)


# 中间件（拦截器）：介于两个程序之间的程序
# 针对每一个http请求
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    print('路由处理函数执行前。。。。')

    response = await call_next(request) # 调用下一个中间件或目标路由函数

    print('。。。路由处理函数执行后')

    return response



# 注册路由（接口）
# 路由其实是一种映射关系
# key : value
# key 是一个请求路径
# value 是对应的处理函数
# 请求一个路径，执行对应的处理（路由）函数
@app.get('/users')
async def get_users():
    print('处理 get /users 请求')

    # 响应给前端的内容
    return {"users":{"name":"老王","age":35}}

@app.post('/users')
async def post_users():
    print('处理 post /users 请求')

    # 响应给前端的内容
    return {"users":{"name":"小王","age":25}}



# https://re.m.jd.com:443/page/homelike?ad_od=3&traffic_source=1004&re_dcp=202m0QjIIg==&bd_vid=nHfvnWfdPWbsP1bvn10YrHn1rj9xnH64n-tkg1Dsn0&cu=true&utm_source=baidu-search&utm_medium=cpc&utm_campaign=t_262767352_baidusearch&utm_term=304792146367_0_9f585801f368e5493be6b9772793389c
# 请求url:http://127.0.0.1:8008/users/123?a=11&b=22&c=33
# 参数：
# path参数 请求url中的路径部分的参数
# query参数 问号后面的键值对
# body参数 请求体中的参数
# 请求报文（请求行 请求头 空行 请求体）
# 响应报文

# 定义body的数据模型
class MyData(BaseModel):
    name: str
    age: int

@app.post('/test/{uid}')
async def test(uid: str, data: MyData):
    return {"id": uid,"data": data}



# 流式输出
async def fake_video_streamer():
    for i in range(10):
        # SSE协议流式输出数据格式：'data: 数据\n\n'
        yield 'data: {"name":"zhangsan","age":23}\n\n'
        await asyncio.sleep(1)

@app.get("/stream")
async def test_stream():
    return StreamingResponse(
        fake_video_streamer(),
        media_type="text/event-stream"
        # 设置响应头的media_type，告诉客户端要遵循SSE协议，按照SSE规则解析流式数据
    )


# 依赖注入（懒加载）
def get_friends():
    return ['李四','王五','马六']

def get_data(friends: list = Depends(get_friends)):
    return {"name":"张三","age":25,"friends":friends}

@app.get("/depend")
async def test_depend(data: dict = Depends(get_data)):
    return data


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8008)
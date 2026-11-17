import asyncio
from _contextvars import ContextVar

# contextVar 上下文变量，用于在多个异步任务之间隔离数据

# 创建上下文变量
# 参数1：上下文变量名称
# 参数2: 上下文变量的默认值
_request_id_context_var: ContextVar = ContextVar("request_id", default='None')

# 设置请求id
def set_request_id(rid: str):
    _request_id_context_var.set(rid)

# 获取请求id
def get_request_id()->str:
    return _request_id_context_var.get()


if __name__ == '__main__':
    # 模拟两个异步请求
    async def request1():
        print(f'请求1开始执行，request_id={get_request_id()}') # None
        # 设置上下文变量的值
        set_request_id('11')
        print(f'请求1开始结束，request_id={get_request_id()}') # 11

    async def request2():
        print(f'请求2开始执行，request_id={get_request_id()}') # None
        # 设置上下文变量的值
        set_request_id('22')
        print(f'请求2开始结束，request_id={get_request_id()}') # 22

    async def main():
        await asyncio.gather(request1(), request2())

    asyncio.run(main())
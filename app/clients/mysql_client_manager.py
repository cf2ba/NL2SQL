import asyncio

from sqlalchemy import text, Select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig, app_config
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MySQLClientManager:
    def __init__(self, config: DBConfig):
        self.config = config
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker | None = None

    def _get_url(self):
        # 获取连接地址
        return f'mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}/{self.config.database}?charset=utf8mb4'

    def init(self):
        # 创建异步引擎
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=10, # 初始创建的常驻链接数
            pool_pre_ping=True, # 检测常驻链接是否可以正常使用
        )

        # 创建异步会话工厂
        self.session_factory = async_sessionmaker(
            self.engine,
            autoflush=True, # 自动刷新，未提交事务的更新数据也可以查询到最新数据
            autobegin=True, # 自动开启事务
            expire_on_commit=False, # 提交事务之后，ORM对象中的数据是否过期
        )

    async def close(self):
        # 关闭引擎
        await self.engine.dispose()

# 创建客户端管理器
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)
meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)


if __name__ == '__main__':
    async def test1():
        # 初始化客户端
        dw_mysql_client_manager.init()

        # 创建异步会话
        async with dw_mysql_client_manager.session_factory() as session:
            # 添加数据（未提交事务）
            # 。。。

            # 查询数据
            result = await session.execute(text("select * from dim_customer limit 2"))

            # print(result) # <sqlalchemy.engine.cursor.CursorResult object at 0x0000023E7C19CA60>
            # print(result.all()) # [('C001', '李伟', '男', '黄金'), ('C002', '王芳', '女', '白银')]

            # print(result.mappings().all()) # [{'customer_id': 'C001', 'customer_name': '李伟', 'gender': '男', 'member_level': '黄金'}, {'customer_id': 'C002', 'customer_name': '王芳', 'gender': '女', 'member_level': '白银'}]

            # print(result.scalars().all()) # ['C001', 'C002']

            # print(result.scalar()) # C001

        # 关闭引擎，释放资源
        await dw_mysql_client_manager.close()

    # 执行协程
    # asyncio.run(test1())


    async def test2():
        # 初始化客户端
        meta_mysql_client_manager.init()

        # 创建异步会话
        async with meta_mysql_client_manager.session_factory() as session:
            # 创建ORM对象
            table1 = TableInfoMySQL(
                id='111',
                name='test_table1',
                role='fact',
                description='测试ORM操作111'
            )
            table2 = TableInfoMySQL(
                id='2',
                name='test_table2',
                role='dim',
                description='测试ORM操作222'
            )

            # 添加数据
            # session.add(table1)
            # session.add(table2)


            # 修改数据
            table3 = await session.get(TableInfoMySQL,'111')
            table3.description = '测试ORM操作333'


            # 查询一条数据
            result: TableInfoMySQL = await session.get(TableInfoMySQL,'2')
            print(result.name) # test_table2

            # 查询多条数据
            results = await session.execute(Select(TableInfoMySQL).limit(2))
            tables: list[TableInfoMySQL] = results.scalars().all()
            print(tables[0].name) # test_table1

            # 删除数据
            table4 = await session.get(TableInfoMySQL, '2')
            await session.delete(table4)


            # 提交事务
            await session.commit()

            # 关闭引擎，释放资源

            await meta_mysql_client_manager.close()

    # 执行协程
    asyncio.run(test2())
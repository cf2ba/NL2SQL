"""
操作dw库
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str)->dict:
        sql = f'show columns from {table_name}'
        result = await self.session.execute(text(sql))
        return {row.Field:row.Type for row in result.all()}

    async def get_column_values(self, table_name: str, column_name: str, limit: int = 5)->list:
        sql = f'select distinct {column_name} from {table_name} limit {limit}'
        result = await self.session.execute(text(sql))
        return result.scalars().all()

    async def get_db_info(self)->dict:
        result = await self.session.execute(text('select version()'))
        version = result.scalar()

        dialect = self.session.get_bind().dialect.name

        return {'dialect':dialect,'version':version}


    async def to_validate_sql(self, sql: str):
        await self.session.execute(text(f'explain {sql}'))


    async def to_execute_sql(self, sql:str)->list[dict]:
        result = await self.session.execute(text(sql))

        return [dict(row) for row in result.mappings().all()]


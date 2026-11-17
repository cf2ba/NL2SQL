from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

# 创建路由器（路由表）
query_router = APIRouter()

# 注册路由（接口）
@query_router.post('/query')
async def query(query_schema: QuerySchema, query_service: QueryService = Depends(get_query_service)):
    return StreamingResponse(
        query_service.search(query_schema.query),
        media_type="text/event-stream"
        # 设置响应头的media_type，告诉客户端要遵循SSE协议，按照SSE规则解析流式数据
    )

from fastapi import APIRouter

router = APIRouter(
    prefix="/export",       # 可选：为该模块所有路径加前缀
    tags=["export"],        # 可选：Swagger 文档分组
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def exportparams():
    # 将参数存入到 数据库
    return [{"name": "Item Foo"}, {"name": "Item Bar"}]
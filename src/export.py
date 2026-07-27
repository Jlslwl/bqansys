import os

from fastapi import APIRouter, HTTPException
import subprocess
from starlette.responses import FileResponse

router = APIRouter(
    prefix="/export",       # 可选：为该模块所有路径加前缀
    tags=["export"],        # 可选：Swagger 文档分组
    responses={404: {"description": "Not found"}},
)

@router.post("/")
def exportparams():
    # 将参数存入到 数据库
    res = 'test'
    filename = 'dianpian.txt'
    str_cmd = f'ansys -dir {res} -b -i {filename} -o output.txt'
    # res = subprocess.run(str_cmd)
    return [{"name": "Item Foo"}, {"name": "Item Bar"}]

# 1. 小文件下载（推荐）
@router.get("/export/{filename}")
async def download_small(filename: str):
    file_path = f"./docs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    # filename 参数指定下载时的文件名，media_type 建议设为二进制流强制下载
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
import os
import yaml
import shutil
from fastapi import FastAPI
import sqlalchemy
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile, Form, Request, Body
from typing import Annotated
from pathlib import Path
from sqlalchemy.orm import sessionmaker

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from utils.save_file import save_file

filename = os.path.dirname(os.path.dirname(__file__)) + '/config.yaml'

# #####连接数据库#####
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
import export
import doansys

with open(filename, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    db_config = config['database']

dataname = db_config['dbname']
host = db_config['host']
port = db_config['port']
username = db_config['username']
password = db_config['password']
engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{username}:{password}@{host}:{port}/{dataname}",
    pool_pre_ping=True,
)
Session = sessionmaker(bind=engine)
Base = automap_base()
Base.prepare(engine,reflect=True)
Proparams = Base.classes.bpm_som_pro_param
# 测试数据库连接
####################
app = FastAPI()


# 允许所有服务跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*']
)
# 将子路由挂载到主应用
app.include_router(export.router)
app.include_router(doansys.router)


RAW_DATA_DICT = {}

ENCODINGS = [
    "utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-32", "utf-32-le", "ascii", "gbk", "gb2312", "iso-8859-1",
]


# loadtype = 1，需要解析内容，反给前端， 否则直接保存
@app.post('/upload/')
async def upload(
        file: Annotated[UploadFile, File()],
        uid: Annotated[str, Form()],
        ltype: Annotated[str, Form()]
):
    if ltype == '1':
        raw_data = file.file.read()
        file_name = file.filename
        RAW_DATA_DICT[uid] = (raw_data, file_name)
        try:
            text_data = raw_data.decode('utf-8', errors='strict')
            j_data = [{'content': data} for data in text_data.splitlines()]
            return j_data
        except:
            return {'content': '解析错误'}
    else:
        file_path = Path('../testdata/' + uid + '/' + file.filename)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb", ) as buffer:
                shutil.copyfileobj(file.file, buffer)
            return {
                "message": "Large file uploaded successfully",
                "filename": file_path
            }
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            print(repr(e))
            return {
                "error": "file uploaded failed",
            }


# 返回解析文件类型
@app.get('/codingtype/')
async def codingtype():
    return {'type': ENCODINGS}


# 解析文件api
@app.post('/parsefile/')
async def parsefile(request: dict = Body(...)):
    uid = request.get('uid')
    recode = request.get('coding')
    raw_data, _ = RAW_DATA_DICT.get(uid)
    try:
        text_data = raw_data.decode(recode, errors='strict')
        j_data = [{'content': data} for data in text_data.splitlines()]
        return j_data
    except UnicodeError as exc:
        print(repr(exc))
        return [{'content': '解析错误'},]

# 接收所有参数，可以然后保存到数据库
@app.post('receive_params')
async def recparams(request: dict = Body(...)):
    data_list = request['changeParams']
    guid = request['guid']
    usage = request['usage']
    # 文本 将文本 转为 utf-8 方便后续训练使用
    raw_data, file_name = RAW_DATA_DICT[guid]
    save_file(raw_data,file_name)


    with Session() as session:
        for content_data in data_list:
            guid = content_data.get('guid')
            if guid:
                # 如果存在，就是修改，加入(行，start，len)
                ...
            else:
                # 如果不存在，就是新建数据 , 就是文件
                ...

    # 清除内存中的字节流数据
    del RAW_DATA_DICT[guid]
    return {'status':200}




if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)

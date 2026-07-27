from pathlib import Path

from fastapi import APIRouter,Body
from main import Session
router = APIRouter(
    prefix="/doansys",       # 可选：为该模块所有路径加前缀
    tags=["export"],        # 可选：Swagger 文档分组
    responses={404: {"description": "Not found"}},
)

@router.post("/start/")
def doansys(request:dict=Body(...)):
    # 读取传过来的所有参数，去数据库中查询对应原始文本的其实位置等
    data_list = request.get('params')
    file_path = Path("sdalkdjaljwq11231l/dianpian.txt")
    changes = [
        # (20, 11, 4, 0.22),
        # (25, 9, 5, 4000),
        # (49, 6, 1, 20),
        # (49, 14, 3, 330)
    ]
    with Session() as session:
        for param_data in data_list:
            param_instance = session.query(guid=param_data['guid']).one()
            res = (10,2,5,12)
            changes.append(res)

    with file_path.open("r", encoding="utf-8", newline="") as file:
        lines = file.read()
        all_data = lines.splitlines()
    # # 同一行有多个修改时，从右向左处理，避免前面的修改导致位置偏移 # 这还是有问题
    changes.sort(key=lambda item: (item[0], item[1]), reverse=True)
    print(changes)
    for line_number, start_col, len_col, new_value in changes:
        if not 1 <= line_number <= len(all_data):
            raise IndexError(f"第 {line_number} 行不存在")
        content = all_data[line_number - 1]
        print('修改前:', content)
        # 用户给出的列号从1开始；Python字符串下标从0开始
        start_index = start_col - 1
        end_index = start_index + len_col
        old_value = content[start_index:end_index]
        content = (
                content[:start_index]
                + str(new_value)
                + content[end_index:]
        )
        all_data[line_number - 1] = content
        print('修改后:', content)
    new_path = file_path.with_stem(file_path.stem + "_temp")

    with new_path.open("w", encoding="utf-8", newline="") as file:
        file.writelines([line + "\n" for line in all_data])
    print("修改完成")

    return {'status':'开始训练'}

def save_file(byte_data,filename,recodetype='utf-8'):
    # 将所有数据转换成utf-8
    lines = byte_data.decode(recodetype)
    all_data = lines.splitlines()
    with filename.open("w", encoding="utf-8", newline="") as file:
        file.writelines([line + "\n" for line in all_data])
    print("修改完成")
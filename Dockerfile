## 基础镜像py3.9+linux
FROM ludotech/python3.9-poetry:latest

## 把当前文件夹里的文件构建到镜像的/app目录下
ADD . /app

## 指定默认工作目录为/app目录
WORKDIR /app

## 修改C:\Users{username}\AppData\Roaming\pip\pip.ini文件，指定镜像源加速和pip缓存不用每次都重复下载
RUN pip install --cache-dir="D:\pip-cache" -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

## 镜像启动后统一执行 sh run.sh
CMD ["sh", "run.sh"]
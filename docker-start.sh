#!/bin/bash

#mkdir /var/gxcg-spider/output
#mkdir /var/gxcg-spider/data/sqlite3
#mkdir /var/gxcg-spider/templates
#mkdir /var/gxcg-spider/static

docker rm -f gxcg-spider
image=registry.cn-hangzhou.aliyuncs.com/handsomestwei/gxcg-spider:1.0.0
docker pull $image
## 指定root用户运行，映射端口和目录
docker run -d --name gxcg-spider --user root -p 8765:8765 -it \
-v /var/gxcg-spider/output/:/app/output \
-v /var/gxcg-spider/data/sqlite3/:/app/data/sqlite3 \
-v /var/gxcg-spider/templates/:/app/templates \
-v /var/gxcg-spider/static/:/app/static \
$image
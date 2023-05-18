docker login --username=handsomestwei registry.cn-hangzhou.aliyuncs.com
## win环境下登录报tty错误时添加winpty前缀
#winpty docker login --username=handsomestwei registry.cn-hangzhou.aliyuncs.com

## 阿里云镜像仓库的镜像，标签命名必须是/命名空间/仓库:[版本号]
docker build -t registry.cn-hangzhou.aliyuncs.com/handsomestwei/gxcg-spider:1.0.0 .

## 本地验证
docker run -d --name gxcg-spider --user root -p 8765:8765 -it registry.cn-hangzhou.aliyuncs.com/handsomestwei/gxcg-spider:1.0.0

## 推送到镜像仓库
docker push registry.cn-hangzhou.aliyuncs.com/handsomestwei/gxcg-spider:1.0.0
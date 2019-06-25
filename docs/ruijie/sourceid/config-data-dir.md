## 设置数据存储目录

MongoDB和RocketMQ都需要持久化保存数据，默认存储路径如下：

- MongoDB数据库文件：`/ruijie/ruijie-sourceid/mongodb/data`
- RocketMQ数据文件：`/ruijie/ruijie-sourceid/rocketmq/data`
- RocketMQ日志文件：`/ruijie/ruijie-sourceid/rocketmq/log`

其中`ruijie-sourceid`是K8s命名空间。

数据保存路径可以通过修改配置文件来调整，假设数据保存路径需要改到以下位置：

- MongoDB数据库文件：`/mnt/mongodb/data`
- RocketMQ数据文件：`/mnt/rocketmq/data`
- RocketMQ日志文件：`/mnt/rocketmq/log`

修改`/opt/kad/workspace/ruijie-sourceid/conf/all.yml`文件，设置以下参数：
```
mongodb_data_dir: "/mnt/mongodb/data"
rocketmq_data_dir: "/mnt/rocketmq/data"
rocketmq_logs_dir: "/mnt/rocketmq/log"
```

**注意：设数据保存路径只能在部署SourceID前修改，部署后再修改不会生效**

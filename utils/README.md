# utils

本Python包主要包含后端和AI代码的成果。

## ai 子包

AI功能的实现，主要包括对于简答题的批改和答疑功能的实现。

## database 子包

服务于后端的数据库包，主要包括数据库各表的数据模型。

使用`sqlalchemy`包实现。

## auth 模块

编写了一个函数：`get_userid_with_sessionid`，以服务于API实现中查询当前登录用户的userid的需求。

## config 模块

实现对项目根目录下`custom_config.toml`中保存的有关配置的读取，将配置文件对象化，以配合IDE自动补全减少因输入错误造成的BUG。

`custom_config.toml`包括了诸如SessionID有效时长、数据库地址链接、AI服务Token等内容。故不会上传到Github仓库中。
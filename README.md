# ATA·学习岛

[本项目要求于此](./static/course/高阶.md)

[前期课程资料于此](https://github.com/the-real-jushen/aiSummerCamp2025)


## 1. 项目分工安排

按照一般Web应用的开发分工方式，结合本项目特点，本项目开发人员分工如下：

1. 前端开发：2人，代码主要位于`/static`
2. 后端开发：2人，代码主要位于`/api`和`/utils`
3. AI开发：1人，代码主要位于`/utils/ai`

## 2. 项目使用技术

### 2.1 前端

传统的HTML/CSS/JavaScript开发。

### 2.2 后端

1. FastAPI：用于编写API的包。
2. Uvicorn: 启动Web服务的包。
3. SQLAlchemy：数据库操作的包。
4. BCrypt：用于加密用户密码的包。

### 2.3 AI

使用SiliconFlow平台的API。
使用Python的requests库直接请求。

## 3. 项目结构

### 3.1 api包

主要存放了后端API接口的实现。

包内部结构请参照[api包内README.md](./api/README.md)。

### 3.2 data文件夹

存放服务运行产生的数据，例如Sqlite3数据库。

后期如果拓展开发头像功能，用户上传的头像图片也可置于此处。

因此，本文件夹不会上传到Github仓库中。

> 请在部署时，创建`data`文件夹，以及其子文件夹`avatar`。

### 3.3 static文件夹

前端页面入口位于`/static/index.html`。

前端及其所需静态资源的存放处。也包括了内置课程的相关资料。

### 3.4 utils包

包括后端开发根据需要编写的一部分代码和AI开发实现的功能。

内部结构请参照[utils包内部README.md](./utils/README.md)

### 3.5 app模块

服务于此启动。

注：实际应用中应调整`uvicorn.run`的参数使之启动HTTPS服务。具体原因在[api包内README.md](./api/README.md)中有所陈述。

## 4. 项目运行

我们假定您具有基础的工具，如`git`。

### 4.1 前置安装

安装uv。参考[官方文档](https://docs.astral.sh/uv/getting-started/installation/)。

### 4.2 克隆代码

运行以下命令。
```shell
git clone https://github.com/z5ar/AITeachingAI.git
cd ./AITeachingAI
uv sync
```
### 4.3 配置项目

在项目根目录新建`data`文件夹。
在`data`文件夹下新建`avatar`文件夹。

在项目根目录下创建文件`custom_config.toml`，按照以下模板编写您的配置。
```toml
[database]
# 填写您的数据库地址，这里使用的是项目根目录下的data/database.db数据库。
url = 'sqlite:///data/database.db' 

[sessionid]
# SessionID超时时间，以秒为单位，此处为一周。决定了用户登录后的超时时间。
ttl = 604_800

[ai]
# 您的AI服务Token。
token = ''
```

按照您的需求修改`app.py`中`uvicorn.run`的参数，以使用HTTPS等功能。

### 4.4 启动服务

在项目根目录中，运行以下指令。
```shell
uv run app.py
```
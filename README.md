# 千AI＊万师


~~私のスライドを見てください。~~

~~<p align='right'>——你的AI老师</p>~~

~~Ciallo～(∠・ω< )⌒★~~

~~<p align='right'>——你的AI助教</p>~~

**以上为整活，还请大家集思广益如何正经地写一写~**

[本项目要求于此](./static/course/高阶.md)

[前期课程资料于此](https://github.com/the-real-jushen/aiSummerCamp2025)

## 0. 写与项目成员

**交作业时此部分将删除。**

如果看不懂我写了啥可以不用读，由我来整合各位的成果就好。

各位只需要将代码放在各自的文件夹里即可。

前端放在`/static`文件夹中，AI放在`/utils/ai`文件夹中。

这份代码的根分支名称叫做`trunk`。

如何使用这份代码？

假定你们具有基础的工具，如`git`。

### 0.1 前置安装

安装uv。参考[这里](https://docs.astral.sh/uv/getting-started/installation/)。

### 0.2 部署项目

运行以下命令。
```shell
git clone https://github.com/z5ar/AITeachingAI.git
cd ./AITeachingAI
uv sync
```
### 4.3 配置项目

在项目根目录下创建文件`custom_config.toml`，直接将以下内容复制进去。
```toml
[database]
# 填写您的数据库地址，这里使用的是项目根目录下的data/database.db数据库。
url = 'sqlite:///data/database.db' 

[sessionid]
# SessionID超时时间，以秒为单位，此处为一周。
ttl = 604_800

[ai]
# 您的AI服务Token。
token = ''
```

### 4.4 启动服务

在项目根目录中，运行以下指令，即可运行服务。
```shell
uv run app.py
```

前端注意：
1. 在浏览器中输入`http://localhost:8000/docs`即可查看后端提供的API接口。需要新接口尽管提，我现在空余时间充裕。
2. 在浏览器中输入`http://localhost:8000/`就是前端的首页，对应的是`static`文件夹下的`index.html`。

## 1. 项目分工安排

按照一般Web应用的开发分工方式，结合本项目特点，本项目开发人员分工如下：

1. 前端开发：2人，代码主要位于`/static`
2. 后端开发：2人，代码主要位于`/api`和`/utils`
3. AI开发：1人，代码主要位于`/utils/ai`

## 2. 项目使用技术

### 2.1 前端

请前端开发填写。

### 2.2 后端

1. FastAPI：用于编写API的包。
2. Uvicorn: 启动Web服务的包。
3. SQLAlchemy：数据库操作的包。
4. BCrypt：用于加密用户密码的包。

### 2.3 AI

请AI开发填写。

## 3. 项目结构

### 3.1 api包

主要存放了后端API接口的实现。

包内部结构请参照[api包内README.md](./api/README.md)。

### 3.2 data文件夹

存放服务运行产生的数据，例如Sqlite3数据库。

后期如果拓展开发头像功能，用户上传的头像图片也可置于此处。

因此，本文件夹不会上传到Github仓库中。

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

### 4.2 部署项目

运行以下命令。
```shell
git clone https://github.com/z5ar/AITeachingAI.git
cd ./AITeachingAI
uv sync
```
### 4.3 配置项目

在项目根目录下创建文件`custom_config.toml`，按照以下模板编写您的配置。
```toml
[database]
# 填写您的数据库地址，这里使用的是项目根目录下的data/database.db数据库。
url = 'sqlite:///data/database.db' 

[sessionid]
# SessionID超时时间，以秒为单位，此处为一周。
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
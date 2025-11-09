# 千AI＊万师


~~私のスライドを見てください。~~

~~<p align='right'>——你的AI老师</p>~~

~~Ciallo～(∠・ω< )⌒★~~

~~<p align='right'>——你的AI助教</p>~~

**以上为整活，还请大家集思广益如何正经地写一写~**

[本项目要求于此](./static/course/高阶.md)

[前期课程资料于此](https://github.com/the-real-jushen/aiSummerCamp2025)

## 0. 写与项目成员
前端完善：
[] 学习报告
[] AI询问
[] 课程选择页
[] 保存进度的评判记录


**交作业时此部分将删除。**

当下需要解决的问题：

1. AI需不需要对台词进行改写

2. AI答疑的参数
    让AI答疑的时候，上下文该怎么传递。
    - AI有限额
    - Web 数据包过大，性能不行
    - 传的数据多的话，AI思考时间会变长

    已有的AI代码，只传问题，没有上下文。
    “这里的XXX是什么意思” 这种问题就没法解决了
    
3. 到底用什么AI平台
    老师说可以问他要限额。
    用什么平台都还没决定。

4. AI教师怎么设计？
    要不要像提交的代码一样，搞一些人设之类的东西。
    
5. 脚本的格式。
```json
[
    {
        "type": "text",
        "content": "bla bla",
        "ppt": "/static/ppt/",
        "note": ""
    },
    {
        "type": "video",
        "content": "https://...",
        "description": "这个视频讲了什么。"
    },
    {
        "type": "problem",
        "content": {"problem_id":1}
    },
    {
        "type": "interaction",
        "content": "xxxx?"
    }
]
```

6. 学习报告
    - 出现的时机
        - 小节末
        - 章节末
        - 课程末
    - 包含的内容
        - 小节末
            - 学习时长
            - 互动
            - 测验
            - 打分
            - 评语
            - ~~老师好感度~~
        - 作业小节末
            - 分数
            - 评语
        - 章末
            - 汇总一下上面的内容
        - 课程末
            - 汇总一下所有内容


7. 报告、PPT的分工。
    一个人可能做不太来。
    - 报告：原理性
    - PPT：展示，女同志

8. 最大的问题：
    项目还没有做完
    时间紧迫

9. 交流问题：
    交流太少，职责之间对接差异大。
    最后一周，加把劲。

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
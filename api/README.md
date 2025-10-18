# API接口

这里是后端的主要工作，包括身份认证、课程相关信息获取、批改作业等API，主要使用FastAPI实现。

## API简介

下面陈列的是对于API功能的简要介绍。后端代码对FastAPI的自动docs生成做了特意编写，故具体API的用法可以在运行服务后使用该docs文档。

### 1. 身份认证API `/api/auth`

#### 1.1 `POST /api/auth/register`: 用户注册

传入用户名及密码，注册一个用户，以进行后续操作。

原理上传递的密码在后端经过bcrypt加密后存入数据库，保障即使数据库泄露也不会暴露用户的明文密码。

设计上，本接口传输的是明文密码，实际应用中，理应使用HTTPS进行传输，这样配合前述的密码bcrypt加密可保障用户的密码安全。但**为了方便，在app.py中默认启动的是HTTP服务**。

#### 1.2. `POST /api/auth/login`：用户登录

传入用户名和密码，进行用户的登录。

使用浏览器Cookies保存SessionID，对于前端是无感的。

#### 1.3. `POST /api/auth/logout`：用户登出

无需前端传递任何参数，实现用户的退出登录。

原理上使用了1.2所述Cookies中保存的SessionID。

#### 1.4. `POST /api/auth/unregister`：用户删除

必须在用户既登录的状态下操作，传入用户名和密码，以删除用户账户。

原理上采取了软删除措施，即数据库中给既删除的账户添加一个`deleted_at`字段，标记其已删除，而非直接彻底删除账户数据。有助于恢复数据。

### 2. 课程相关API `/api/lesson`

#### 2.1 获取所有课程 `GET /api/lesson/course/getAll`

获取所有课程列表。

设计上使用`/course/getAll`二级路径是为了可扩展性，后续可以加入用户添加课程的功能。但为了简化问题，此处只实现了获取系统内置课程的功能。

#### 2.2 获取课程所有小节 `GET /api/lesson/section/{course_id}/getAll`

获取系统内部ID为`course_id`的课程的所有小节。该ID可以在2.1所述API的响应体中获取。

设计上同2.1所述，后续可扩展用户添加课程小节功能。但为了简化问题，只实现了获取课程章节功能。

#### 2.3 获取当前用户在某小节的学习进度 `GET /api/lesson/progress/{section_id}/get`

获取当前登录用户在系统内部ID为`section_id`的小节的学习进度。该ID可以在2.2所述API中获取。

获取当前登录用户仍旧使用浏览器Cookie中保存的SessionID。

#### 2.4 更改当前用户在某小节的学习进度 `SET /api/lesson/progress/{section_id}/set`

更改当前登录用户在系统内部ID为`section_id`的小节的学习进度记录，对于系统内不存在记录的，新建一条记录。该ID可以在2.2所述API中获取。

获取当前登录用户仍旧使用浏览器Cookie中保存的SessionID。

没有实现学习进度记录的删除功能，因为理论上将学习进度改为0可以等效为学习进度的删除。

### 3. 作业批改API `/api/judge`

系统内部对于题目的定义有五类：

```Python
class ProblemType(Enum):
    single_choice = 'single_choice'
    multiple_choice = 'multiple_choice'
    variable_choice = 'variable_choice'
    blank_filling = 'blank_filling'
    brief_response = 'brief_response'
```

`single_choice`：单项选择题，只能选一个答案的题型。
`multiple_choice`：多项选择题，至少选两个选项的题型。
`variable_choice`：不定项选择题，除了不能选零个答案其他都行的题型。只是后端代码编写者对山东高考生物不定项选择的怨念，实际不需要的话可以删除。
`blank_filling`：填空题，必须回答与参考答案一字不差的题型。
`brief_response`：简答题，准许一定程度的自由发挥的题型，由AI批改的题型~~，得多少分全靠命运~~。

无论要批改的只有一题还是多题，都要传入一个“由系统内部题目ID`problem_id`和学生答案`answer`组成的对象”的列表，以实现对多题批改的兼容。

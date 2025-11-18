# API接口

这里是后端的主要工作，包括身份认证、课程相关信息获取、批改作业等API，主要使用FastAPI实现。

## API简介

下面陈列的是对于API功能的简要介绍。后端代码对FastAPI的自动docs生成做了特意编写，故具体API的用法可以在运行服务后使用该docs文档。

---

### 1. 身份认证API `/api/auth`

- `POST /api/auth/register`：用户注册，明文密码经bcrypt加密存储。
- `POST /api/auth/login`：用户登录，返回SessionID存于Cookie。
- `POST /api/auth/logout`：用户登出，清除SessionID。
- `POST /api/auth/unregister`：用户删除，软删除账户（加deleted_at字段）。
- `POST /api/auth/repasswd`：修改密码。

> 生产环境中因为涉及到密码传输建议使用HTTPS，开发时默认使用HTTP仅为方便调试。

---

### 2. 课程与学习进度API `/api/lesson`

- `GET /api/lesson/course/getAll`：获取所有课程列表。
- `GET /api/lesson/section/{course_id}/getAll`：获取指定课程的所有小节。
- `GET /api/lesson/progress/{section_id}/get`：获取当前用户在某小节的学习进度。
- `POST /api/lesson/progress/{section_id}/set`：更改/新建当前用户在某小节的学习进度。

#### 教师AI相关
- `POST /api/lesson/teacher/startSection/{section_id}`：开始小节，返回AI教师的首步内容。
- `POST /api/lesson/teacher/next_step`：获取AI教师的下一步内容。
- `POST /api/lesson/teacher/judge`：判定简答题，支持标准答案、满分、评语。
- `POST /api/lesson/teacher/report`：生成学习报告，传入学习时长与判题明细。
- `POST /api/lesson/teacher/answer`：答疑接口，传入问题与当前对话context，返回AI教师回答。

---

### 3. 问题相关API `/api/problem`

- `POST /api/problem/get`：批量获取题目内容（支持多题ID）。
- `POST /api/problem/judge`：批量判分（选择题/填空题/多选题/简答题，自动区分题型）。
- `POST /api/problem/judge/interaction`：判定互动题（特殊类型，返回标准答案与评语）。

---

### 4. 个人信息API `/api/profile`

- `GET /api/profile/whoami`：获取当前用户个人信息（昵称、头像、主题色等）。
- `POST /api/profile/iamwho`：修改个人信息（昵称、头像、主题色）。

---

### 5. 答疑API `/api/qanda`

- `POST /api/qanda/`：AI答疑（接口预留，具体参数和返回值待完善）。

---

## 说明

- 所有接口均支持自动文档（Swagger UI），可通过 `/docs` 路径访问。
- 用户身份通过SessionID自动管理，前端无需手动传递。
- 课程、章节、题目、进度等均有详细的数据模型和示例，便于前后端联调。
- 教师AI相关接口支持个性化教学流程、自动判题、学习报告生成和答疑。

---

> 如需扩展更多功能（如课程自定义、题库管理、成绩统计等），可参考现有API风格进行开发。

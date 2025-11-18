# AI 教师模块说明

本模块用于实现“AI教师”角色，支持脚本式教学、答疑、判题与学习报告生成，适用于智能化教学场景。

## 主要文件
- `teacher.py`：核心实现，定义 AI 教师的抽象基类、具体角色、API客户端等。

## 主要类与结构

### ScriptType & ScriptBase
- `ScriptType`：枚举脚本类型（text、video、problem、interaction）。
- `ScriptBase`/`ScriptInput`/`ScriptOutput`：统一描述教学脚本内容，可包含文本、视频、题目、PPT等。

### StudentProgress
- 跟踪学生学习进度、好感度、学习时长等，支持动态调整。

### SiliconFlowClient
- 封装 SiliconFlow AI API，支持 chat_completion 聊天接口。
- 用于与大模型交互，生成讲解、答疑、判题等内容。

### AITeacher（抽象基类）
- 定义 AI 教师的基本接口：
	- `load_script(script)`：加载教学脚本。
	- `next_script()`：获取下一个教学内容。
	- `answer_question(question, context)`：答疑。
	- `judge_problem(problem, std, ans, mscore, context)`：判题。
	- `generate_report(time_spent, problems)`：生成学习报告。

### MyCharater（具体角色实现）
- 以“15岁怪力少女侦探”为人设，结合脚本内容生成讲解、串场、答疑、判题和报告。
- 支持分段讲解、个性化语气、生活化举例。

## 用法示例
1. 实例化角色：
	 ```python
	 teacher = MyCharater(api_key)
	 teacher.load_script([...])
	 item = teacher.next_script()
	 answer = teacher.answer_question('什么是ADC？', context=3)
	 score, comment = teacher.judge_problem(...)
	 report = teacher.generate_report(time_spent, problems)
	 ```
2. 通过 `get_teacher(uuid, character, api_key)` 获取/复用角色实例。

## 典型流程
- 加载教学脚本（支持文本、视频、题目等多种类型）。
- 逐步生成讲解内容，支持分段输出。
- 支持上下文答疑，自动结合历史对话。
- 判题时自动评分并生成评语。
- 课后自动生成学习报告。

## 扩展说明
- 可自定义角色人设，扩展更多教学风格。
- 支持多角色并发，实例缓存于 `instances` 字典。
- API Key 需为 SiliconFlow 平台有效密钥。

---
如需扩展新角色或功能，请继承 `AITeacher` 并实现相关方法。

# 初始化
teacher = AIResponse("gpt-3.5-turbo", "your-api-key")

# 加载剧本
teacher.load_teaching_script(your_script)

# 进行教学
response = teacher.teach_next_step("student_id")

# 处理学生回答
response = teacher.teach_next_step("student_id", student_answer)

# 自由对话
response = teacher.continue_conversation("student_id", student_message)

# 生成报告
report = teacher.generate_learning_report("student_id")
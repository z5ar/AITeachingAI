# 创建角色协议
character_protocol = ElysiaProtocol()

# 初始化AI教师时传入角色协议
ai_teacher = AIResponse("gpt-3.5-turbo", "your-api-key", character_protocol)

# 或者后期设置角色
ai_teacher.set_role_protocol(character_protocol)
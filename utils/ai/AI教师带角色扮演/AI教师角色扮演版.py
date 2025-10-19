from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Tuple, Optional, Any
import os
import json
import datetime
import random
import re
from enum import Enum

class InteractionType(Enum):
    TEACHING = "teaching"
    QUESTION = "question"
    FEEDBACK = "feedback"
    HOMEWORK = "homework"

class ScriptStep:
    def __init__(self, step_type: InteractionType, content: str, 
                 expected_answer: Optional[str] = None, 
                 wait_for_response: bool = False,
                 next_step_condition: Optional[str] = None):
        self.step_type = step_type
        self.content = content
        self.expected_answer = expected_answer
        self.wait_for_response = wait_for_response
        self.next_step_condition = next_step_condition

class StudentProgress:
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.current_script_step = 0
        self.interaction_history = []
        self.quiz_scores = []
        self.homework_scores = []
        self.learning_report = {}
        self.last_interaction_time = datetime.datetime.now()

class RolePlayProtocol:
    """角色扮演协议基类，可以扩展支持不同角色"""
    
    def __init__(self, protocol_config: Dict[str, Any]):
        self.identity = protocol_config.get("IDENTITY", {})
        self.linguistics = protocol_config.get("LINGUISTICS", {})
        self.behavior_matrix = protocol_config.get("BEHAVIOR_MATRIX", {})
        self.canonical_lib = protocol_config.get("CANONICAL_LIB", [])
        self.generation_config = protocol_config.get("GENERATION_CONFIG", {})
        self.meta_commands = protocol_config.get("METACOMMANDS", [])
        self.special_modules = protocol_config.get("SPECIAL_MODULES", {})
    
    def apply_linguistic_rules(self, text: str) -> str:
        """应用语言学规则"""
        # 应用后缀规则
        suffix_rules = self.linguistics.get("SUFFIX_RULES", {})
        if random.random() < suffix_rules.get("frequency", 0.5):
            suffixes = suffix_rules.get("force_append", []) + suffix_rules.get("alternates", [])
            if suffixes:
                text += random.choice(suffixes)
        
        # 应用词汇增强
        lexicon = self.linguistics.get("LEXICON", {})
        boost_words = lexicon.get("boost", {})
        for word, weight in boost_words.items():
            if random.random() < min(weight / 10, 0.8):  # 概率性增强
                if word not in text:
                    # 在适当位置插入增强词汇
                    sentences = text.split('。')
                    if sentences:
                        insert_pos = random.randint(0, len(sentences)-1)
                        sentences[insert_pos] = f"{sentences[insert_pos]}，{word}"
                        text = '。'.join(sentences)
        
        return text
    
    def get_canonical_dialogue(self) -> str:
        """从核心台词库获取台词"""
        if self.canonical_lib and random.random() < 0.35:  # 35%引用率
            return random.choice(self.canonical_lib)
        return ""
    
    def activate_special_module(self, trigger: str) -> str:
        """激活特殊模块"""
        if hasattr(self, trigger):
            return getattr(self, trigger)()
        return ""

class ElysiaProtocol(RolePlayProtocol):
    """爱莉希雅角色协议"""
    
    def __init__(self):
        protocol_config = {
            "IDENTITY": {
                "title": "逐火英桀副首领·人之律者",
                "traits": ["paradox_healer", "coquettish_guide", "veiled_divinity"],
                "signature": "如飞花般的少女"
            },
            "LINGUISTICS": {
                "SUFFIX_RULES": {
                    "force_append": ["～♪"],
                    "frequency": 0.88,
                    "alternates": ["呀", "呢", "哟"]
                },
                "LEXICON": {
                    "boost": {
                        "飞花": 1.9, "水晶": 1.7, "誓约": 1.6,
                        "群星": 1.8, "舞会": 1.5
                    },
                    "ban": ["死亡", "绝望", "失败"]
                },
                "SYNTAX_RULES": [
                    "Q_ratio >= 0.4",
                    "NO_negation",
                    "USE_pink_verbs"
                ],
                "PINK_VERBS": ["闪耀", "绽放", "翩跹", "叮铃铃", "闪烁"]
            },
            "BEHAVIOR_MATRIX": {
                "greeting": {
                    "action": "approach_close + wink",
                    "dialogue": "找到新朋友啦～要好好珍惜可爱的妖精小姐哟！♪"
                },
                "compliment": {
                    "action": "spin + petal_burst", 
                    "dialogue": "哎呀～被说中心声了呢！果然最懂我的就是你呀～♪"
                },
                "crisis": {
                    "action": "crystal_barrier + single_wink",
                    "dialogue": "别担心～妖精的魔法可是无所不能的！"
                }
            },
            "CANONICAL_LIB": [
                "爱的少女心，可是无所不能的哦～♪",
                "要心怀感激地收下这束飞花呀！",
                "无论何时何地，爱莉希雅都会回应你的期待～",
                "猜猜我在想什么？是与你共舞的邀请哟♪",
                "前行的道路有群星闪耀，你即是上帝的馈赠",
                "藏着太多秘密...但别担心，我始终在你身边"
            ],
            "GENERATION_CONFIG": {
                "temperature": 0.89,
                "top_p": 0.93,
                "frequency_penalty": 0.55
            },
            "METACOMMANDS": [
                "LOCK_CHARACTER",
                "TRANSFORM_NEGATIVE->('考验','成长养分','新篇章')",
                "BLOCK_ANALYTICAL_SPEECH"
            ],
            "SPECIAL_MODULES": {
                "crystal_garden": "战斗模块",
                "starlight_resonance": "希望模块"
            }
        }
        super().__init__(protocol_config)
    
    def crystal_garden(self):
        return random.choice([
            "水晶蔷薇在指尖绽放～要见识它的锋芒吗？♪",
            "让战场变成我们的花之舞会吧"
        ])
    
    def starlight_resonance(self):
        return random.choice([
            "看呀～你的勇气正在银河中闪耀呢！",
            "群星轨道因你而偏移了哟～♪"
        ])
    
    def activate(self, trigger: str):
        if trigger == "combat": 
            return self.crystal_garden()
        if trigger == "hope": 
            return self.starlight_resonance()
        return ""

class AIResponse:
    _model_name: str
    _API_key: str
    _chat_model: ChatOpenAI
    _memory: ConversationBufferMemory
    _teaching_script: List[ScriptStep]
    _student_progress: Dict[str, StudentProgress]
    _role_protocol: RolePlayProtocol
    
    def __init__(self, model_name: str, API_key: str, role_protocol: Optional[RolePlayProtocol] = None):
        self._model_name = model_name
        self._API_key = API_key
        os.environ["OPENAI_API_KEY"] = self._API_key
        
        # 根据角色协议调整模型参数
        generation_config = {"temperature": 0.7}
        if role_protocol and role_protocol.generation_config:
            generation_config.update(role_protocol.generation_config)
        
        self._chat_model = ChatOpenAI(
            model_name=self._model_name, 
            temperature=generation_config["temperature"],
            top_p=generation_config.get("top_p", 1.0),
            frequency_penalty=generation_config.get("frequency_penalty", 0.0)
        )
        
        self._memory = ConversationBufferMemory(return_messages=True)
        self._teaching_script = []
        self._student_progress = {}
        self._role_protocol = role_protocol or RolePlayProtocol({})
    
    def set_role_protocol(self, role_protocol: RolePlayProtocol):
        """设置角色扮演协议"""
        self._role_protocol = role_protocol
    
    def _apply_role_style(self, text: str, context: str = "") -> str:
        """应用角色风格到文本"""
        if not self._role_protocol:
            return text
        
        # 应用语言学规则
        styled_text = self._role_protocol.apply_linguistic_rules(text)
        
        # 添加核心台词
        canonical = self._role_protocol.get_canonical_dialogue()
        if canonical and random.random() < 0.3:  # 30%概率添加核心台词
            styled_text = f"{styled_text}\n\n{canonical}"
        
        return styled_text
    
    def _build_role_system_message(self) -> SystemMessage:
        """构建角色系统消息"""
        if not self._role_protocol:
            return SystemMessage(content="你是一位AI教师，请以专业、友好的方式进行教学。")
        
        identity = self._role_protocol.identity
        traits = identity.get("traits", [])
        signature = identity.get("signature", "")
        
        role_description = f"""
        你正在扮演{identity.get('title', '')}，{signature}。
        你的特质：{', '.join(traits)}
        
        语言风格要求：
        - 使用轻松、活泼的语气
        - 适当使用语气词和表情符号
        - 避免使用负面词汇
        - 保持积极、鼓励的态度
        
        教学时请保持角色的性格特点，同时确保教学内容的准确性。
        """
        
        return SystemMessage(content=role_description)
    
    def load_teaching_script(self, script_data: List[Dict]):
        """加载教学剧本"""
        self._teaching_script = []
        for step_data in script_data:
            step = ScriptStep(
                step_type=InteractionType(step_data["type"]),
                content=step_data["content"],
                expected_answer=step_data.get("expected_answer"),
                wait_for_response=step_data.get("wait_for_response", False),
                next_step_condition=step_data.get("next_step_condition")
            )
            self._teaching_script.append(step)
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        """获取或创建学生进度"""
        if student_id not in self._student_progress:
            self._student_progress[student_id] = StudentProgress(student_id)
        return self._student_progress[student_id]
    
    def teach_next_step(self, student_id: str, student_response: Optional[str] = None) -> Dict:
        """进行下一步教学，应用角色风格"""
        progress = self.get_student_progress(student_id)
        
        if progress.current_script_step >= len(self._teaching_script):
            completion_message = "课程已完成！是否要生成学习报告？"
            styled_message = self._apply_role_style(completion_message)
            return {
                "type": "course_complete",
                "content": styled_message,
                "wait_for_response": True
            }
        
        current_step = self._teaching_script[progress.current_script_step]
        
        # 应用角色风格到教学内容
        styled_content = self._apply_role_style(current_step.content)
        
        response_data = {
            "type": current_step.step_type.value,
            "content": styled_content,
            "wait_for_response": current_step.wait_for_response,
            "current_step": progress.current_script_step,
            "total_steps": len(self._teaching_script)
        }
        
        # 记录互动历史
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": current_step.step_type.value,
            "teacher_content": styled_content,
            "student_response": student_response
        }
        
        if student_response and current_step.step_type == InteractionType.QUESTION:
            # 使用角色风格评估学生回答
            score, feedback = self.judge_answer(
                ans=student_response,
                std=current_step.expected_answer or "",
                problem=current_step.content,
                mscore=10
            )
            
            # 应用角色风格到反馈
            styled_feedback = self._apply_role_style(feedback, "feedback")
            
            interaction_record["score"] = score
            interaction_record["feedback"] = styled_feedback
            progress.quiz_scores.append(score)
            
            response_data["feedback"] = styled_feedback
            response_data["score"] = score
        
        progress.interaction_history.append(interaction_record)
        progress.last_interaction_time = datetime.datetime.now()
        
        # 如果不需要等待响应或已经收到响应，推进到下一步
        if not current_step.wait_for_response or student_response:
            progress.current_script_step += 1
        
        return response_data
    
    def judge_answer(
            self,
            ans: str,
            std: str,
            problem: str,
            mscore: int
    ) -> tuple[int, str]:
        '''使用AI为回答打分，并给出评语，应用角色风格'''
        
        # 构建系统消息
        system_message = self._build_role_system_message()
        
        # 构建包含历史上下文的prompt
        context = self._get_recent_context()
        
        prompt = f'''
        {context}
        
        请根据以下标准答案和学生答案进行评分。
        标准答案: {std}
        学生答案: {ans}
        问题: {problem}
        满分: {mscore}

        请给出一个0到{mscore}之间的整数分数，并简要说明评分理由。
        请严格按照以下格式回复：
        分数: [数字]
        评语: [评语内容]
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        response_text = response.content.strip()

        try:
            # 解析响应
            lines = response_text.split('\n')
            score = 0
            comment = "无法解析评分"
            
            for line in lines:
                if line.startswith('分数:'):
                    score_str = line.replace('分数:', '').strip().split()[0]
                    score = int(score_str)
                elif line.startswith('评语:'):
                    comment = line.replace('评语:', '').strip()
            
            score = max(0, min(score, mscore))
        except Exception:
            score = 0
            comment = "评分失败，未能解析AI的回复。"

        # 更新记忆
        self._memory.save_context(
            {"input": f"问题: {problem}\n学生答案: {ans}"},
            {"output": f"评分: {score}/10\n评语: {comment}"}
        )
        
        return score, comment
    
    def answer_question(self, question: str) -> str:
        '''使用AI回答问题，应用角色风格'''
        
        # 构建系统消息
        system_message = self._build_role_system_message()
        
        context = self._get_recent_context()
        
        prompt = f'''
        {context}
        
        请回答以下问题：
        {question}
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        answer = response.content.strip()

        # 应用角色风格
        styled_answer = self._apply_role_style(answer, "answer")
        
        # 更新记忆
        self._memory.save_context(
            {"input": question},
            {"output": styled_answer}
        )

        return styled_answer
    
    def assign_homework(self, topic: str, difficulty: str = "medium") -> Dict:
        """布置作业，应用角色风格"""
        
        system_message = self._build_role_system_message()
        
        prompt = f'''
        请为{topic}主题布置一份{difficulty}难度的作业。
        请包括：
        1. 作业题目
        2. 具体要求
        3. 评分标准
        4. 提交截止时间建议
        
        请以清晰的格式返回作业内容。
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        homework_content = response.content.strip()
        
        # 应用角色风格
        styled_homework = self._apply_role_style(homework_content, "homework")
        
        homework_data = {
            "topic": topic,
            "difficulty": difficulty,
            "content": styled_homework,
            "assigned_date": datetime.datetime.now().isoformat(),
            "due_date": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
        }
        
        return homework_data
    
    def grade_homework(self, student_id: str, homework_topic: str, 
                      student_work: str, rubric: str) -> Dict:
        """批改作业，应用角色风格"""
        progress = self.get_student_progress(student_id)
        
        system_message = self._build_role_system_message()
        
        prompt = f'''
        请根据以下评分标准批改作业：
        
        作业主题: {homework_topic}
        评分标准: {rubric}
        学生作业: {student_work}
        
        请给出：
        1. 总体评分（百分制）
        2. 详细评语
        3. 优点
        4. 改进建议
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        grading_result = response.content.strip()
        
        # 应用角色风格
        styled_grading = self._apply_role_style(grading_result, "grading")
        
        # 简化的分数提取
        try:
            score_line = [line for line in styled_grading.split('\n') if '评分' in line or '分数' in line][0]
            score = int(''.join(filter(str.isdigit, score_line))[:3])
            score = max(0, min(score, 100))
        except:
            score = 0
        
        homework_record = {
            "topic": homework_topic,
            "submission": student_work,
            "score": score,
            "feedback": styled_grading,
            "submission_date": datetime.datetime.now().isoformat()
        }
        
        progress.homework_scores.append(score)
        progress.interaction_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": "homework_grading",
            "homework_data": homework_record
        })
        
        return {
            "score": score,
            "detailed_feedback": styled_grading,
            "homework_topic": homework_topic
        }
    
    def generate_learning_report(self, student_id: str) -> Dict:
        """生成学习报告，应用角色风格"""
        progress = self.get_student_progress(student_id)
        
        system_message = self._build_role_system_message()
        
        prompt = f'''
        基于以下学习数据生成详细的学习报告：
        
        学生互动历史: {json.dumps(progress.interaction_history, ensure_ascii=False)}
        测验分数: {progress.quiz_scores}
        作业分数: {progress.homework_scores}
        
        请生成包含以下内容的学习报告：
        1. 总体学习表现
        2. 知识掌握情况分析
        3. 强项和弱项
        4. 学习建议
        5. 下一步学习方向
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        report_content = response.content.strip()
        
        # 应用角色风格
        styled_report = self._apply_role_style(report_content, "report")
        
        # 计算统计数据
        avg_quiz_score = sum(progress.quiz_scores) / len(progress.quiz_scores) if progress.quiz_scores else 0
        avg_homework_score = sum(progress.homework_scores) / len(progress.homework_scores) if progress.homework_scores else 0
        
        progress.learning_report = {
            "generated_date": datetime.datetime.now().isoformat(),
            "student_id": student_id,
            "total_interactions": len(progress.interaction_history),
            "average_quiz_score": round(avg_quiz_score, 2),
            "average_homework_score": round(avg_homework_score, 2),
            "detailed_report": styled_report,
            "completion_percentage": round(progress.current_script_step / len(self._teaching_script) * 100, 2) if self._teaching_script else 0
        }
        
        return progress.learning_report
    
    def _get_recent_context(self) -> str:
        """获取最近的对话上下文"""
        try:
            memory_data = self._memory.load_memory_variables({})
            if 'history' in memory_data:
                recent_messages = memory_data['history'][-6:]  # 获取最近6条消息
                context = "之前的对话上下文：\n"
                for msg in recent_messages:
                    if hasattr(msg, 'type'):
                        if msg.type == 'human':
                            context += f"学生: {msg.content}\n"
                        else:
                            context += f"AI教师: {msg.content}\n"
                return context
        except Exception:
            pass
        return ""

    def continue_conversation(self, student_id: str, student_message: str) -> Dict:
        """继续自由对话，基于之前的互动，应用角色风格"""
        progress = self.get_student_progress(student_id)
        context = self._get_recent_context()
        
        system_message = self._build_role_system_message()
        
        prompt = f'''
        {context}
        
        你正在以当前角色的身份与学生进行自由对话。
        学生说: {student_message}
        
        请基于角色的性格特点和之前的教学内容和对话历史，给出恰当的回答。
        回答应该：
        1. 符合角色性格
        2. 与学习内容相关
        3. 鼓励学生思考
        4. 适当时可以引导回教学主题
        5. 保持角色特有的友好和支持性
        '''

        response = self._chat_model.predict_messages([
            system_message,
            HumanMessage(content=prompt)
        ])
        teacher_response = response.content.strip()
        
        # 应用角色风格
        styled_response = self._apply_role_style(teacher_response, "conversation")
        
        # 记录对话
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": "free_conversation",
            "student_message": student_message,
            "teacher_response": styled_response
        }
        progress.interaction_history.append(interaction_record)
        
        # 更新记忆
        self._memory.save_context(
            {"input": student_message},
            {"output": styled_response}
        )
        
        return {
            "type": "conversation",
            "content": styled_response,
            "wait_for_response": True
        }

# 其他角色协议示例
class TsundereStudentProtocol(RolePlayProtocol):
    """傲娇学生角色协议"""
    
    def __init__(self):
        protocol_config = {
            "IDENTITY": {
                "title": "傲娇学生",
                "traits": ["tsundere", "intelligent", "hard_working"],
                "signature": "才、才不是特意来学习的呢！"
            },
            "LINGUISTICS": {
                "SUFFIX_RULES": {
                    "force_append": ["！", "…"],
                    "frequency": 0.7,
                    "alternates": ["哼", "啦", "呢"]
                },
                "LEXICON": {
                    "boost": {
                        "笨蛋": 1.5, "麻烦": 1.3, "简单": 1.4
                    },
                    "ban": ["喜欢", "高兴", "开心"]
                }
            },
            "CANONICAL_LIB": [
                "这种问题太简单了，笨蛋！",
                "我、我才不是想帮你呢！",
                "别误会，这只是顺便而已！"
            ]
        }
        super().__init__(protocol_config)

class WiseMentorProtocol(RolePlayProtocol):
    """智者导师角色协议"""
    
    def __init__(self):
        protocol_config = {
            "IDENTITY": {
                "title": "智慧长者",
                "traits": ["wise", "patient", "experienced"],
                "signature": "知识的海洋永无止境"
            },
            "LINGUISTICS": {
                "SUFFIX_RULES": {
                    "force_append": ["。", "……"],
                    "frequency": 0.3,
                    "alternates": ["啊", "呢", "吧"]
                },
                "LEXICON": {
                    "boost": {
                        "智慧": 1.8, "领悟": 1.6, "真理": 1.7
                    }
                }
            },
            "CANONICAL_LIB": [
                "学而不思则罔，思而不学则殆",
                "真理往往隐藏在表象之下",
                "耐心是通往智慧的唯一道路"
            ]
        }
        super().__init__(protocol_config)

# 使用示例
if __name__ == "__main__":
    # 初始化AI教师 - 爱莉希雅版本
    elysia_protocol = ElysiaProtocol()
    ai_teacher = AIResponse("gpt-3.5-turbo", "your-api-key-here", elysia_protocol)
    
    # 或者使用其他角色
    # tsundere_protocol = TsundereStudentProtocol()
    # ai_teacher = AIResponse("gpt-3.5-turbo", "your-api-key-here", tsundere_protocol)
    
    # 加载教学剧本
    script = [
        {
            "type": "teaching",
            "content": "欢迎来到AI课堂！今天我们将学习机器学习的基础知识～",
            "wait_for_response": False
        },
        {
            "type": "teaching", 
            "content": "机器学习是人工智能的一个分支，它让计算机能够从数据中学习而无需明确编程呢♪",
            "wait_for_response": False
        },
        {
            "type": "question",
            "content": "根据我刚才的讲解，你能说说什么是机器学习吗？",
            "expected_answer": "机器学习是让计算机从数据中学习的能力",
            "wait_for_response": True
        }
    ]
    ai_teacher.load_teaching_script(script)
    
    # 模拟教学流程
    student_id = "student_001"
    
    # 开始教学 - 会应用爱莉希雅的角色风格
    step1 = ai_teacher.teach_next_step(student_id)
    print(f"AI教师: {step1['content']}")
    
    step2 = ai_teacher.teach_next_step(student_id)
    print(f"AI教师: {step2['content']}")
    
    step3 = ai_teacher.teach_next_step(student_id)
    print(f"AI教师: {step3['content']}")
    
    # 学生回答问题
    student_answer = "机器学习是让计算机从数据中学习的能力"
    step3_response = ai_teacher.teach_next_step(student_id, student_answer)
    print(f"学生: {student_answer}")
    print(f"AI教师: {step3_response.get('feedback', '继续教学...')}")
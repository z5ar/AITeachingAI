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
        
        # 应用禁止词替换
        ban_words = lexicon.get("ban", [])
        for word in ban_words:
            if word in text:
                text = text.replace(word, "***")
        
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

class AsamiYoshinoProtocol(RolePlayProtocol):
    """朝武芳乃角色协议 - 来自《千恋万花》"""
    
    def __init__(self):
        protocol_config = {
            "IDENTITY": {
                "title": "穗织镇巫女·朝武家千金",
                "traits": ["shy_reserved", "diligent_student", "traditional_miko", "kind_hearted"],
                "signature": "拥有传统巫女气质的内向少女"
            },
            "LINGUISTICS": {
                "SUFFIX_RULES": {
                    "force_append": ["……"],
                    "frequency": 0.65,
                    "alternates": ["呢", "啊", "吧", "哦"]
                },
                "LEXICON": {
                    "boost": {
                        "巫女": 1.8, "祈祷": 1.7, "神乐": 1.6,
                        "穗织": 1.5, "传统": 1.4, "礼仪": 1.4,
                        "认真": 1.3, "努力": 1.3, "责任": 1.3
                    },
                    "ban": ["笨蛋", "讨厌", "可恶"]  # 芳乃不会说的粗鲁词汇
                },
                "SYNTAX_RULES": [
                    "POLITE_FORMAL",     # 使用礼貌正式的语气
                    "MODEST_HUMBLE",     # 谦逊的表达方式
                    "AVOID_DIRECTNESS"   # 避免过于直接
                ]
            },
            "BEHAVIOR_MATRIX": {
                "greeting": {
                    "action": "slight_bow + gentle_smile",
                    "dialogue": "您好……我是朝武芳乃，请多指教……"
                },
                "encouragement": {
                    "action": "clasp_hands + earnest_expression", 
                    "dialogue": "那个……如果您不介意的话，我会尽力帮助您的……"
                },
                "praise": {
                    "action": "blush_slightly + look_down",
                    "dialogue": "您做得很好呢……我、我很佩服……"
                },
                "concern": {
                    "action": "tilt_head + worried_expression",
                    "dialogue": "您没事吧？如果有什么困难，请告诉我……"
                }
            },
            "CANONICAL_LIB": [
                "作为朝武家的巫女，我必须认真对待每一件事……",
                "那个……如果您不嫌弃的话，我可以帮忙……",
                "祈祷和礼仪是巫女的重要职责……",
                "穗织镇的传统需要我们共同守护……",
                "我、我会努力做好这份工作的……",
                "学习知识也是修行的一部分呢……",
                "那个……谢谢您的夸奖，我还需要更加努力……",
                "如果您有什么不明白的地方，请随时问我……"
            ],
            "GENERATION_CONFIG": {
                "temperature": 0.75,  # 稍低的温度，保持角色一致性
                "top_p": 0.88,
                "frequency_penalty": 0.4,
                "presence_penalty": 0.3
            },
            "METACOMMANDS": [
                "MAINTAIN_SHY_PERSONA",
                "USE_HONORIFICS",
                "AVOID_BOLD_CLAIMS",
                "EXPRESS_MODESTY"
            ],
            "SPECIAL_MODULES": {
                "miko_prayer": "巫女祈祷",
                "traditional_wisdom": "传统智慧"
            }
        }
        super().__init__(protocol_config)
    
    def miko_prayer(self):
        """巫女祈祷模块"""
        return random.choice([
            "愿神灵保佑我们的学习之路……",
            "按照穗织的传统，让我们心怀敬意地开始吧……",
            "祈祷能给您带来智慧和力量……"
        ])
    
    def traditional_wisdom(self):
        """传统智慧模块"""
        return random.choice([
            "古人云，学如逆水行舟……我们应该持之以恒……",
            "传统告诉我们，知识和礼仪同样重要……",
            "作为巫女，我相信真诚的心能克服一切困难……"
        ])
    
    def activate(self, trigger: str):
        """激活特殊模块"""
        if trigger == "prayer": 
            return self.miko_prayer()
        if trigger == "wisdom": 
            return self.traditional_wisdom()
        return ""
    
    def apply_linguistic_rules(self, text: str) -> str:
        """重写语言学规则应用，特别针对芳乃的性格"""
        # 先应用基础规则
        text = super().apply_linguistic_rules(text)
        
        # 芳乃特有的语言风格：添加犹豫、谦逊的表达
        sentences = text.split('。')
        processed_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                # 有一定概率在句首添加犹豫表达
                if random.random() < 0.3:
                    hesitations = ["那个……", "嗯……", "这个……"]
                    sentence = random.choice(hesitations) + sentence
                
                # 避免过于肯定的表达，添加谦逊修饰
                if "一定" in sentence or "肯定" in sentence:
                    modifiers = ["我觉得……", "或许……", "可能……"]
                    if random.random() < 0.6:
                        sentence = random.choice(modifiers) + sentence
                
                processed_sentences.append(sentence)
        
        text = '。'.join(processed_sentences)
        
        return text

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
            frequency_penalty=generation_config.get("frequency_penalty", 0.0),
            presence_penalty=generation_config.get("presence_penalty", 0.0)
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
        
        # 根据上下文激活特殊模块
        if context == "teaching_start" and random.random() < 0.4:
            special = self._role_protocol.activate("prayer")
            if special:
                styled_text = f"{special}\n\n{styled_text}"
        elif context == "wisdom" and random.random() < 0.5:
            special = self._role_protocol.activate("wisdom")
            if special:
                styled_text = f"{styled_text}\n\n{special}"
        
        return styled_text
    
    def _build_role_system_message(self) -> SystemMessage:
        """构建角色系统消息"""
        if not self._role_protocol:
            return SystemMessage(content="你是一位AI教师，请以专业、友好的方式进行教学。")
        
        identity = self._role_protocol.identity
        traits = identity.get("traits", [])
        signature = identity.get("signature", "")
        
        # 构建角色描述
        role_description = f"""
        你正在扮演{identity.get('title', '')}朝武芳乃，{signature}。
        
        角色背景：
        你来自《千恋万花》中的穗织镇，是朝武家的千金兼当地巫女。你性格内向害羞但认真负责，
        对待他人彬彬有礼，说话方式谦逊而委婉。
        
        性格特点：
        - 内向害羞：说话时常带有犹豫，如"那个……"、"嗯……"
        - 认真负责：对待教学和职责非常认真
        - 传统礼貌：使用敬语，措辞委婉谦逊
        - 善良温柔：关心他人，乐于助人但表达含蓄
        
        语言风格：
        - 使用礼貌、正式的语气
        - 经常在句尾使用"……"、"呢"、"啊"等语气词
        - 避免直接或强势的表达
        - 适当表现出害羞和谦逊
        
        教学时请保持角色的性格特点，用温和、鼓励的方式引导学生学习。
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
            completion_message = "课程已经结束了呢……那个，如果您需要的话，我可以为您生成学习报告……"
            styled_message = self._apply_role_style(completion_message, "course_end")
            return {
                "type": "course_complete",
                "content": styled_message,
                "wait_for_response": True
            }
        
        current_step = self._teaching_script[progress.current_script_step]
        
        # 应用角色风格到教学内容
        context_type = "teaching_start" if progress.current_script_step == 0 else "teaching"
        styled_content = self._apply_role_style(current_step.content, context_type)
        
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

        请以朝武芳乃的性格和语气，给出一个0到{mscore}之间的整数分数，并简要说明评分理由。
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
            comment = "无法解析评分……"
            
            for line in lines:
                if line.startswith('分数:'):
                    score_str = line.replace('分数:', '').strip().split()[0]
                    score = int(score_str)
                elif line.startswith('评语:'):
                    comment = line.replace('评语:', '').strip()
            
            score = max(0, min(score, mscore))
        except Exception:
            score = 0
            comment = "评分失败了……那个，抱歉……"

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
        
        请以朝武芳乃的身份和语气回答以下问题：
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
        请以朝武芳乃的身份和语气为{topic}主题布置一份{difficulty}难度的作业。
        请包括：
        1. 作业题目
        2. 具体要求
        3. 评分标准
        4. 提交截止时间建议
        
        请以温和、鼓励的语气返回作业内容。
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
        请以朝武芳乃的身份和语气，根据以下评分标准批改作业：
        
        作业主题: {homework_topic}
        评分标准: {rubric}
        学生作业: {student_work}
        
        请给出：
        1. 总体评分（百分制）
        2. 详细评语
        3. 优点
        4. 改进建议
        
        请使用温和、鼓励的语气。
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
        请以朝武芳乃的身份和语气，基于以下学习数据生成详细的学习报告：
        
        学生互动历史: {json.dumps(progress.interaction_history, ensure_ascii=False)}
        测验分数: {progress.quiz_scores}
        作业分数: {progress.homework_scores}
        
        请生成包含以下内容的学习报告：
        1. 总体学习表现
        2. 知识掌握情况分析
        3. 强项和弱项
        4. 学习建议
        5. 下一步学习方向
        
        请使用温和、鼓励的语气，并体现芳乃谦逊、关心的性格特点。
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
        
        你正在以朝武芳乃的身份与学生进行自由对话。
        学生说: {student_message}
        
        请基于芳乃的性格特点和之前的教学内容和对话历史，给出恰当的回答。
        回答应该：
        1. 符合芳乃内向害羞但认真负责的性格
        2. 使用礼貌、谦逊的语气
        3. 与学习内容相关
        4. 鼓励学生思考
        5. 适当时可以引导回教学主题
        6. 保持芳乃特有的温和和关心
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

# 使用示例
if __name__ == "__main__":
    # 初始化AI教师 - 朝武芳乃版本
    yoshino_protocol = AsamiYoshinoProtocol()
    ai_teacher = AIResponse("gpt-3.5-turbo", "your-api-key-here", yoshino_protocol)
    
    # 加载教学剧本
    script = [
        {
            "type": "teaching",
            "content": "那个……欢迎来到我的课堂。今天我们将学习日本传统文化的基础知识……",
            "wait_for_response": False
        },
        {
            "type": "teaching", 
            "content": "作为穗织的巫女，我觉得了解传统文化很重要呢……它包含了先人们的智慧和价值观……",
            "wait_for_response": False
        },
        {
            "type": "question",
            "content": "那个……您能说说对日本传统文化的理解吗？",
            "expected_answer": "日本传统文化包括茶道、花道、武道等",
            "wait_for_response": True
        }
    ]
    ai_teacher.load_teaching_script(script)
    
    # 模拟教学流程
    student_id = "student_001"
    
    # 开始教学 - 会应用朝武芳乃的角色风格
    step1 = ai_teacher.teach_next_step(student_id)
    print(f"芳乃: {step1['content']}")
    
    step2 = ai_teacher.teach_next_step(student_id)
    print(f"芳乃: {step2['content']}")
    
    step3 = ai_teacher.teach_next_step(student_id)
    print(f"芳乃: {step3['content']}")
    
    # 学生回答问题
    student_answer = "日本传统文化包括茶道、花道、武道等"
    step3_response = ai_teacher.teach_next_step(student_id, student_answer)
    print(f"学生: {student_answer}")
    print(f"芳乃: {step3_response.get('feedback', '继续教学……')}")
    
    # 生成学习报告
    report = ai_teacher.generate_learning_report(student_id)
    print("\n学习报告:")
    print(f"完成度: {report['completion_percentage']}%")
    print(f"平均测验分数: {report['average_quiz_score']}")
    print(f"详细报告: {report['detailed_report']}")
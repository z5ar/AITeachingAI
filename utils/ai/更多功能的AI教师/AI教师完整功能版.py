from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Tuple, Optional
import os
import json
import datetime
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

class AIResponse:
    _model_name: str
    _API_key: str
    _chat_model: ChatOpenAI
    _memory: ConversationBufferMemory
    _teaching_script: List[ScriptStep]
    _student_progress: Dict[str, StudentProgress]
    
    def __init__(self, model_name: str, API_key: str):
        self._model_name = model_name
        self._API_key = API_key
        os.environ["OPENAI_API_KEY"] = self._API_key
        self._chat_model = ChatOpenAI(model_name=self._model_name, temperature=0.7)
        self._memory = ConversationBufferMemory(return_messages=True)
        self._teaching_script = []
        self._student_progress = {}
        
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
        """进行下一步教学，类似Galgame的文字推进"""
        progress = self.get_student_progress(student_id)
        
        if progress.current_script_step >= len(self._teaching_script):
            return {
                "type": "course_complete",
                "content": "课程已完成！是否要生成学习报告？",
                "wait_for_response": True
            }
        
        current_step = self._teaching_script[progress.current_script_step]
        response_data = {
            "type": current_step.step_type.value,
            "content": current_step.content,
            "wait_for_response": current_step.wait_for_response,
            "current_step": progress.current_script_step,
            "total_steps": len(self._teaching_script)
        }
        
        # 记录互动历史
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": current_step.step_type.value,
            "teacher_content": current_step.content,
            "student_response": student_response
        }
        
        if student_response and current_step.step_type == InteractionType.QUESTION:
            # 评估学生回答
            score, feedback = self.judge_answer(
                ans=student_response,
                std=current_step.expected_answer or "",
                problem=current_step.content,
                mscore=10
            )
            interaction_record["score"] = score
            interaction_record["feedback"] = feedback
            progress.quiz_scores.append(score)
            
            response_data["feedback"] = feedback
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
        '''
        使用AI为回答打分，并给出评语。
        '''
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

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
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
        '''
        使用AI回答问题，包含记忆功能。
        '''
        context = self._get_recent_context()
        
        prompt = f'''
        {context}
        
        请回答以下问题：
        {question}
        '''

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        answer = response.content.strip()

        # 更新记忆
        self._memory.save_context(
            {"input": question},
            {"output": answer}
        )

        return answer
    
    def assign_homework(self, topic: str, difficulty: str = "medium") -> Dict:
        """布置作业"""
        prompt = f'''
        请为{topic}主题布置一份{difficulty}难度的作业。
        请包括：
        1. 作业题目
        2. 具体要求
        3. 评分标准
        4. 提交截止时间建议
        
        请以清晰的格式返回作业内容。
        '''

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        homework_content = response.content.strip()
        
        homework_data = {
            "topic": topic,
            "difficulty": difficulty,
            "content": homework_content,
            "assigned_date": datetime.datetime.now().isoformat(),
            "due_date": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
        }
        
        return homework_data
    
    def grade_homework(self, student_id: str, homework_topic: str, 
                      student_work: str, rubric: str) -> Dict:
        """批改作业"""
        progress = self.get_student_progress(student_id)
        
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

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        grading_result = response.content.strip()
        
        # 简化的分数提取（实际应用中需要更复杂的解析）
        try:
            score_line = [line for line in grading_result.split('\n') if '评分' in line or '分数' in line][0]
            score = int(''.join(filter(str.isdigit, score_line))[:3])
            score = max(0, min(score, 100))
        except:
            score = 0
        
        homework_record = {
            "topic": homework_topic,
            "submission": student_work,
            "score": score,
            "feedback": grading_result,
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
            "detailed_feedback": grading_result,
            "homework_topic": homework_topic
        }
    
    def generate_learning_report(self, student_id: str) -> Dict:
        """生成学习报告"""
        progress = self.get_student_progress(student_id)
        
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

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        report_content = response.content.strip()
        
        # 计算统计数据
        avg_quiz_score = sum(progress.quiz_scores) / len(progress.quiz_scores) if progress.quiz_scores else 0
        avg_homework_score = sum(progress.homework_scores) / len(progress.homework_scores) if progress.homework_scores else 0
        
        progress.learning_report = {
            "generated_date": datetime.datetime.now().isoformat(),
            "student_id": student_id,
            "total_interactions": len(progress.interaction_history),
            "average_quiz_score": round(avg_quiz_score, 2),
            "average_homework_score": round(avg_homework_score, 2),
            "detailed_report": report_content,
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
        """继续自由对话，基于之前的互动"""
        progress = self.get_student_progress(student_id)
        context = self._get_recent_context()
        
        prompt = f'''
        {context}
        
        你是一位AI教师，正在与学生进行自由对话。
        学生说: {student_message}
        
        请基于之前的教学内容和对话历史，给出恰当的回答。
        回答应该：
        1. 与学习内容相关
        2. 鼓励学生思考
        3. 适当时可以引导回教学主题
        4. 保持友好和支持性
        '''

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        teacher_response = response.content.strip()
        
        # 记录对话
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": "free_conversation",
            "student_message": student_message,
            "teacher_response": teacher_response
        }
        progress.interaction_history.append(interaction_record)
        
        # 更新记忆
        self._memory.save_context(
            {"input": student_message},
            {"output": teacher_response}
        )
        
        return {
            "type": "conversation",
            "content": teacher_response,
            "wait_for_response": True
        }

# 示例使用方式
def create_sample_script() -> List[Dict]:
    """创建示例教学剧本"""
    return [
        {
            "type": "teaching",
            "content": "欢迎来到AI课堂！今天我们将学习机器学习的基础知识。",
            "wait_for_response": False
        },
        {
            "type": "teaching", 
            "content": "机器学习是人工智能的一个分支，它让计算机能够从数据中学习而无需明确编程。",
            "wait_for_response": False
        },
        {
            "type": "question",
            "content": "根据我刚才的讲解，你能说说什么是机器学习吗？",
            "expected_answer": "机器学习是让计算机从数据中学习的能力",
            "wait_for_response": True
        },
        {
            "type": "teaching",
            "content": "很好！现在让我们学习监督学习和无监督学习的区别...",
            "wait_for_response": False
        },
        {
            "type": "question",
            "content": "监督学习和无监督学习的主要区别是什么？",
            "expected_answer": "监督学习使用标注数据，无监督学习使用未标注数据",
            "wait_for_response": True
        }
    ]

# 使用示例
if __name__ == "__main__":
    # 初始化AI教师
    ai_teacher = AIResponse("gpt-3.5-turbo", "your-api-key-here")
    
    # 加载教学剧本
    script = create_sample_script()
    ai_teacher.load_teaching_script(script)
    
    # 模拟教学流程
    student_id = "student_001"
    
    # 开始教学
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
    
    # 生成学习报告
    report = ai_teacher.generate_learning_report(student_id)
    print("\n学习报告:")
    print(f"完成度: {report['completion_percentage']}%")
    print(f"平均测验分数: {report['average_quiz_score']}")
    print(f"详细报告: {report['detailed_report']}")
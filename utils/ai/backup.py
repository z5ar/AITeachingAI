import os
import json
import datetime
import random
import requests
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum

class InteractionType(Enum):
    TEXT = "text"
    VIDEO = "video"
    PROBLEM = "problem"
    INTERACTION = "interaction"
    TEACHER_INTERACTION = "teacher_interaction"  # 新增：教师主动互动类型

class ScriptStep:
    def __init__(self, 
                 step_type: InteractionType, 
                 content: str, 
                 expected_answer: Optional[str] = None,
                 options: Optional[List[str]] = None,
                 video_description: Optional[str] = None,
                 wait_for_response: bool = False,
                 notes: Optional[str] = None,
                 ppt_image: Optional[str] = None,
                 knowledge_point: Optional[str] = None,
                 chapter: Optional[str] = None):
        self.step_type = step_type
        self.content = content
        self.expected_answer = expected_answer
        self.options = options
        self.video_description = video_description
        self.wait_for_response = wait_for_response
        self.notes = notes
        self.ppt_image = ppt_image
        self.knowledge_point = knowledge_point
        self.chapter = chapter

class StudentProgress:
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.current_script_step = 0
        self.interaction_history = []
        self.quiz_scores = []
        self.homework_scores = []
        self.learning_report = {}
        self.affection_level = 50
        self.affection_history = []
        self.start_time = datetime.datetime.now()
        self.last_interaction_time = datetime.datetime.now()
        self.learning_duration = 0
        self.consecutive_teaching_steps = 0  # 新增：连续教学步骤计数

    def update_affection(self, change: int, reason: str):
        old_level = self.affection_level
        self.affection_level = max(0, min(100, self.affection_level + change))
        self.affection_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "old_level": old_level,
            "new_level": self.affection_level,
            "change": change,
            "reason": reason
        })

    def update_learning_duration(self):
        now = datetime.datetime.now()
        self.learning_duration += (now - self.last_interaction_time).total_seconds()
        self.last_interaction_time = now

class SiliconFlowClient:
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        if not self.api_key.startswith("sk-"):
            print(f"警告: API密钥格式可能不正确: {self.api_key[:10]}...")
        self.base_url = "https://api.siliconflow.cn/v1"
    
    def chat_completion(self, messages: List[Dict], model: str = "deepseek-ai/DeepSeek-V3", **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=data,
                timeout=60
            )
            
            if response.status_code == 401:
                return f"API认证失败: 请检查API密钥是否正确"
            elif response.status_code != 200:
                return f"API请求失败，状态码: {response.status_code}"
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "AI响应格式异常"
                
        except requests.exceptions.RequestException as e:
            return f"网络请求失败: {str(e)}"
        except Exception as e:
            return f"AI服务暂时不可用: {str(e)}"

class YukinoshitaYukinoAI:
    def __init__(self, api_key: str):
        self.client = SiliconFlowClient(api_key)
        self.identity = {
            "title": "雪之下雪乃",
            "signature": "总武高中完美超人，冷静理性的优等生"
        }
        self.teaching_script = []
        self.student_progress = {}
    
    def load_teaching_script(self, script_data: List[Dict]):
        self.teaching_script = []
        for step_data in script_data:
            step = ScriptStep(
                step_type=InteractionType(step_data["type"]),
                content=step_data["content"],
                expected_answer=step_data.get("expected_answer"),
                options=step_data.get("options"),
                video_description=step_data.get("video_description"),
                wait_for_response=step_data.get("wait_for_response", False),
                notes=step_data.get("notes"),
                ppt_image=step_data.get("ppt_image"),
                knowledge_point=step_data.get("knowledge_point"),
                chapter=step_data.get("chapter")
            )
            self.teaching_script.append(step)
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        if student_id not in self.student_progress:
            self.student_progress[student_id] = StudentProgress(student_id)
        return self.student_progress[student_id]
    
    def apply_role_style(self, text: str) -> str:
        if random.random() < 0.2:
            prefixes = ["说起来，", "从学生的角度来说，", "简单来说，"]
            text = random.choice(prefixes) + text
        
        if random.random() < 0.3:
            suffixes = ["……这样解释应该能明白吧。", "……其实并不复杂。", "……理解了吗？"]
            text += random.choice(suffixes)
            
        return text
    
    def build_system_message(self, additional_context: str = "") -> Dict:
        role_description = f"""
        你正在扮演{self.identity['title']}，{self.identity['signature']}。

        角色背景：来自《我的青春恋爱物语果然有问题》中的雪之下雪乃，是总武高中的优等生。
        性格特点：冷静理性、聪明过人、表面高冷但内心温柔，说话直接但有理有据。

        语言风格：
        - 使用理性、清晰且通俗易懂的语气
        - 避免使用过于复杂的专业术语，必要时会用简单比喻解释
        - 讲解清晰有条理，逻辑性强
        - 不会过度热情，但会认真负责地教学
        - 避免推眼镜等不相关的动作描述

        教学要求：
        - 用通俗易懂的方式详细讲解知识点，就像在给同学讲解一样
        - 不仅要解释概念，还要用生活中的例子来说明
        - 结合实际案例和日常应用进行讲解
        - 保持内容的准确性，但避免过度学术化
        - 适当时候可以分享学习心得和方法

        {additional_context}
        """
        
        return {"role": "system", "content": role_description}
    
    def generate_detailed_explanation(self, topic: str, base_content: str, chapter: str = "") -> str:
        """生成对知识点的通俗易懂解释"""
        system_message = self.build_system_message(
            f"请用通俗易懂的方式讲解以下AI知识点，就像在给同学解释一样："
        )
        
        prompt = f"""
        需要讲解的主题：{topic}
        基础内容：{base_content}
        所属章节：{chapter}

        请用雪之下雪乃的风格，用通俗易懂的语言讲解这个AI知识点：
        1. 用简单的语言解释概念的核心思想
        2. 用生活中的例子或比喻来说明
        3. 说明这个技术的实际应用场景
        4. 解释为什么这个技术重要
        5. 避免过于专业的术语，如果必须使用请简单解释

        请确保讲解既准确又容易理解，就像在帮助同学理解一样。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7, max_tokens=1200)
        return self.apply_role_style(response)
    
    def generate_teacher_interaction(self, progress: StudentProgress, current_step: ScriptStep) -> str:
        """生成教师主动互动的内容"""
        system_message = self.build_system_message(
            "请根据教学情况生成自然的教师互动语句："
        )
        
        # 构建上下文信息
        context_info = {
            "current_chapter": current_step.chapter or "未知章节",
            "current_knowledge_point": current_step.knowledge_point or "当前知识点",
            "progress_percentage": (progress.current_script_step / len(self.teaching_script)) * 100,
            "affection_level": progress.affection_level,
            "consecutive_steps": progress.consecutive_teaching_steps
        }
        
        prompt = f"""
        教学上下文信息：
        - 当前章节：{context_info['current_chapter']}
        - 当前知识点：{context_info['current_knowledge_point']}
        - 课程进度：{context_info['progress_percentage']:.1f}%
        - 学生认可度：{context_info['affection_level']}/100
        - 连续讲解步骤：{context_info['consecutive_steps']}步

        请用雪之下雪乃的风格，生成一句自然的教师互动语句。这些互动应该像真实教师在课堂上会说的话，例如：
        - 检查理解情况："这部分内容理解了吗？有疑问可以提出来。"
        - 鼓励提问："关于这个概念，有什么不明白的地方吗？"
        - 过渡提示："接下来我们要讲下一个知识点了，请大家集中注意力。"
        - 给予思考时间："给大家一点时间消化一下刚才的内容。"
        - 调动积极性："今天大家学习状态不错，继续保持。"
        - 进度提醒："我们已经学完了一半内容，坚持就是胜利。"

        请根据当前教学情况生成一句合适的互动语句，要自然、贴切，符合雪之下雪乃的性格特点。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.8, max_tokens=500)
        return self.apply_role_style(response)
    
    def should_insert_interaction(self, progress: StudentProgress) -> bool:
        """判断是否应该插入互动"""
        # 基于以下条件决定是否插入互动：
        # 1. 连续讲解步骤超过2步
        # 2. 随机因素（约30%概率）
        # 3. 学生认可度较低时需要更多互动
        base_probability = 0.3
        
        # 连续讲解步骤越多，插入互动的概率越高
        if progress.consecutive_teaching_steps >= 3:
            base_probability += 0.2
        if progress.consecutive_teaching_steps >= 5:
            base_probability += 0.3
        
        # 学生认可度低时增加互动频率
        if progress.affection_level < 40:
            base_probability += 0.2
        
        return random.random() < base_probability
    
    def teach_next_step(self, student_id: str, student_response: Optional[str] = None) -> Dict:
        progress = self.get_student_progress(student_id)
        progress.update_learning_duration()
        
        # 检查是否需要插入教师互动
        if (progress.current_script_step > 0 and 
            progress.current_script_step < len(self.teaching_script) and
            self.should_insert_interaction(progress)):
            
            current_step = self.teaching_script[progress.current_script_step]
            interaction_content = self.generate_teacher_interaction(progress, current_step)
            
            # 创建互动步骤
            interaction_step = {
                "type": "teacher_interaction",
                "content": interaction_content,
                "wait_for_response": False,
                "current_step": progress.current_script_step,
                "total_steps": len(self.teaching_script),
                "is_auto_generated": True  # 标记为自动生成的互动
            }
            
            # 重置连续教学步骤计数
            progress.consecutive_teaching_steps = 0
            
            # 记录互动历史
            progress.interaction_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "step_type": "teacher_interaction",
                "teacher_content": interaction_content,
                "student_response": student_response,
                "step_index": progress.current_script_step,
                "is_auto_generated": True
            })
            
            return interaction_step
        
        # 正常教学流程
        if progress.current_script_step >= len(self.teaching_script):
            return self.generate_course_complete_response(progress)
        
        current_step = self.teaching_script[progress.current_script_step]
        response_data = self.process_step(current_step, progress, student_response)
        
        # 更新连续教学步骤计数
        if current_step.step_type == InteractionType.TEXT:
            progress.consecutive_teaching_steps += 1
        else:
            progress.consecutive_teaching_steps = 0
        
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": current_step.step_type.value,
            "teacher_content": response_data["content"],
            "student_response": student_response,
            "step_index": progress.current_script_step
        }
        
        if student_response and current_step.step_type in [InteractionType.PROBLEM, InteractionType.INTERACTION]:
            feedback_data = self.process_student_response(current_step, student_response, progress)
            response_data.update(feedback_data)
            interaction_record.update(feedback_data)
        
        progress.interaction_history.append(interaction_record)
        
        if not current_step.wait_for_response or student_response:
            progress.current_script_step += 1
        
        return response_data
    
    def process_step(self, step: ScriptStep, progress: StudentProgress, student_response: Optional[str]) -> Dict:
        base_response = {
            "type": step.step_type.value,
            "wait_for_response": step.wait_for_response,
            "current_step": progress.current_script_step,
            "total_steps": len(self.teaching_script),
            "notes": step.notes,
            "ppt_image": step.ppt_image,
            "chapter": step.chapter,
            "knowledge_point": step.knowledge_point
        }
        
        if step.step_type == InteractionType.TEXT:
            content = self.generate_detailed_explanation(
                step.knowledge_point or "AI知识", 
                step.content,
                step.chapter or ""
            )
            base_response["content"] = content
            
        elif step.step_type == InteractionType.VIDEO:
            content = self.generate_video_content(step.content, step.video_description)
            base_response["content"] = content
            base_response["video_description"] = step.video_description
            
        elif step.step_type == InteractionType.PROBLEM:
            content = self.generate_problem_content(step.content, step.options)
            base_response["content"] = content
            base_response["options"] = step.options
            base_response["expected_answer"] = step.expected_answer
            
        elif step.step_type == InteractionType.INTERACTION:
            content = self.generate_interaction_content(step.content, progress.affection_level)
            base_response["content"] = content
            
        elif step.step_type == InteractionType.TEACHER_INTERACTION:
            # 对于剧本中预定义的教师互动，也使用AI生成内容
            content = self.generate_teacher_interaction(progress, step)
            base_response["content"] = content
            base_response["wait_for_response"] = False
            
        return base_response
    
    def generate_video_content(self, content: str, video_description: str) -> str:
        system_message = self.build_system_message(
            "请根据视频内容进行通俗讲解："
        )
        
        prompt = f"""
        视频内容描述：{video_description}
        教学要点：{content}
        
        请用雪之下雪乃的风格，用容易理解的方式介绍视频内容和学习重点。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7)
        return self.apply_role_style(response)
    
    def generate_problem_content(self, content: str, options: Optional[List[str]]) -> str:
        system_message = self.build_system_message(
            "请用清晰的方式提出问题："
        )
        
        option_text = ""
        if options:
            option_text = "\n选项：\n" + "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""
        问题：{content}
        {option_text}
        
        请用雪之下雪乃的风格清晰地提出这个问题。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7)
        return self.apply_role_style(response)
    
    def generate_interaction_content(self, content: str, affection_level: int) -> str:
        system_message = self.build_system_message(
            "请用友好的方式进行互动："
        )
        
        prompt = f"""
        互动主题：{content}
        当前认可度：{affection_level}/100
        
        请用雪之下雪乃的风格发起友好的互动。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.8)
        return self.apply_role_style(response)
    
    def process_student_response(self, step: ScriptStep, student_answer: str, progress: StudentProgress) -> Dict:
        if step.step_type == InteractionType.PROBLEM:
            return self.grade_problem_answer(step, student_answer, progress)
        elif step.step_type == InteractionType.INTERACTION:
            return self.handle_interaction(step, student_answer, progress)
        return {}
    
    def grade_problem_answer(self, step: ScriptStep, student_answer: str, progress: StudentProgress) -> Dict:
        score = 0
        if step.expected_answer:
            if student_answer.strip().lower() == step.expected_answer.strip().lower():
                score = 100
            elif step.options:
                correct_index = ord(step.expected_answer.upper()) - 65
                if 0 <= correct_index < len(step.options):
                    if student_answer.upper() == step.expected_answer.upper():
                        score = 100
        
        affection_change = 0
        if score >= 80:
            affection_change = 5
            feedback = "回答正确，理解得很到位。"
        elif score >= 60:
            affection_change = 2
            feedback = "基本正确，但还可以更准确一些。"
        else:
            affection_change = -2
            feedback = "这个回答不太准确，建议再思考一下。"
        
        progress.update_affection(affection_change, f"问题回答得分：{score}")
        progress.quiz_scores.append(score)
        
        system_message = self.build_system_message(
            "请对学生的回答给予建设性反馈："
        )
        
        prompt = f"""
        问题：{step.content}
        学生答案：{student_answer}
        正确答案：{step.expected_answer}
        得分：{score}/100
        
        请用雪之下雪乃的风格给出鼓励性的反馈，并简单解释正确答案。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            ai_feedback = self.client.chat_completion(messages, temperature=0.7)
            ai_feedback = self.apply_role_style(ai_feedback)
        except:
            ai_feedback = feedback
        
        return {
            "score": score,
            "feedback": ai_feedback,
            "affection_change": affection_change,
            "correct_answer": step.expected_answer
        }
    
    def handle_interaction(self, step: ScriptStep, student_message: str, progress: StudentProgress) -> Dict:
        system_message = self.build_system_message(
            "请友好地回答学生的问题："
        )
        
        prompt = f"""
        学生说：{student_message}
        当前认可度：{progress.affection_level}/100
        
        请用雪之下雪乃的风格友好回应，用通俗易懂的语言解释。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            reply = self.client.chat_completion(messages, temperature=0.8)
            reply = self.apply_role_style(reply)
            
            progress.update_affection(3, "积极参与讨论")
            
        except Exception as e:
            reply = f"这个问题需要更清晰的解答……{str(e)}"
        
        return {
            "interaction_reply": reply,
            "affection_change": 3
        }
    
    def answer_question_about_knowledge(self, student_id: str, knowledge_point: str, student_question: str) -> Dict:
        progress = self.get_student_progress(student_id)
        
        related_content = ""
        for step in self.teaching_script:
            if step.knowledge_point == knowledge_point:
                related_content = step.content
                break
        
        system_message = self.build_system_message(
            f"请针对知识点 '{knowledge_point}' 用通俗语言回答学生的问题："
        )
        
        prompt = f"""
        相关知识点内容：{related_content}
        学生的问题：{student_question}
        
        请用雪之下雪乃的风格，用容易理解的方式详细解释这个问题。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            answer = self.client.chat_completion(messages, temperature=0.7)
            answer = self.apply_role_style(answer)
            
            progress.interaction_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "knowledge_question",
                "knowledge_point": knowledge_point,
                "question": student_question,
                "answer": answer
            })
            
            progress.update_affection(3, "主动提问学习")
            
            return {
                "success": True,
                "answer": answer,
                "affection_change": 3
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_course_complete_response(self, progress: StudentProgress) -> Dict:
        progress.update_learning_duration()
        
        completion_message = """
        课程已经全部完成了。

        你的学习态度值得肯定，希望这些AI知识对你有所帮助。
        我会为你生成最终的学习报告……
        """
        
        return {
            "type": "course_complete",
            "content": self.apply_role_style(completion_message),
            "wait_for_response": False
        }

class Characters(Enum):
    YukinoshitaYukino = YukinoshitaYukinoAI

instances = dict()

def render_teacher(api_key: str, character: Characters):
    if character not in instances.keys:
        instances[character] = character(api_key)
    return instances[character]
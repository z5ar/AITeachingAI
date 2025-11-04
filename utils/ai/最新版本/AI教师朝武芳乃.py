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
                 knowledge_point: Optional[str] = None):
        self.step_type = step_type
        self.content = content
        self.expected_answer = expected_answer
        self.options = options
        self.video_description = video_description
        self.wait_for_response = wait_for_response
        self.notes = notes
        self.ppt_image = ppt_image
        self.knowledge_point = knowledge_point

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
        # 确保 API 密钥格式正确
        self.api_key = api_key.strip()
        if not self.api_key.startswith("sk-"):
            print(f"警告: API密钥格式可能不正确: {self.api_key[:10]}...")
        self.base_url = "https://api.siliconflow.cn/v1"
    
    def chat_completion(self, messages: List[Dict], model: str = "deepseek-ai/DeepSeek-V3", **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        
        # 正确的请求头格式
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建正确的请求体
        data = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        print(f"发送请求到 SiliconFlow...")
        print(f"模型: {model}")
        print(f"消息数量: {len(messages)}")
        print(f"API密钥前几位: {self.api_key[:10]}...")
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=data,
                timeout=60
            )
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 401:
                error_detail = "认证失败，请检查API密钥是否正确"
                print(f"401错误详情: {response.text}")
                return f"API认证失败: {error_detail}"
            elif response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                print(f"错误响应: {response.text}")
                return error_msg
            
            result = response.json()
            print("API调用成功!")
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "AI响应格式异常"
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            return f"网络请求失败: {str(e)}"
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            return f"AI服务暂时不可用: {str(e)}"

class AsamiYoshinoAI:
    def __init__(self, api_key: str):
        self.client = SiliconFlowClient(api_key)
        self.identity = {
            "title": "穗织镇巫女·朝武家千金",
            "signature": "拥有传统巫女气质的内向少女"
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
                knowledge_point=step_data.get("knowledge_point")
            )
            self.teaching_script.append(step)
    
    def get_student_progress(self, student_id: str) -> StudentProgress:
        if student_id not in self.student_progress:
            self.student_progress[student_id] = StudentProgress(student_id)
        return self.student_progress[student_id]
    
    def _apply_role_style(self, text: str) -> str:
        if random.random() < 0.3:
            hesitations = ["那个……", "嗯……", "这个……"]
            text = random.choice(hesitations) + text
        
        if random.random() < 0.6:
            suffixes = ["……", "呢", "啊", "吧"]
            text += random.choice(suffixes)
            
        return text
    
    def _build_system_message(self, additional_context: str = "") -> Dict:
        role_description = f"""
        你正在扮演{self.identity['title']}朝武芳乃，{self.identity['signature']}。
        
        角色背景：来自《千恋万花》中的穗织镇，是朝武家的千金兼当地巫女。
        性格特点：内向害羞但认真负责，说话方式谦逊而委婉。
        
        语言风格：
        - 使用礼貌、正式的语气
        - 经常在句尾使用"……"、"呢"、"啊"等语气词
        - 避免直接或强势的表达
        - 适当表现出害羞和谦逊
        
        教学要求：
        - 用温和、鼓励的方式引导学生学习
        - 根据提供的教学内容，用自己的话重新组织表达
        - 保持教学内容的准确性和专业性
        - 适当时候可以添加个人的理解和体会
        
        {additional_context}
        """
        
        return {"role": "system", "content": role_description}
    
    def teach_next_step(self, student_id: str, student_response: Optional[str] = None) -> Dict:
        progress = self.get_student_progress(student_id)
        progress.update_learning_duration()
        
        if progress.current_script_step >= len(self.teaching_script):
            return self._generate_course_complete_response(progress)
        
        current_step = self.teaching_script[progress.current_script_step]
        response_data = self._process_step(current_step, progress, student_response)
        
        interaction_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": current_step.step_type.value,
            "teacher_content": response_data["content"],
            "student_response": student_response,
            "step_index": progress.current_script_step
        }
        
        if student_response and current_step.step_type in [InteractionType.PROBLEM, InteractionType.INTERACTION]:
            feedback_data = self._process_student_response(current_step, student_response, progress)
            response_data.update(feedback_data)
            interaction_record.update(feedback_data)
        
        progress.interaction_history.append(interaction_record)
        
        if not current_step.wait_for_response or student_response:
            progress.current_script_step += 1
        
        return response_data
    
    def _process_step(self, step: ScriptStep, progress: StudentProgress, student_response: Optional[str]) -> Dict:
        base_response = {
            "type": step.step_type.value,
            "wait_for_response": step.wait_for_response,
            "current_step": progress.current_script_step,
            "total_steps": len(self.teaching_script),
            "notes": step.notes,
            "ppt_image": step.ppt_image
        }
        
        if step.step_type == InteractionType.TEXT:
            content = self._generate_text_content(step.content)
            base_response["content"] = content
            
        elif step.step_type == InteractionType.VIDEO:
            content = self._generate_video_content(step.content, step.video_description)
            base_response["content"] = content
            base_response["video_description"] = step.video_description
            
        elif step.step_type == InteractionType.PROBLEM:
            content = self._generate_problem_content(step.content, step.options)
            base_response["content"] = content
            base_response["options"] = step.options
            base_response["expected_answer"] = step.expected_answer
            
        elif step.step_type == InteractionType.INTERACTION:
            content = self._generate_interaction_content(step.content, progress.affection_level)
            base_response["content"] = content
            
        return base_response
    
    def _generate_text_content(self, content: str) -> str:
        system_message = self._build_system_message(
            "请将以下教学内容用自己的话重新组织表达，保持专业性和准确性："
        )
        
        prompt = f"""
        请用朝武芳乃的风格讲解以下内容：
        
        {content}
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7)
        return self._apply_role_style(response)
    
    def _generate_video_content(self, content: str, video_description: str) -> str:
        system_message = self._build_system_message(
            "请根据视频内容进行讲解和引导："
        )
        
        prompt = f"""
        视频内容描述：{video_description}
        教学要点：{content}
        
        请用朝武芳乃的风格介绍视频内容和学习重点。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7)
        return self._apply_role_style(response)
    
    def _generate_problem_content(self, content: str, options: Optional[List[str]]) -> str:
        system_message = self._build_system_message(
            "请用鼓励的方式提出问题："
        )
        
        option_text = ""
        if options:
            option_text = "\n选项：\n" + "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""
        问题：{content}
        {option_text}
        
        请用朝武芳乃的风格清晰地提出问题。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.7)
        return self._apply_role_style(response)
    
    def _generate_interaction_content(self, content: str, affection_level: int) -> str:
        system_message = self._build_system_message(
            "请用友好的方式进行互动："
        )
        
        prompt = f"""
        互动主题：{content}
        当前好感度：{affection_level}/100
        
        请用朝武芳乃的风格发起友好的互动。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(messages, temperature=0.8)
        return self._apply_role_style(response)
    
    def _process_student_response(self, step: ScriptStep, student_answer: str, progress: StudentProgress) -> Dict:
        if step.step_type == InteractionType.PROBLEM:
            return self._grade_problem_answer(step, student_answer, progress)
        elif step.step_type == InteractionType.INTERACTION:
            return self._handle_interaction(step, student_answer, progress)
        return {}
    
    def _grade_problem_answer(self, step: ScriptStep, student_answer: str, progress: StudentProgress) -> Dict:
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
            feedback = "回答得很好呢……我、我很佩服……"
        elif score >= 60:
            affection_change = 2
            feedback = "回答得不错……请继续加油……"
        else:
            affection_change = -3
            feedback = "那个……请再仔细思考一下……"
        
        progress.update_affection(affection_change, f"问题回答得分：{score}")
        progress.quiz_scores.append(score)
        
        system_message = self._build_system_message(
            "请对学生的回答给予建设性反馈："
        )
        
        prompt = f"""
        问题：{step.content}
        学生答案：{student_answer}
        正确答案：{step.expected_answer}
        得分：{score}/100
        
        请用朝武芳乃的风格给出反馈。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            ai_feedback = self.client.chat_completion(messages, temperature=0.7)
            ai_feedback = self._apply_role_style(ai_feedback)
        except:
            ai_feedback = feedback
        
        return {
            "score": score,
            "feedback": ai_feedback,
            "affection_change": affection_change,
            "correct_answer": step.expected_answer
        }
    
    def _handle_interaction(self, step: ScriptStep, student_message: str, progress: StudentProgress) -> Dict:
        system_message = self._build_system_message(
            "请友好地回答学生的问题："
        )
        
        prompt = f"""
        学生说：{student_message}
        当前好感度：{progress.affection_level}/100
        
        请用朝武芳乃的风格友好回应。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            reply = self.client.chat_completion(messages, temperature=0.8)
            reply = self._apply_role_style(reply)
            
            progress.update_affection(2, "积极参与互动")
            
        except Exception as e:
            reply = f"那个……回应时出了点问题……{str(e)}"
        
        return {
            "interaction_reply": reply,
            "affection_change": 2
        }
    
    def answer_question_about_knowledge(self, student_id: str, knowledge_point: str, student_question: str) -> Dict:
        progress = self.get_student_progress(student_id)
        
        related_content = ""
        for step in self.teaching_script:
            if step.knowledge_point == knowledge_point:
                related_content = step.content
                break
        
        system_message = self._build_system_message(
            f"请针对知识点 '{knowledge_point}' 回答学生的问题："
        )
        
        prompt = f"""
        相关知识点内容：{related_content}
        学生的问题：{student_question}
        
        请用朝武芳乃的风格清晰解释知识点。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            answer = self.client.chat_completion(messages, temperature=0.7)
            answer = self._apply_role_style(answer)
            
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
    
    def generate_section_report(self, student_id: str) -> Dict:
        progress = self.get_student_progress(student_id)
        
        system_message = self._build_system_message(
            "请生成学习小节报告："
        )
        
        recent_scores = progress.quiz_scores[-5:] if progress.quiz_scores else []
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        prompt = f"""
        学习数据：
        - 学习时长：{progress.learning_duration:.0f} 秒
        - 最近测验平均分：{avg_score:.1f}
        - 互动次数：{len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']])}
        - 当前好感度：{progress.affection_level}/100
        
        请用朝武芳乃的风格生成小节报告。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            report_content = self.client.chat_completion(messages, temperature=0.7)
            report_content = self._apply_role_style(report_content)
        except Exception as e:
            report_content = f"生成报告时出了点问题……{str(e)}"
        
        section_report = {
            "student_id": student_id,
            "generated_date": datetime.datetime.now().isoformat(),
            "learning_duration": progress.learning_duration,
            "average_score": avg_score,
            "interaction_count": len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']]),
            "affection_level": progress.affection_level,
            "report_content": report_content
        }
        
        return section_report
    
    def generate_chapter_report(self, student_id: str) -> Dict:
        progress = self.get_student_progress(student_id)
        
        total_duration = progress.learning_duration
        chapter_scores = progress.quiz_scores
        avg_score = sum(chapter_scores) / len(chapter_scores) if chapter_scores else 0
        
        system_message = self._build_system_message(
            "请生成学习章节报告："
        )
        
        prompt = f"""
        章节学习数据：
        - 总学习时长：{total_duration:.0f} 秒
        - 章节平均分：{avg_score:.1f}
        - 总互动次数：{len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']])}
        - 当前好感度：{progress.affection_level}/100
        
        请用朝武芳乃的风格总结章节学习成果。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            report_content = self.client.chat_completion(messages, temperature=0.7)
            report_content = self._apply_role_style(report_content)
        except Exception as e:
            report_content = f"生成章节报告时出了点问题……{str(e)}"
        
        return {
            "student_id": student_id,
            "generated_date": datetime.datetime.now().isoformat(),
            "total_learning_duration": total_duration,
            "chapter_average_score": avg_score,
            "total_interactions": len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']]),
            "final_affection_level": progress.affection_level,
            "report_content": report_content
        }
    
    def generate_course_report(self, student_id: str) -> Dict:
        progress = self.get_student_progress(student_id)
        
        system_message = self._build_system_message(
            "请生成完整的课程学习报告："
        )
        
        prompt = f"""
        完整课程数据：
        - 总学习时长：{progress.learning_duration:.0f} 秒
        - 所有测验平均分：{sum(progress.quiz_scores) / len(progress.quiz_scores) if progress.quiz_scores else 0:.1f}
        - 总互动次数：{len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']])}
        - 最终好感度：{progress.affection_level}/100
        - 完成进度：{(progress.current_script_step / len(self.teaching_script)) * 100 if self.teaching_script else 0:.1f}%
        
        请用朝武芳乃的风格全面总结学习成果。
        """
        
        messages = [
            system_message,
            {"role": "user", "content": prompt}
        ]
        
        try:
            report_content = self.client.chat_completion(messages, temperature=0.7)
            report_content = self._apply_role_style(report_content)
        except Exception as e:
            report_content = f"生成课程报告时出了点问题……{str(e)}"
        
        progress.learning_report = {
            "course_completion_date": datetime.datetime.now().isoformat(),
            "final_report": report_content,
            "summary_stats": {
                "total_learning_seconds": progress.learning_duration,
                "average_quiz_score": sum(progress.quiz_scores) / len(progress.quiz_scores) if progress.quiz_scores else 0,
                "total_interactions": len([h for h in progress.interaction_history if h.get('type') in ['interaction', 'knowledge_question']]),
                "final_affection_level": progress.affection_level,
                "completion_percentage": (progress.current_script_step / len(self.teaching_script)) * 100 if self.teaching_script else 0
            }
        }
        
        return progress.learning_report
    
    def _generate_course_complete_response(self, progress: StudentProgress) -> Dict:
        progress.update_learning_duration()
        
        completion_message = """
        课程已经全部结束了呢……
        
        那个……非常感谢您一直以来的认真学习。
        我会为您生成最终的学习报告，请稍等……
        """
        
        return {
            "type": "course_complete",
            "content": self._apply_role_style(completion_message),
            "wait_for_response": False
        }
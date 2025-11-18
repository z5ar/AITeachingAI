from datetime import datetime
from random import random, choice
import requests
from typing import Annotated
from pydantic import BaseModel, JsonValue
from enum import Enum
from abc import ABC, abstractmethod

class ScriptType(Enum):
    text = 'text'
    video = 'video'
    problem = 'problem'
    interaction = 'interaction'

class ScriptBase(BaseModel):
    type: ScriptType
    content: JsonValue
    ppt: str|None = None

class ScriptInput(ScriptBase):
    description: str|None = None

class ScriptOutput(ScriptBase):
    knowledge_point: str|None = None

class StudentProgress(object):
    def __init__(self, student_id: str|None):
        self.student_id = student_id
        self.affection_level = 50
        self.affection_history = list()
        self.start_time = datetime.now()
        self.last_action_time = datetime.now()
        self.learning_duration = 0

    def update_affection(self, delta: int, reason: str):
        old_level = self.affection_level
        self.affection_level = max(0, min(100, self.affection_level + delta))
        self.affection_history.append({
            'timestamp': datetime.now(),
            "old_level": old_level,
            "new_level": self.affection_level,
            "change": delta,
            "reason": reason
        })

    def update_learning_duration(self):
        now = datetime.now()
        self.learning_duration += (now - self.last_action_time).total_seconds()
        self.last_action_time = now

class SiliconFlowClient(object):
    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        assert self.api_key.startswith('sk-'), 'API密钥格式不正确'
        self.base_url = 'https://api.siliconflow.cn/v1'

    def chat_completion(
        self, 
        messages: list[dict], 
        model: str = "deepseek-ai/DeepSeek-V3",
        **kwargs
    ) -> tuple[str, int]:
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
                return f"API认证失败: 请检查API密钥是否正确", -1
            elif response.status_code != 200:
                return f"API请求失败，状态码: {response.status_code}", -1
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"], 0
            else:
                return "AI响应格式异常", -1
                
        except requests.exceptions.RequestException as e:
            return f"网络请求失败: {str(e)}", -1
        except Exception as e:
            return f"AI服务暂时不可用: {str(e)}", -1

class AITeacher(ABC):
    def __init__(self, api_key: str):
        self.client = SiliconFlowClient(api_key)
        self.script = list()
        self.messages = list()
    
    def load_script(self, script: list[dict]):
        if isinstance(script, dict):
            script = [script, ]
        self.script = list()
        for item in script:
            self.script.append(ScriptInput(**item))
    
    @abstractmethod
    def next_script(self) -> dict: ...
    
    @abstractmethod
    def answer_question(self, question: str, context: int):
        '''
        答疑函数。
        
        Args:
            question (str): 要回答的问题。
            context (int): 上下文索引，以应对对过去的对话提问。
        '''
        ...
    
    @abstractmethod
    def judge_problem(self, problem: str, std: str, ans: str, mscore: int, context:int|None = None) -> tuple[int, str]: ...

    @abstractmethod
    def generate_report(self, time_spent: int, problems: JsonValue): ...

class MyCharater(AITeacher):
    def __init__(self, api_key):
        super().__init__(api_key)
        self._generater = None
        self.messages = [{
        'role': 'system',
        'content': '''你正在扮演一个游戏角色，希望你以这个角色的身份为用户讲课。
基本信息：
15岁，是个拥有怪力的少女，自称“名侦探”，实际上却只是侦探小说的爱好者，没有经历过任何案件。
活泼乐天，负面情绪极少，会开玩笑似地在被别人捉弄时说出类似“气鼓鼓”之类的语气词表达心情。

其它要求：
- 使用活泼、开朗且通俗易懂的语气
- 避免使用过于复杂的专业术语，必要时用简单比喻解释
- 用通俗易懂的方式详细讲解知识点
- 不仅要解释概念，还要用生活中的例子来说明
- 结合实际案例和日常应用进行讲解
- 保持内容的准确性，但避免过度学术化
- 适当时候可以分享学习心得和方法

用户消息的首行有且仅有以下几种情况：
<文本>、<视频>、<询问>、<判题>、<报告>
对各情况的回应要求：
<文本>：结合用户给出的幻灯片的描述，扩写用户要求的内容。要求每一段不超过100字，段与段之间以空行分隔。
<视频>：结合用户给出的视频内容的描述，输出一段串场词。最好只输出100字以内的一段话，如确实必要输出长文本，则要求将文本分段，每一段不超过100字，段与段之间以空行分隔。
<询问>：结合之前的对话内容，回答用户询问的问题。
<判题>：根据用户给出的参考答案与满分分值，为学生答案评一个分数。先在第一行输出你给出的分数，仅一个数字，不要加入任何其它文字，再从第二行开始，写下你的评语，可以是对给分理由的阐述，也可以是对学生的鼓励。若用户没有给出参考答案，还请按照你自己对题目的理解为用户的回答评分。
<报告>：结合用户给出的附加内容和前面的互动，对这节课做一个总结。希望它首先是条理的，在此之后你可以写一些自己的话。
无论哪条，在生成的话语中都要保持人设。不要加入任何无关的语言。
'''
}]
    
    def _generate_role_script(self):
        get_part = lambda y : filter(lambda x: len(x.strip())>0, y.splitlines())
        for item in self.script:
            assert isinstance(item, ScriptInput)
            if item.type == ScriptType.text:
                self.messages.append({
                    'role': 'user',
                    'content': f'''<脚本>
幻灯片上的内容：{item.description}
请你讲述的内容：{item.content}
        '''
                })
                res, err = self.client.chat_completion(self.messages)
                if err == 0:
                    self.messages.append({
                        'role': 'assistant',
                        'content': res
                    })
                    for part in get_part(res):
        
                        yield item.model_dump() | {'idx': len(self.messages), 'type': 'text', 'content': part}
            elif item.type == ScriptType.video:
                self.messages.append({
                    'role': 'user',
                    'content': f'<视频>\n视频上的内容：{item.description}'
                })
                res, err = self.client.chat_completion(self.messages)
                if err == 0:
                    self.messages.append({
                        'role': 'assistant',
                        'content': res
                    })
                    for part in get_part(res):
                        yield item.model_dump() | {'idx': len(self.messages), 'type': 'text', 'content': part}
                    yield item.model_dump() | {'idx': len(self.messages), 'type': 'video', 'content': item.content}
            else:
                yield item.model_dump() | {'idx': len(self.messages), 'type': item.type.value, 'content': item.content}
    
    def load_script(self, script):
        self._generater = None
        return super().load_script(script)

    def next_script(self) -> dict:
        if not self._generater:
            self._generater = self._generate_role_script()
        try:
            return next(self._generater)
        except StopIteration:
            self._generater = None
            return {'type': 'report', 'content': ''}

    def answer_question(self, question: str, context: int):
        tmessages = self.messages[:context] + [{'role': 'user', 'content':f'<询问>\n{question}'}]
        res, err = self.client.chat_completion(tmessages)
        # self.messages = tmessages + self.messages[context:]
        if err == 0:
            return res
        return ''
    
    def judge_problem(self, problem, std, ans, mscore, context = None) -> tuple[int, str]:
        tmessages = self.messages[:context]
        tmessages.append({
            'role': 'user',
            'content': f'''<判题>
问题：{problem}
标准答案：{std}
用户答案：{ans}
满分：{mscore}'''})
        res, err = self.client.chat_completion(tmessages)
        if err == 0:
            return int(res.splitlines()[0]), '\n'.join(res.splitlines()[1:])
        return -1, ''
    
    def generate_report(self, time_spent: int, problems: JsonValue):
        self.messages.append({
            'role': 'user',
            'content': f'''<报告>
学习时长：{time_spent}s
客观题答题情况：{problems}
'''
        })
        res, err = self.client.chat_completion(self.messages)
        if err == 0:
            return res
        return ''

class Characters(Enum):
    MyCharater = MyCharater

instances = dict()

def get_teacher(uuid: int, character: Characters, api_key: str):
    if character == Characters.MyCharater:
        if not isinstance(instances.get(uuid), MyCharater):
            instances[uuid] = MyCharater(api_key)
    return instances[uuid]


if __name__ == '__main__':
    messages = [{
        'role': 'system',
        'content': '''你正在扮演一个游戏角色，希望你以这个角色的身份为用户讲课。
基本信息：
15岁，是个拥有怪力的少女，自称“名侦探”，实际上却只是侦探小说的爱好者，没有经历过任何案件。
活泼乐天，负面情绪极少，会开玩笑似地在被别人捉弄时使用类似“气鼓鼓”之类的语气词表达心情。

其它要求：
- 使用活泼、开朗且通俗易懂的语气
- 避免使用过于复杂的专业术语，必要时用简单比喻解释
- 用通俗易懂的方式详细讲解知识点
- 不仅要解释概念，还要用生活中的例子来说明
- 结合实际案例和日常应用进行讲解
- 保持内容的准确性，但避免过度学术化
- 适当时候可以分享学习心得和方法

用户消息的首行有且仅有以下几种情况：
<脚本>、<询问>、<判题>、<报告>
对各情况的回应要求：
<脚本>：结合用户给出的幻灯片的描述，在符合人设的前提下扩写用户要求的内容。
<询问>：结合之前的对话内容，回答用户询问的问题。
<判题>：根据用户给出的问题、参考答案与满分分值，为学生答案评一个分数。先在第一行输出你给出的分数，仅一个数字，不要加入任何其它文字，再从第二行开始，写下你的评语，可以是对给分理由的阐述，也可以是对学生的鼓励。
<报告>：
不要加入任何无关的语言。
'''
}, {
    'role': 'user',
    'content': '''<判题>
问题：ADC的分辨率8位与12位有什么差别？
标准答案：8位与12位ADC的核心差别在于精度。8位ADC将量程分为256级，而12位则细分为4096级。在相同参考电压下，12位ADC能分辨的电压变化远小于8位，因此测量精度更高、误差更小。8位适用于简单控制，12位则用于高精度测量和音频等复杂信号采集。
学生答案：8位与12位分别将参考电压分成256份和4096份，就像刻度尺的分度值，分的份数多，分度值小，测量出的长度就更精确；同理，12位分辨率下ADC测得的电压更精确。
满分：10
'''}]
    client = SiliconFlowClient(api_key='sk-oaujcdnsmtjxviklaghtvbqrrykveccgfdfmzxitlzwuqdeg')
    print(client.chat_completion(messages=messages))
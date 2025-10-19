from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import os

class AIResponse:
    _model_name: str
    _API_key: str
    _chat_model: ChatOpenAI

    def __init__(self, model_name: str, API_key: str):
        self._model_name = model_name
        self._API_key = API_key
        os.environ["OPENAI_API_KEY"] = self._API_key
        self._chat_model = ChatOpenAI(model_name=self._model_name, temperature=0.7)

    def judge_answer(
            self,
            ans: str,
            std: str,
            problem: str,
            mscore: int
    ) -> tuple[int, str]:
        '''
        使用AI为回答打分，并给出评语。

        Args:
            ans (str): 学生答案，需要被评判的答案
            std (str): 标准答案，评判的依据
            problem (str): 原始问题，供AI参考用
            mscore (int): 以该分数为满分

        Returns:
            score (int): AI判断该答案可以得到的分数
            comment (str): AI给出的评语
        '''

        prompt = f'''
        请根据以下标准答案和学生答案进行评分。
        标准答案: {std}
        学生答案: {ans}
        问题: {problem}
        满分: {mscore}

        请给出一个0到{mscore}之间的整数分数，并简要说明评分理由。
        '''

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        response_text = response.content.strip()

        try:
            score_line, comment = response_text.split('\n', 1)
            score = int(score_line.split()[0])
            score = max(0, min(score, mscore))  # 确保分数在合理范围内
        except Exception:
            score = 0
            comment = "评分失败，未能解析AI的回复。"

        return score, comment
    
    def answer_question(
            self,
            question: str
    ) -> str:
        '''
        使用AI回答问题。

        Args:
            question (str): 需要AI回答的问题

        Returns:
            answer (str): AI给出的答案
        '''

        prompt = f'''
        请回答以下问题：
        {question}
        '''

        response = self._chat_model.predict_messages([HumanMessage(content=prompt)])
        answer = response.content.strip()

        return answer
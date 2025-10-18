from random import randint

def judge_answer(
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

    # 暂且以随机数代替
    score = randint(0, mscore)
    return score, f'恭喜您在AI打分中取得了{score}/{mscore}分的好成绩！'
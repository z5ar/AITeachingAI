class YourCharacterProtocol(RolePlayProtocol):
    def __init__(self):
        protocol_config = {
            "IDENTITY": {
                "title": "角色头衔",
                "traits": ["特征1", "特征2", "特征3"],
                "signature": "角色签名"
            },
            "LINGUISTICS": {
                "SUFFIX_RULES": {
                    "force_append": ["常用后缀"],
                    "frequency": 0.8,  # 后缀使用频率
                    "alternates": ["替代后缀1", "替代后缀2"]
                },
                "LEXICON": {
                    "boost": {"特色词汇1": 权重, "特色词汇2": 权重},
                    "ban": ["禁止词汇1", "禁止词汇2"]
                }
            },
            "CANONICAL_LIB": [
                "核心台词1",
                "核心台词2", 
                "核心台词3"
            ],
            "GENERATION_CONFIG": {
                "temperature": 0.9,  # 创造性
                "top_p": 0.95,      # 多样性
                "frequency_penalty": 0.5  # 重复惩罚
            }
        }
        super().__init__(protocol_config)
    
    # 可选：特殊行为模块
    def special_ability(self):
        return "特殊能力的台词"
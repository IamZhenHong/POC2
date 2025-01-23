from pydantic import BaseModel
from typing import Optional

class LoveAnalysisBase(BaseModel):
    previous_love_analysis: str
    current_convo: str

class LoveAnalysisCreate(LoveAnalysisBase):
    new_love_analysis: str  # Add this field to match the input data

class LoveAnalysis(LoveAnalysisBase):
    id: int

    class Config:
        from_attributes = True

class StyleBase(BaseModel):
    previous_style: str
    current_convo: str

class StyleCreate(StyleBase):
    pass

class Style(StyleBase):
    id: int
    new_style: str

    class Config:
        from_attributes = True

class ChatStrategyBase(BaseModel):
    new_love_analysis: str

class ChatStrategyCreate(ChatStrategyBase):
    pass

class ChatStrategy(ChatStrategyBase):
    id: int
    chat_strategy: str

    class Config:
        from_attributes = True

class ReplyOptionsFlowBase(BaseModel):
    new_chat_strategy: str
    new_love_analysis: str
    current_convo: str

class ReplyOptionsFlowCreate(ReplyOptionsFlowBase):
    pass

class ReplyOptionsFlow(ReplyOptionsFlowBase):
    id: int
    reply_options_flow: str

    class Config:
        from_attributes = True

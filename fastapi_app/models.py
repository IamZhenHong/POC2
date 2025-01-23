from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class LoveAnalysis(Base):
    __tablename__ = "love_analysis"

    id = Column(Integer, primary_key=True, index=True)
    previous_love_analysis = Column(String)
    current_convo = Column(String)
    new_love_analysis = Column(String)

    # Removed the user_id reference
    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="love_analyses")

class Style(Base):
    __tablename__ = "styles"

    id = Column(Integer, primary_key=True, index=True)
    previous_style = Column(String)
    current_convo = Column(String)
    new_style = Column(String)

    # Removed the user_id reference
    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="styles")

class ChatStrategy(Base):
    __tablename__ = "chat_strategies"

    id = Column(Integer, primary_key=True, index=True)
    new_love_analysis = Column(String)
    chat_strategy = Column(String)

    # Removed the user_id reference
    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="chat_strategies")

class ReplyOptionsFlow(Base):
    __tablename__ = "reply_options_flows"

    id = Column(Integer, primary_key=True, index=True)
    new_chat_strategy = Column(String)
    new_love_analysis = Column(String)
    current_convo = Column(String)
    reply_options_flow = Column(String)

    # Removed the user_id reference
    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="reply_options_flows")

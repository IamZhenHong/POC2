from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, Base, get_db
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Initialize FastAPI
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Routes for Love Analysis
@app.post("/love_analysis/", response_model=schemas.LoveAnalysis)
def create_love_analysis(love_analysis: schemas.LoveAnalysisBase, db: Session = Depends(get_db)):
    new_love_analysis = models.LoveAnalysis(
        previous_love_analysis=love_analysis.previous_love_analysis,
        current_convo=love_analysis.current_convo,
        new_love_analysis=love_analysis.new_love_analysis
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "user", "content": "write a haiku about ai"}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI error: {str(e)}")


@app.get("/love_analysis/{love_analysis_id}", response_model=schemas.LoveAnalysis)
def get_love_analysis(love_analysis_id: int, db: Session = Depends(get_db)):
    love_analysis = db.query(models.LoveAnalysis).filter(models.LoveAnalysis.id == love_analysis_id).first()
    if not love_analysis:
        raise HTTPException(status_code=404, detail="Love Analysis not found")
    return love_analysis

# Routes for Style
@app.post("/styles/", response_model=schemas.Style)
def create_style(style: schemas.StyleCreate, db: Session = Depends(get_db)):
    new_style = models.Style(
        previous_style=style.previous_style,
        current_convo=style.current_convo,
        new_style=style.new_style
    )
    db.add(new_style)
    db.commit()
    db.refresh(new_style)
    return new_style

@app.get("/styles/{style_id}", response_model=schemas.Style)
def get_style(style_id: int, db: Session = Depends(get_db)):
    style = db.query(models.Style).filter(models.Style.id == style_id).first()
    if not style:
        raise HTTPException(status_code=404, detail="Style not found")
    return style

# Routes for Chat Strategy
@app.post("/chat_strategies/", response_model=schemas.ChatStrategy)
def create_chat_strategy(chat_strategy: schemas.ChatStrategyCreate, db: Session = Depends(get_db)):
    new_chat_strategy = models.ChatStrategy(
        new_love_analysis=chat_strategy.new_love_analysis,
        chat_strategy=chat_strategy.chat_strategy
    )
    db.add(new_chat_strategy)
    db.commit()
    db.refresh(new_chat_strategy)
    return new_chat_strategy

@app.get("/chat_strategies/{chat_strategy_id}", response_model=schemas.ChatStrategy)
def get_chat_strategy(chat_strategy_id: int, db: Session = Depends(get_db)):
    chat_strategy = db.query(models.ChatStrategy).filter(models.ChatStrategy.id == chat_strategy_id).first()
    if not chat_strategy:
        raise HTTPException(status_code=404, detail="Chat Strategy not found")
    return chat_strategy

# Routes for Reply Options Flow
@app.post("/reply_options_flows/", response_model=schemas.ReplyOptionsFlow)
def create_reply_options_flow(reply_options_flow: schemas.ReplyOptionsFlowCreate, db: Session = Depends(get_db)):
    new_reply_options_flow = models.ReplyOptionsFlow(
        new_chat_strategy=reply_options_flow.new_chat_strategy,
        new_love_analysis=reply_options_flow.new_love_analysis,
        current_convo=reply_options_flow.current_convo,
        reply_options_flow=reply_options_flow.reply_options_flow
    )
    db.add(new_reply_options_flow)
    db.commit()
    db.refresh(new_reply_options_flow)
    return new_reply_options_flow

@app.get("/reply_options_flows/{reply_options_flow_id}", response_model=schemas.ReplyOptionsFlow)
def get_reply_options_flow(reply_options_flow_id: int, db: Session = Depends(get_db)):
    reply_options_flow = db.query(models.ReplyOptionsFlow).filter(models.ReplyOptionsFlow.id == reply_options_flow_id).first()
    if not reply_options_flow:
        raise HTTPException(status_code=404, detail="Reply Options Flow not found")
    return reply_options_flow

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, Base, get_db
from openai import OpenAI
import os
from dotenv import load_dotenv
from sqlalchemy import desc
import json
# Load environment variables
load_dotenv()


openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Initialize FastAPI
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/targets/", response_model=schemas.TargetOut)
def create_target(target: schemas.TargetCreate, db: Session = Depends(get_db)):
    db_target = models.Target(**target.dict())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target


# Routes for Love Analysis
@app.post("/love_analysis/", response_model=schemas.LoveAnalysisOut)
def create_love_analysis(love_analysis: schemas.LoveAnalysisCreate, db: Session = Depends(get_db)):
    if not love_analysis.target_id:
        raise HTTPException(status_code=400, detail="Target ID is required.")

    new_convo_snippet = models.ConversationSnippet(content=love_analysis.convo, target_id=love_analysis.target_id)
    db.add(new_convo_snippet)
    db.commit()
    db.refresh(new_convo_snippet)

    target = db.query(models.Target).filter(models.Target.id == love_analysis.target_id).first()

    previous_love_analysis = (
        db.query(models.LoveAnalysis)
        .order_by(desc(models.LoveAnalysis.created_at))
        .first()
    )
    previous_love_analysis_content = previous_love_analysis.content if previous_love_analysis else "None"
    print(f"Latest Love Analysis: {previous_love_analysis_content}")

    try:
        prompt = f"""
        You are a love coach who is very good at analysing the relationship dynamics, personalities, latent feeling and of both parties.  I'm your client seeking your advice. 
        ###
        Analyse chat history example and relationship info provided and output the following analysis
        1. general relationship dynamic
        2. how I present myself in front of the other party
        3. how the other party most likely see me and feel about me; 
        4. what the other party most likely need from our interaction or relationship
        5. my personalities shown in the conversation
        6.  the other party's personality shown in the conversation
        7.  what the other party are likely to do next in our interactions
        8. overall advice if I want to achieve my relationship goals
        ###
        Previous Love Analysis:
        {previous_love_analysis_content}

        Current Conversation:
        {love_analysis.convo}

        New Love Analysis:
        """

        # Call the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"""Output in {target.language}:"""}
            ]
        )
        current_love_analysis_content = completion.choices[0].message.content


        new_love_analysis = models.LoveAnalysis(
            convo=love_analysis.convo,
            content=current_love_analysis_content,
            target_id=love_analysis.target_id
        )

        db.add(new_love_analysis)
        db.commit()
        db.refresh(new_love_analysis)
        return schemas.LoveAnalysisOut(
            content = current_love_analysis_content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Azure OpenAI error: {str(e)}")


# # Not solved yet
# @app.get("/love_analysis/{love_analysis_id}", response_model=schemas.LoveAnalysis)
# def get_love_analysis(love_analysis_id: int, db: Session = Depends(get_db)):
#     love_analysis = db.query(models.LoveAnalysis).filter(models.LoveAnalysis.id == love_analysis_id).first()
#     print(f"Queried Love Analysis: {love_analysis}")
#     if not love_analysis:
#         raise HTTPException(status_code=404, detail="Love Analysis not found")
#     return love_analysis


# # Routes for Style
# @app.post("/styles/", response_model=schemas.Style)
# def create_style(style: schemas.StyleCreate, db: Session = Depends(get_db)):
#     previous_style = (
#         db.query(models.Style)
#         .order_by(desc(models.Style.created_at))
#         .first()
#     )
#     previous_style_content = previous_style.content if previous_style else "None"
#     prompt = ""
#     completion = client.chat.completions.create(
#             model="gpt-4o",
#             store=True,
#             messages=[
#                 {"role": "system", "content": "Y"},
#                 {"role": "user", "content": prompt}
#             ]
#         )
#     db.add(new_style)
#     db.commit()
#     db.refresh(new_style)
#     return new_style

# @app.get("/styles/{style_id}", response_model=schemas.Style)
# def get_style(style_id: int, db: Session = Depends(get_db)):
#     style = db.query(models.Style).filter(models.Style.id == style_id).first()
#     if not style:
#         raise HTTPException(status_code=404, detail="Style not found")
#     return style

# Routes for Chat Strategy
@app.post("/chat_strategies/", response_model=schemas.ChatStrategyOut)
def create_chat_strategy(chat_strategy: schemas.ChatStrategyCreate, db: Session = Depends(get_db)):
    target = db.query(models.Target).filter(models.Target.id == chat_strategy.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    latest_love_analysis = (
        db.query(models.LoveAnalysis)
        .order_by(desc(models.LoveAnalysis.created_at))
        .first()
    )
    latest_convo_snippet = (
        db.query(models.ConversationSnippet)
        .order_by(desc(models.ConversationSnippet.created_at))
        .first()
    )
    latest_chat_strategy = (
        db.query(models.ChatStrategy)
        .order_by(desc(models.ChatStrategy.created_at))
        .first()
    )


    print (f"Latest Love Analysis: {latest_love_analysis.content}")
    print (f"Latest Convo Snippet: {latest_convo_snippet.content}")

    if not latest_love_analysis or not latest_convo_snippet:
        raise HTTPException(status_code=404, detail="Latest Love Analysis or Conversation Snippet not found")

    latest_chat_strategy_content = latest_chat_strategy.content if latest_chat_strategy else "None"
    latest_love_analysis_content = latest_love_analysis.content if latest_love_analysis else "None"
    latest_convo_snippet_content = latest_convo_snippet.content  if latest_convo_snippet else "None"
    
    system_prompt = f"""
        You are a love coach who is very good at helping clients come up with the right strategy and exact reply in communication to reach their short-term and long-term relationship goals. I'm your client seeking your advice.

        Come up with a communication strategy that is brief, easy to follow, and actionable for me to talk to {target.name} based on the context below.
        Output in {target.language}:
        Context: 
        """
    system_prompt += f"""
        my gender: {target.gender}
        I'm talking to {target.name} online
        {target.name}'s gender: {target.gender}
        {target.name}'s personality: {target.personality}
        relationship context: {target.relationship_context}
        my feelings about our relationship: {target.relationship_perception}
        my short-term goal with {target.name}: {target.relationship_goals}
        my long-term goal with {target.name}: {target.relationship_goals_long}
        relationship dynamics:
        {latest_love_analysis_content}
        Last conversation snippet: {latest_convo_snippet_content}
        Last chat strategy: {latest_chat_strategy_content}
        """

    # user_prompt = f"""Here is the context for generating a chat strategy:

    #     Current Conversation:
    #     "{latest_convo_snippet_content}"

    #     Love Analysis:
    #     "{latest_love_analysis_content}"

    #     Please create a thoughtful and detailed chat strategy that helps address the issues discussed in the conversation and analysis.
    #     """

    user_prompt = f""" Output in {target.language}: """

    print ("User Prompt___________________________________________-: ", user_prompt)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        store=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format= schemas.ChatStrategyOut
    )

    chat_strategy_content = completion.choices[0].message.parsed.content
    
    new_chat_strategy = models.ChatStrategy(
        convo = latest_convo_snippet_content,
        love_analysis=latest_love_analysis_content,
        content=chat_strategy_content,
        target_id=chat_strategy.target_id
    )
    db.add(new_chat_strategy)
    db.commit()
    db.refresh(new_chat_strategy)
    return new_chat_strategy

# # Not tested yet
# @app.get("/chat_strategies/{chat_strategy_id}", response_model=schemas.ChatStrategy)
# def get_chat_strategy(chat_strategy_id: int, db: Session = Depends(get_db)):
#     chat_strategy = db.query(models.ChatStrategy).filter(models.ChatStrategy.id == chat_strategy_id).first()
#     if not chat_strategy:
#         raise HTTPException(status_code=404, detail="Chat Strategy not found")
#     return chat_strategy

# Routes for Reply Options Flow
@app.post("/reply_options_flow/", response_model=schemas.ReplyOptionsOut)
def create_reply_options_flow(reply_options: schemas.ReplyOptionsCreate, db: Session = Depends(get_db)):
    
    target = db.query(models.Target).filter(models.Target.id == reply_options.target_id).first()

    latest_convo_snippet = (
        db.query(models.ConversationSnippet)
        .order_by(desc(models.ConversationSnippet.created_at))
        .first()
    )
    latest_chat_strategy = (
        db.query(models.ChatStrategy)
        .order_by(desc(models.ChatStrategy.created_at))
        .first()
    )

    latest_love_analysis = (
        db.query(models.LoveAnalysis)
        .order_by(desc(models.LoveAnalysis.created_at))
        .first()
    )

    latest_love_analysis_content = latest_love_analysis.content if latest_love_analysis else "None"
    latest_convo_snippet_content = latest_convo_snippet.content if latest_convo_snippet else "None"
    latest_chat_strategy_content = latest_chat_strategy.content if latest_chat_strategy else "None"
    
    system_prompt = f"""
        You are a love coach who is very good at helping clients come up with the right strategy and exact reply in communication to reach their short-term and long-term relationship goals. I'm your client seeking your advice.

        Write 4 distinguishable reply options for me to {target.name} as my next reply in the current conversation dialog; based on the communication strategy and context below. Each reply option should explore different directions or aspects of the interaction.
        Output in {target.language}:
        ###
        Current conversation dialog: \"\"\" 
        {latest_convo_snippet_content}
        \"\"\"
        Communication strategy: \"\"\" 
        {latest_chat_strategy_content}
        \"\"\"
        Context: \"\"\" 
        my gender: male
        I'm talking to {target.name} online
        {target.name}'s gender: {target.gender}
        {target.name}'s personality: {target.personality}
        relationship context: {target.relationship_context}
        my feelings about our relationship: {target.relationship_perception}
        my short-term goal with {target.name}: {target.relationship_goals}
        my long-term goal with {target.name}: {target.relationship_goals_long}
        relationship dynamic: {latest_love_analysis_content}
        \"\"\"
        ###
        """
    user_prompt = f""" Output in {target.language}: """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        store=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format= schemas.ReplyOptionsOut
    )
    print("Completion!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!: ", completion)

    new_reply_options_flow = models.ReplyOptionsFlow(
        chat_strategy=latest_chat_strategy_content,
        convo=latest_convo_snippet_content,
        option1 = completion.choices[0].message.parsed.option1,
        option2 = completion.choices[0].message.parsed.option2,
        option3 = completion.choices[0].message.parsed.option3,
        option4 = completion.choices[0].message.parsed.option4,
        target_id=reply_options.target_id
    )
    
    db.add(new_reply_options_flow)
    db.commit()
    db.refresh(new_reply_options_flow)
    return schemas.ReplyOptionsOut(
        option1=completion.choices[0].message.parsed.option1,
        option2=completion.choices[0].message.parsed.option2,
        option3=completion.choices[0].message.parsed.option3,
        option4=completion.choices[0].message.parsed.option4
    )

# @app.get("/reply_options_flows/{reply_options_flow_id}", response_model=schemas.ReplyOptionsFlow)
# def get_reply_options_flow(reply_options_flow_id: int, db: Session = Depends(get_db)):
#     reply_options_flow = db.query(models.ReplyOptionsFlow).filter(models.ReplyOptionsFlow.id == reply_options_flow_id).first()
#     if not reply_options_flow:
#         raise HTTPException(status_code=404, detail="Reply Options Flow not found")
#     return reply_options_flow

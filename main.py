from langchain.llms import OpenAI
import os
openai_key = os.environ.get('OPENAI_API_KEY')
llm=OpenAI(openai_api_key=openai_key)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from fastapi import FastAPI, Body,Path,Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional,List
import json

class File_Path(BaseModel):
    file: str
    location: str

class Prompt(BaseModel):
    Question : str
    Temp : Optional[float] = Field(0.7, gt=0, lt=2)
    Files_To_Read : Optional[List[File_Path]]

def file_reader(file_list: List[File_Path]):
    variable_dict={}
    for item in file_list:
        file_name = item.file
        location = item.location
        with open(location, 'r') as file:
            File_Data = file.read()
        variable_dict[file_name] = File_Data    
    return variable_dict

app=FastAPI()
@app.post("/Prompt")
async def Answer_The_Prompt(req_body: Prompt):
    try:
        template_string=req_body.Question
        chat=ChatOpenAI(openai_api_key=openai_key,temperature=req_body.Temp,model="gpt-3.5-turbo")
        if req_body.Files_To_Read==None:
            variable_dict={}
        else:
            variable_dict=file_reader(req_body.Files_To_Read)
        prompt_template=ChatPromptTemplate.from_template(template_string)
        Content=prompt_template.format_messages(**variable_dict)
        LLM_response = chat(Content)
        return(LLM_response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.{e}")
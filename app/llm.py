
import json
import logging 

from openai import OpenAI
from app.config import settings
from app.schemas import ExtractedTask
from app.tools import calculator,get_current_time

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key,base_url=settings.openai_api_base_url)

def chat_completion(messages: list[dict],temperature: float = 0.2 ) -> str:
    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=messages,
            temperature=temperature
        )

        return response.output_text

    except Exception as e:
        logger.exception("LLM call failed")
        raise RuntimeError(f"LLM call failed: {str(e)}")
    
def extract_task(text: str) -> ExtractedTask:
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role":"system",
                "content": "你是任务识别助手，请从用户文本中提取任务类型，摘要，优先级，是否需要工具。",
            },
            {
                "role": "user",
                "content": text,
            },     
        ],
        text_format=ExtractedTask,
    )

    return response.output_parsed


TOOLS = [
    {
        "type": "function",
        "name": "calculator",
        "description": "计算器工具，提供数学计算功能",
        "parameters":{
            "type":"object",
            "properties":{
                "expression":{
                    "type":"string",
                    "description":"数学表达式，例如：2+2*3",
                }
            },
            "required":["expression"],
            "additionalProperties": False,
        },
    },
    {
        "type":"function",
        "name":"get_current_time",
        "description":"获取当前时间 或者 Get the current time. ",
        "parameters":{
            "type":"object",
            "properties":{},
            "additionalProperties": False,
        },
    }
]

def run_tool(name: str, arguments:dict):
    if name == "calculator":
        return calculator(arguments["expression"])
    
    elif name == "get_current_time":
        return get_current_time()
    
    raise ValueError(f"Unknown tool: {name}")
    
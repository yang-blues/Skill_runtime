import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI



load_dotenv(override=True)
QWEN_API_KEY=os.getenv("QWEN_KEY")
QWEN_BASE_URL=os.getenv("QWEN_BASE_URL")

llm = ChatOpenAI(
    model='qwen3.8-max-0902',
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
)
from typing import List

import uvicorn
from fastapi import FastAPI, Body
from llama_index.core.base.llms.types import MessageRole, ChatMessage
from starlette.middleware.cors import CORSMiddleware

from llama_index.core.agent import ReActAgent
from lite_agent.agent.memory import get_memory
from lite_agent.agent.tools import llm_tool_kits, platformContext
from lite_agent.settings import llm, zk_host, zk_port

agent = ReActAgent.from_tools(llm_tool_kits, llm=llm, verbose=True)
app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/agentChat")
async def agent_chat(user_id: int = Body(..., embed=True, alias="userId"), msg: str = Body(..., embed=True)) -> str:
    """
    用户与 agent 智能体的对话接口
    """
    long_term_memory = get_memory(user_id, long_term=True)
    short_term_memory = get_memory(user_id, long_term=False)

    # 聚合的聊天记录，包含长短期记忆
    chat_history: List[ChatMessage] = list()
    # chat_history += long_term_memory.get()
    chat_history += short_term_memory.get()
    chat_history.append(ChatMessage.from_str(content=platformContext(user_id), role=MessageRole.SYSTEM))
    resp = agent.chat(message=msg, chat_history=chat_history)
    short_term_memory.put(ChatMessage.from_str(content=msg))
    # 返回智能体的聊天响应结果
    return str(resp)


def initHttp():
    print("Http API 服务器正在启动...")
    uvicorn.run(app, port=11455)
    print("Http API 服务初始化完成")

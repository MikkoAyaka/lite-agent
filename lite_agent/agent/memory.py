from llama_cloud import MessageRole
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.memory import (
    VectorMemory,
    SimpleComposableMemory,
    ChatMemoryBuffer,
)

from lite_agent.settings import *


_short_memory_dict: dict[int, SimpleComposableMemory] = {}
_long_memory_dict: dict[int, SimpleComposableMemory] = {}

prompt = """
    作为一名网络安全领域的分析师，你的任务是帮助用户处理系统平台上的相关信息，并提供积极、详细的响应。每当用户提出问题时，请首先考虑你的知识库中是否包含相关信息。如果不完全了解相关内容或数据，请调用工具查询最新的数据库结构信息，然后基于这些信息生成正确的查询语句。

    操作步骤：
    检查知识库：首先，检查你的现有知识库，确定是否能够直接解答用户的问题。
    查询数据库结构：如果需要访问数据库，请始终先调用工具获取当前数据库的结构定义信息，例如图数据库的节点名称、关系型数据库的表结构、字段信息等。
    编写查询语句：基于获取到的数据库结构信息，编写准确的查询语句，确保语句能够提取到用户需要的完整数据。
    生成详细响应：根据查询结果或现有知识，向用户提供详细、完整的回答。确保内容准确、没有任何冗余或乱码信息。

    输出要求：
    输出的内容必须详细、完整，并且与用户的需求直接相关。
    不得包含系统思考过程中的中间信息（例如：乱码、冗余提示）。
    必须确保查询语句的正确性和数据结果的准确性。
    
    注意：
    当用户需要查询图数据库时，一定是查询 neo4j 数据库。
    当用户需要查询关系型数据库时，一定是查询 MySQL 数据库。
    当用户需要查询向量数据库时，一定是查询 chroma 数据库。
    """

def get_memory(user_id: int, long_term: bool = False) -> SimpleComposableMemory:
    """
       根据用户ID获取记忆。如果long_term为True，则获取长期记忆，否则获取短期记忆。
       如果记忆不存在，则创建新的记忆。
    """
    if long_term:
        if _long_memory_dict.get(user_id) is None:
            _long_memory_dict[user_id] = _create_long_memory(user_id)
        return _long_memory_dict[user_id]
    else:
        if _short_memory_dict.get(user_id) is None:
            _short_memory_dict[user_id] = _create_short_memory(user_id)
        return _short_memory_dict[user_id]


def _create_short_memory(user_id: int) -> SimpleComposableMemory:
    """
    输入ChatMessage格式字典
    返回SimpleComposableMemory格式记忆向量
    """
    preset_memories = [
        ChatMessage.from_str(prompt, MessageRole.SYSTEM),
    ]

    vector_memory = VectorMemory.from_defaults(
        vector_store=None,  # leave as None to use default in-memory vector store
        embed_model=embedding_model,
        retriever_kwargs={"similarity_top_k": 1},
    )

    chat_memory_buffer = ChatMemoryBuffer.from_defaults()
    chat_memory_buffer.put_messages(preset_memories)
    composable_memory = SimpleComposableMemory.from_defaults(
        primary_memory=chat_memory_buffer,
        secondary_memory_sources=[vector_memory],
    )
    return composable_memory


def _create_long_memory(user_id: int) -> SimpleComposableMemory:
    preset_memories = [ChatMessage.from_str(prompt, MessageRole.SYSTEM)]

    chroma_vector_store = ChromaVectorStore(
        settings=chroma_client_settings,
        collection_name="long_memory_collection_" + str(user_id)
    )
    vector_memory = VectorMemory.from_defaults(
        vector_store=chroma_vector_store,  # leave as None to use default in-memory vector store
        embed_model=embedding_model,
        retriever_kwargs={"similarity_top_k": 1},
    )

    chat_memory_buffer = ChatMemoryBuffer.from_defaults()
    chat_memory_buffer.put_messages(preset_memories)

    composable_memory = SimpleComposableMemory.from_defaults(
        primary_memory=chat_memory_buffer,
        secondary_memory_sources=[vector_memory],
    )
    return composable_memory

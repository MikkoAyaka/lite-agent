import os

from chromadb import Settings
from dotenv import load_dotenv, dotenv_values
from llama_index.core import SQLDatabase, VectorStoreIndex, ServiceContext
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.core.objects import SQLTableNodeMapping, SQLTableSchema, ObjectIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, MetaData

from lite_agent.api.search_api import BingSearchAPI
from lite_agent.api.chroma_base import ChromaVectorStore

# 加载对应环境的环境变量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env.docker')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=True)
    config = dotenv_values(env_path)
else:
    raise FileNotFoundError(f"Environment file {env_path} not found")

bing_api_key = os.getenv('BING_API_KEY')
bing_search_api = BingSearchAPI(bing_api_key)

zk_host = os.getenv('ZOOKEEPER_HOST')
zk_port = os.getenv('ZOOKEEPER_PORT')
# LLM 相关初始化
llm = OpenAI(temperature=0, model="gpt-4o")
# 数据库初始化
base_engine = create_engine(os.getenv('SQL_URL'))
# load all table definitions
metadata_obj = MetaData()
metadata_obj.reflect(base_engine)

sql_database = SQLDatabase(base_engine)

table_node_mapping = SQLTableNodeMapping(sql_database)

table_schema_objs = []
for table_name in metadata_obj.tables.keys():
    table_schema_objs.append(SQLTableSchema(table_name=table_name))

obj_index = ObjectIndex.from_objects(
    objects=table_schema_objs,
    object_mapping=table_node_mapping,
    index_cls=VectorStoreIndex
)
service_context = ServiceContext.from_defaults(llm=llm)
sql_query_engine = SQLTableRetrieverQueryEngine(
    sql_database,
    obj_index.as_retriever(similarity_top_k=1),
    service_context=service_context,
)

chroma_client_settings = Settings(
        chroma_client_auth_provider='chromadb.auth.basic_authn.BasicAuthClientProvider',
        chroma_client_auth_credentials=os.getenv('CHROMA_USERNAME') + ":" + os.getenv('CHROMA_PASSWORD')
    )
chroma_db = ChromaVectorStore(settings=chroma_client_settings)
neo4j_db = Neo4jGraphStore(url=os.getenv('NEO4J_URI'), username=os.getenv('NEO4J_USERNAME'), password=os.getenv('NEO4J_PASSWORD'))

embedding_model = OpenAIEmbedding(temperature=0, api_base="https://api.xty.app/v1")

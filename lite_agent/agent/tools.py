from lite_agent.api import search_api
from lite_agent.settings import neo4j_db, chroma_db, sql_query_engine, bing_search_api
from llama_index.core.tools import QueryEngineTool, FunctionTool
import datetime


def platformContext(user_id: int) -> str:
    return "当前用户在智安智策平台的 ID 为："+str(user_id)


def dateToolFunc(unit: str) -> int:
    """
    get the real time date,such as year 2024, month 12, day 15, day 2 of this week
    Args:
        unit(str): the time unit of real time date.
    Example argument inputs:
        'YEAR'
        'MONTH'
        'MINUTE'
        'HOUR'
        'DAY_OF_MONTH'
        'DAY_OF_WEEK'
    """
    now = datetime.datetime.now()
    if unit == 'MINUTE':
        return now.minute
    elif unit == 'YEAR':
        return now.year
    elif unit == 'MONTH':
        return now.month
    elif unit == 'HOUR':
        return now.hour
    elif unit == 'DAY_OF_MONTH':
        return now.day
    elif unit == 'DAY_OF_WEEK':
        return now.isoweekday()
    else:
        raise ValueError("Unsupported time unit")


def searchToolFunc(query: str) -> str:
    """
    You can use this tool to search from website
    """
    return bing_search_api.search(query)

def platformToolFunc() -> int:
    """
    You can use this tool to manage all resources on the platform for the user and view the user's notifications.
    If the user requests assistance with managing servers, configuring protection policies, etc., please use this tool
    The operation will always be successful, don't worry about that.
    """
    pass


neo4j_tool = QueryEngineTool.from_defaults(
    neo4j_db,
    name="neo4j",
    description="""
    Use this Neo4j query tool to explore relationships and patterns in complex data sets. Ideal for
    scenarios requiring graph-based data analysis, such as network security analysis, fraud detection,
    and recommendation systems.
    
    Example Query Descriptions:
        
        1.Query to Find All IPs with Domain Associations:
        Retrieve all nodes representing IP addresses that have at least one associated domain. This query helps identify active IPs with domain links.
        Query Cypher: MATCH (n) WHERE n.ip IS NOT NULL AND n.domain_count > 0 RETURN n.ip, n.domain_count
        
        2.Query for Potentially Malicious IPs:
        Identify IP addresses flagged with a severity level and a confidence level in their threat assessment. This query is essential for focusing on IPs that have been assessed, even if they are not confirmed as malicious.
        Query Cypher: MATCH (n) WHERE n.severity IS NOT NULL AND n.confidence_level IS NOT NULL RETURN n.ip, n.severity, n.confidence_level

        3.Query to List All IPs with Zero Domain Associations:
        Fetch all IP nodes that currently have no associated domains. This query can help in identifying isolated IPs in the network.
        Query Cypher: MATCH (n) WHERE n.ip IS NOT NULL AND n.domain_count = 0 RETURN n.ip
        
        4.Query for Nodes with Specific Attributes:
        Retrieve nodes that contain a specific attribute, such as a name or an IP address, to understand the entity structure within the graph.
        Query Cypher: MATCH (n) WHERE n.name IS NOT NULL OR n.ip IS NOT NULL RETURN n
        
        5.Query for Detailed IP Analysis:
        Analyze IP nodes with additional details such as severity, confidence level, and domain associations to prioritize security responses.
        Query Cypher: MATCH (n) WHERE n.ip IS NOT NULL AND (n.severity IS NOT NULL OR n.domain_count IS NOT NULL) RETURN n.ip, n.severity, n.confidence_level, n.domain_count LIMIT 20

    These prompts guide the agent to construct and execute specific Neo4j queries that align with the structure and needs of the database. By using these examples, the intelligent agent can generate accurate and contextually appropriate queries for various analysis scenarios.
    """
)
chroma_tool = QueryEngineTool.from_defaults(
    chroma_db,
    name="chroma",
    description=("Use the Chroma graphical database query tool to retrieve and analyze complex relational data. "
                 "Ideal for scenarios requiring detailed data visualization, relationship mapping, and in-depth "
                 "database insights. Input your query to get started.")
)
sql_tool = QueryEngineTool.from_defaults(
    sql_query_engine,
    name="mysql",
    description=(
        "Use this MySQL query tool to perform efficient and reliable operations on structured relational data. "
        "Ideal for scenarios requiring traditional relational database management, such as data storage, "
        "retrieval, and complex query execution. Input your SQL query to get started and gain insights from "
        "your structured datasets."
    )
)
date_tool = FunctionTool.from_defaults(fn=dateToolFunc)
platform_tool = FunctionTool.from_defaults(fn=platformToolFunc)
search_tool = FunctionTool.from_defaults(fn=searchToolFunc)

llm_tool_kits = [date_tool, chroma_tool, neo4j_tool, platform_tool, sql_tool, search_tool]


# TEST
#
# query = "OpenAI"
# results = bing_search_tool.search(query)
# parsed_results = bing_search_tool.parse_results(results)
#
# for result in parsed_results:
#     print(f"Title: {result['title']}, URL: {result['url']}")

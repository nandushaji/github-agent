import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent,AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from github import fetch_github_issues
from langchain import hub
from note import note_tool

load_dotenv()

def connect_vstore():
    embeddings = OpenAIEmbeddings()
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    namespace = os.getenv("ASTRA_DB_KEYSPACE")

    if namespace:
        ASTRA_DB_KEYSPACE = namespace
    else:
        ASTRA_DB_KEYSPACE = None

    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name="github",
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace=ASTRA_DB_KEYSPACE
    )
    return vstore

vstore = connect_vstore()
add_to_vector_store = input("Do you want to update the issues? (Y/N):").lower() in ["yes","y"]

if add_to_vector_store:
    owner = "nandushaji"
    repo = "webRTC-Video-Chat"
    issues = fetch_github_issues(owner,repo)

    try:
        vstore.delete_collection()
    except:
        pass

    vstore = connect_vstore()
    try:
        vstore.add_documents(issues)
    except:
        pass


retriever = vstore.as_retriever(search_kwargs= {"k":30})
retriever_tool = create_retriever_tool(
    retriever,
    "github_search",
    "Search for information about github issues. For any questions about github issues, you must use this tool!"
)

prompt = hub.pull("hwchase17/openai-functions-agent")

llm = ChatOpenAI()

tools = [retriever_tool,note_tool]
agent = create_tool_calling_agent(llm,tools,prompt)

agent_executor = AgentExecutor(agent=agent,tools=tools,verbose=True)

while (question := input("Ask any questions about github issues (q to quit): ")) != "q":
    result = agent_executor.invoke({"input":question})
    print(result["output"])

    






    

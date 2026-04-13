from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
import os

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY")
)

# -------------------------
# State Definition
# -------------------------
class ChatState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]


# -------------------------
# Node Function
# -------------------------
def chat_node(state: ChatState):
    msg = state.messages

    # FIX: safer response parsing
    response = llm.invoke(msg)

    try:
        res = response.content[0]['text']
    except Exception:
        res = str(response)

    return {"messages": [AIMessage(content=res)]}


# -------------------------
# Graph Setup
# -------------------------
checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# thread_id = 1
# while True:
#     user_query = input('enter u r query')
#     if user_query.strip() in ['bye','exit','quit']:
#         break
#     intial_state = {
#         'messages':[
#         HumanMessage(content=user_query)
#         ]}
#     config = {'configurable':{'thread_id':thread_id}}
#     res = workflow.invoke(intial_state,config=config)
#     print(res['messages'][-1].content)


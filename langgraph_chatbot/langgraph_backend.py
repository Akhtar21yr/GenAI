from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import os
import sqlite3
from pathlib import Path

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


def run_cmd(cmd):
    pass
    


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
BASEDIR = Path(__file__).parent

conn = sqlite3.connect(database=BASEDIR /'chatbot.db',check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# res = chatbot.invoke({'messages':['hello how r u']},config = {'configurable': {'thread_id': 'thread_id'}})
# print(res)

def get_all_threads():
    threads = set()
    result = []

    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        threads.add(thread_id)

    for thread_id in threads:
        state = chatbot.get_state(
            config={'configurable': {'thread_id': thread_id}}
        )

        messages = state.values.get('messages', [])

        topic = "New Chat"
        for msg in messages:
            if isinstance(msg, HumanMessage):
                topic = msg.content[:30]
                break

        result.append({
            "thread_id": thread_id,
            "topic": topic
        })

    return result


# get_all_threads
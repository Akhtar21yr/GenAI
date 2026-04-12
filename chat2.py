from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage,AIMessage

from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")


class State(BaseModel):
    user_query : str
    llm_output : str|None = None
    is_good : bool|None = None

def chatbot(state:State):
    res = llm.invoke(HumanMessage(content='best place in lucknow for trip'))
    return {
        "llm_output": res.content
    }


def evalute_res(state:State):
    pass

graph_builder = StateGraph(State)



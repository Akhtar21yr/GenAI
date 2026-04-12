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
    messages: list[BaseMessage]

def chatbot(state:State):
    print('Inside chatbot node state: ',state)
    response = llm.invoke(state.messages)
    return {
        "messages": [response]
    }


def samplenode(state:State):
    print('Inside samplenode node state: ',state)
    return {'messages':[HumanMessage(content='hey i m from samplecode node')]}







graph_builder = StateGraph(State)
graph_builder.add_node('chatbot',chatbot)
graph_builder.add_node('samplenode',samplenode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot","samplenode")
graph_builder.add_edge("samplenode",END)


graph = graph_builder.compile()

result = graph.invoke({
    'messages':[HumanMessage(content="Hi! This is a message from user")]
})

print("\n✅ Final Output:", result)
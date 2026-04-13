import streamlit as st 
from langgraph_backend import chatbot
from streamlit_chat import message
from langchain.messages import HumanMessage

if 'msgs' not in st.session_state :
    st.session_state['msgs'] = []

msgs = st.session_state['msgs']
for msg in msgs:
    message(msg.get('content'),is_user= True if msg.get('role') == 'user' else False)

user_input = st.chat_input('Enter Your Query')

def streaming():
    for msg_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode='messages'):
        if msg_chunk.content:
            if isinstance(msg_chunk.content,list):
                yield msg_chunk.content[0]['text']
            elif isinstance(msg_chunk.content,str):
                yield msg_chunk.content

if user_input:
    msgs.append({'role':'user','content':user_input})
    message(user_input,is_user= True )


    config = {'configurable':{'thread_id':'1'}}
    # res = chatbot.stream({"messages": [HumanMessage(content=user_input)]},config=config)['messages'][-1].content
    
    # msgs.append({'role':'assistant','content':res})
    # message(res,is_user= False )
    response = st.write_stream(streaming)
    msgs.append({'role': 'assistant', 'content': response})

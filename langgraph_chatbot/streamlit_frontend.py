import streamlit as st 
from langgraph_backend import chatbot
from streamlit_chat import message
from langchain.messages import HumanMessage
import uuid
from langgraph_backend import get_all_threads


def genrate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = str(genrate_thread_id())
    st.session_state['thread_id'] = thread_id
    st.session_state['msgs'] = []

def add_thread(thread_id, topic):
    threads = st.session_state['chat_threads']
    if not any(t['thread_id'] == thread_id for t in threads):
        threads.append({
            "thread_id": thread_id,
            "topic": topic
        })


def load_chat(thread_id):
    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )

    return state.values.get('messages', [])

if 'msgs' not in st.session_state:
    st.session_state['msgs'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(genrate_thread_id())

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_all_threads()

st.sidebar.title('LangGraph Chatbot')
if st.sidebar.button('New chat'):
    reset_chat()

for thread_data in st.session_state['chat_threads'][::-1]:
    thread_id = thread_data['thread_id']
    topic = thread_data['topic']

    if st.sidebar.button(topic):
        st.session_state['thread_id'] = thread_id

        messages = load_chat(thread_id)

        temp_msgs = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_msgs.append({'role': role, 'content': msg.content})

        st.session_state['msgs'] = temp_msgs



msgs = st.session_state['msgs']
for msg in msgs:
    message(msg.get('content'),is_user= True if msg.get('role') == 'user' else False)


def streaming(user_input, config):
    for msg_chunk, metadata in chatbot.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode='messages'
    ):
        if msg_chunk.content:
            if isinstance(msg_chunk.content, list):
                yield msg_chunk.content[0]['text']
            elif isinstance(msg_chunk.content, str):
                yield msg_chunk.content

user_input = st.chat_input('Enter Your Query')

if user_input:
    thread_id = st.session_state['thread_id']

    # if st.sidebar.button(user_input):
    #     st.session_state['thread_id'] = thread_id

    # First message → create thread
    

    msgs.append({'role': 'user', 'content': user_input})
    message(user_input, is_user=True)

    config = {'configurable': {'thread_id': thread_id}}

    response = st.write_stream(
        streaming(user_input, config)
    )

    msgs.append({'role': 'assistant', 'content': response})

    if not any(t['thread_id'] == thread_id for t in st.session_state['chat_threads']):
        add_thread(thread_id, user_input)
        st.rerun()

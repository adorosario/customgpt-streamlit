import streamlit as st
import os
import json
import uuid
from customgpt_client import CustomGPT

def get_citations(api_token, project_id, citation_id):
    CustomGPT.api_key = api_token

    try:
        response_citations = CustomGPT.Citation.get(project_id=project_id, citation_id=citation_id)
        if response_citations.status_code == 200:
            try:
                citation = response_citations.parsed.data
                if citation.url != None:
                    source = {'title': citation.title, 'url': citation.url }
                else:
                    source = {'title': 'source', 'url': "" }
                
            except:
                if citation.page_url != None:
                    source = {'title': citation.title, 'url': citation.page_url  }
                else:
                    source = {'title': 'source', 'url': "" }
            
            return source
        else:
            return []
    except sException as e:
        print(f"error::{e}")
   
def query_chatbot(api_token, project_id, session_id, message, stream=True, lang='en'):
    CustomGPT.api_key = api_token
    try:
        stream_response = CustomGPT.Conversation.send(project_id=project_id, session_id=session_id, prompt=message, stream=stream, lang=lang)
        return stream_response
    except Exception as e:
        return [f"Error:: {e}"]

def get_projectList(api_token):
    CustomGPT.api_key = api_token
    try:
        projects = CustomGPT.Project.list()
        if projects.status_code == 200:
            return projects.parsed.data.data
        else:
            return []
    except Exception as e:
        print(f"error:get_projectList:: {e}")

def clear_chat_history():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# App title
st.set_page_config(page_title="CustomGPT Chatbot")
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# CustomGPT Credentials
with st.sidebar:
    st.title('CustomGPT Streamlit Demo')
   
    customgpt_api_key = st.text_input('Enter CustomGPT API Key:', type='password')
    if customgpt_api_key:

        st.subheader('Select Project')
        listProject = get_projectList(customgpt_api_key)
        if listProject is not None:
            projectNames = [projt.project_name for projt in listProject]
            selected_model = st.sidebar.selectbox('Select Model', projectNames, key='selected_model')
            index = projectNames.index(selected_model)
            selected_project = listProject[index]
        else:
            st.error('No projects found. Please check your API key.', icon='❌')
        st.sidebar.button('Reset Chat', on_click=clear_chat_history)

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Display the message content
        st.write(f"{message['content']}")

# User-provided prompt
if prompt := st.chat_input(disabled=not customgpt_api_key):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        # Display the user's message
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = query_chatbot(customgpt_api_key, selected_project['id'], st.session_state.session_id, prompt)
            # response = []
            placeholder = st.empty()
            full_response = ""
            for event in client.events():
                print(event.data)
                resp_data = eval(event.data.replace('null', 'None'))
                if resp_data is not None:
                    if resp_data.get('status') == 'error':
                        full_response += resp_data.get('message', '')
                        placeholder.markdown(full_response+ "▌")

                    if resp_data.get('status') == 'progress':
                        full_response += resp_data.get('message', '')
                        placeholder.markdown(full_response+ "▌")

                    if resp_data.get('status') == 'finish' and resp_data.get('citations') is not None:
                        citation_ids = resp_data.get('citations', [])

                        citation_links = []
                        count = 1
                        for citation_id in citation_ids:
                            citation_obj = get_citations(customgpt_api_key,  selected_project['id'], citation_id)
                            url = citation_obj.get('url', '')
                            title = citation_obj.get('title', '')
                            
                            if len(url) > 0:
                                formatted_url = f"{count}. [{title or url}]({url})"
                                count +=1
                                citation_links.append(formatted_url)

                        if citation_links:
                            cita = "\n\nSources:\n"
                            for link in citation_links:
                                cita += f"{link}\n"
                            full_response += cita
                            placeholder.markdown(full_response+ "▌")
                           
            placeholder.markdown(full_response)
    if full_response == "":
        full_response = "Oh no! Any unknown error has occured. Please check your CustomGPT Dashboard for details."
        placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)


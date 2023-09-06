import streamlit as st
import requests
import os
import json
from sseclient import SSEClient
import uuid
import time

api_endpoint = 'https://dev.customgpt.ai/api/v1/'

# Utilities

def get_citations(api_token, project_id, citation_id):
    url = api_endpoint + "projects/"+str(project_id)+"/citations/" +str(citation_id)

    headers = {
        "accept": "application/json",
        "authorization": 'Bearer ' + api_token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = json.loads(response.text)
        if result['status'] == 'success':
            try:
                if result['data']['url'] != None:
                    source = {'title': result['data']['title'], 'url': result['data']['url'] }
                else:
                    source = {'title': 'source', 'url': "" }
                
            except:
                try:
                    if result['data']['page_url'] != None:
                        source = {'title': result['data']['title'], 'url': result['data']['page_url'] }
                    else:
                        source = {'title': 'source', 'url': "" }
                except:
                    if result['citation']['page_url'] != None:
                        source = {'title': 'source', 'url': result['citation']['page_url'] }
                    else:
                        source = {'title': 'source', 'url': "" }
            
            return source
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"'erreur")
   
def query_chatbot(api_token, project_id,session_id,message,stream='true', lang='en' ):
    url = api_endpoint + "projects/" + str(project_id) +"/conversations/"+str(session_id)+"/messages?stream="+str(stream)+"&lang="+str(lang)

    payload = { "prompt": str(message)}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": 'Bearer ' + api_token
    }

    try:
        stream_response = requests.post(url, json=payload, headers=headers)
        client = SSEClient(stream_response)
        response = []
        for event in client.events():
            resp_data = eval(event.data.replace('null', 'None'))

            if resp_data is not None:
                if resp_data.get('status') == 'error':
                    response.append(resp_data.get('message', ''))

                if resp_data.get('status') == 'progress':
                    response.append(resp_data.get('message', ''))

                if resp_data.get('status') == 'finish' and resp_data.get('citations') is not None:
                    citation_ids = resp_data.get('citations', [])

                    citation_links = []
                    ccount = 1
                    for citation_id in citation_ids:
                        citation_obj = get_citations(api_token, project_id, citation_id)
                        url = citation_obj.get('url', '')
                        
                        if len(url) > 0:
                            formatted_url = f"[{ccount}]({url})"
                            ccount += 1
                            citation_links.append(formatted_url)

                    if citation_links:
                        cita = "\n\nSources: " + ", ".join(citation_links)
                        response.append(cita)
        return response
    except requests.exceptions.RequestException as e:
        return ["Error"]

def get_projectList(api_token):
    url = api_endpoint + "projects?page=1&order=desc&width=100%25&height=auto"

    headers = {
        "accept": "application/json",
        "authorization": 'Bearer ' + api_token
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = json.loads(response.text)
        if result['status'] == 'success':
            return result['data']['data']
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"'erreur")

def clear_chat_history():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# App title
st.set_page_config(page_title="CustomGPT Chatbot")
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# CustomGPT Credentials
with st.sidebar:
    st.title('CustomGPT Chatbot')
   
    customgpt_api_key = st.text_input('Enter CustomGPT API Key:', type='password')
    if customgpt_api_key:

        st.subheader('Select Project')
        listProject = get_projectList(customgpt_api_key)
        if listProject is not None:
            projectNames = [projt['project_name'] for projt in listProject]
            selected_model = st.sidebar.selectbox('', projectNames, key='selected_model')
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
            response = query_chatbot(customgpt_api_key, selected_project['id'], st.session_state.session_id, prompt)
            placeholder = st.empty()
            full_response = ""

            for item in response:
                full_response += item
                time.sleep(0.05)
                placeholder.markdown(full_response+ "▌")
            placeholder.markdown(full_response)
    if full_response == "":
        full_response = "Oh no! Any unknown error has occured. Please check your CustomGPT Dashboard for details."
        placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
import streamlit as st
import requests
import os
import json
from sseclient import SSEClient


api_endpoint = 'https://app.customgpt.ai/api/v1/'



# Utilities

def get_citations(api_token, project_id, citation_id):
    url = "https://app.customgpt.ai/api/v1/projects/"+str(project_id)+"/citations/" +str(citation_id)

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
                source = {'title': result['data']['title'], 'url': result['data']['url'] }
                
            except:
                source = {'title': 'source', 'url': result['citation']['page_url'] }
            
            return source
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"'erreur")
   
def create_conversation(api_token, project_id, name):
    url = api_endpoint + "projects/" + str(project_id) +"/conversations"

    headers = {
        "accept": "application/json",
        "authorization": 'Bearer ' + api_token
    }
    payload = { "name": name }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = json.loads(response.text)
        if result['status'] == 'success':
            return result['data']
        else:
            return json.loads(response.text)["data"]
    except requests.exceptions.RequestException as e:
        print(f"{e}")
        return (False, "Error")

def query_chatbot(api_token, project_id,session_id,message,stream='true', lang='en' ):
    url = api_endpoint + "projects/" + str(project_id) +"/conversations/"+str(session_id)+"/messages?stream="+str(stream)+"&lang="+str(lang)

    payload = { "prompt": str(message)}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": 'Bearer ' + api_token
    }
    stream_response = requests.post(url, stream=True, headers=headers, data=payload)
    client = SSEClient(stream_response)
    for event in client.events():
        print(event.data)
    try:
        stream_response = requests.post(url, json=payload, headers=headers)
        client = SSEClient(stream_response)
        response = []
        for event in client.events():
            resp_data = eval(event.data)
            # print(resp_data['message'])
            if resp_data['status'] == 'progress' :
                response.append(resp_data['message'])

            if resp_data['status'] == 'finish' and resp_data['citations'] != None:
                citation_ids = resp_data['citations']
                citations = "\n\n (Source: "
                for citation_id in citation_ids:
                    citation_obj = get_citations(api_token, project_id,citation_id)
                    if citation_id == citation_ids[-1]:
                        citations += citation_obj['url']+" )"
                    else:
                        citations += citation_obj['url']+", "

                
                response.append(citations)
        
        return response     
    except requests.exceptions.RequestException as e:
        return ["Error"]

def get_projectList(api_token):
    url = "https://app.customgpt.ai/api/v1/projects?page=1&order=desc&width=100%25&height=auto"

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

def get_conversationList(api_token, project_id):
    url = "https://app.customgpt.ai/api/v1/projects/"+str(project_id) +"/conversations?page=1&order=desc&userFilter=all"

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




# App title
st.set_page_config(page_title="CustomGPT Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('CustomGPT Chatbot')
   
    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Select a project')
    listProject = get_projectList(replicate_api)
    if listProject is not None:
        projectNames = [projt['project_name'] for projt in listProject]
        selected_model = st.sidebar.selectbox('', projectNames, key='selected_model')
        index = projectNames.index(selected_model)
        selected_project = listProject[index]
        if selected_project:
            st.subheader('Select a conversation')
            listConversation = get_conversationList(replicate_api,selected_project['id'])
            if listConversation is not None and len(listConversation) > 0:
                convNames = [conv['name'] for conv in listConversation]
                selected_conve = st.selectbox('', convNames, key='selected_conv')
                indx = convNames.index(selected_conve)
                selected_conv = listConversation[indx]

                if selected_conv:
                    st.write(f'Selected Conversation: {selected_conv["name"]}')
            else:
                st.warning('No conversations found for the selected project. You can create a new conversation below.', icon='⚠️')
                new_conv_name = st.text_input('Enter a name for the new conversation:')
                if st.button('Create New Conversation'):
                    selected_conv = create_conversation(replicate_api,selected_project['id'],new_conv_name)
                    st.success(f'Created a new conversation: {new_conv_name}', icon='✅')
        else:
            st.error('No project selected.', icon='❌')
    else:
        st.error('No projects found. Check your API key.', icon='❌')

   
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Display the message content
        st.write(f"{message['content']}")

        
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        # Display the user's message
        st.write(prompt)

# Generate a new response if the last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_chatbot(replicate_api, selected_conv['project_id'], selected_conv['session_id'], prompt)
            placeholder = st.empty()
            full_response = ""

            for item in response:
                full_response += item
                placeholder.markdown(full_response)

    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
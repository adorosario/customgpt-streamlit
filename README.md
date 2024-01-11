This demo Streamlit app is designed to interface with the [CustomGPT API](https://docs.customgpt.ai/reference/i-api-homepage), providing a user-friendly custom GPT chatbot experience. It allows users to interact with various custom GPT agents on your CustomGPT account, manage conversations, and view citations from the chatbot responses.

## About CustomGPT
[CustomGPT.ai](https://customgpt.ai/) is a no-code/low-code SaaS platform to create custom GPT RAG agents with your own content. With just a few lines of code, developers can create sophisticated RAG agents with their own documents and websites, helpdesks, videos, audios, etc. This saves developers the burden of building their own RAG pipeline. And instantly get the benefit of data integrations, anti-hallucination, citations, analytics and [industry-best query relevancy](https://medium.com/towards-artificial-intelligence/build-it-or-buy-it-deployment-options-for-retrieval-augmented-generation-rag-f6d43df8212a). 

## Live Demo
If you have your own CustomGPT API key and projects, you can test the experience on the live app: 
https://customgpt-demo-app.streamlit.app/

## Features In This Demo
- Project selection from available CustomGPT projects
- Real-time chatbot interaction WITH streaming
- Conversations with history
- Clearing of chat history
- Citation viewing for chatbot responses
- RAG Agent with anti-hallucination.

## Requirements
- Streamlit
- customgpt_client

## Installation

1. **Clone the Repository**: First, clone this repository to your local machine.

2. **Install Dependencies**: Run the following command to install the required Python packages.
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the App**: Run the Streamlit app with the following command.
   ```bash
   streamlit run streamlitAndCustomGpt.py
   ```

2. **Enter CustomGPT API Key**: On the app's sidebar, input your CustomGPT API Key in the provided text field.

3. **Select a Project**: After entering the API Key, you will be able to select a project from your available CustomGPT projects.

4. **Chat with the Bot**: Use the chat input to start a conversation with the chatbot. The responses will include citations where applicable.

5. **Reset Chat**: You can reset the chat history at any time using the 'Reset Chat' button.

## Functionality

### Utilities
- `get_citations`: Fetches citation data from a given citation ID.
- `query_chatbot`: Sends a user's message to the CustomGPT chatbot and receives the response.
- `get_projectList`: Retrieves a list of available projects from CustomGPT.
- `clear_chat_history`: Clears the current chat history.

### App Components
- **API Key Input**: Secure text input for entering the CustomGPT API Key.
- **Project Selection**: Dropdown to select a project for the chatbot conversation.
- **Chat Interface**: Real-time chat interface for interacting with the CustomGPT chatbot.
- **Reset Chat**: Button to reset the chat history.

## Troubleshooting
- **API Key Issues**: Ensure that your CustomGPT API Key is entered correctly.
- **Connection Problems**: Check your internet connection if the app fails to connect to the CustomGPT API.
- **Unknown Errors**: For unhandled errors or query logs, check your CustomGPT Dashboard for more details.

## Support
For support, please contact the repository owner or submit an issue on the GitHub repository page. You can also [contact CustomGPT](https://customgpt.ai/contact-us). 

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

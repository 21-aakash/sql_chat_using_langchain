import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables from the .env file to securely manage sensitive data like API keys
load_dotenv()

# Retrieve the Groq API key from environment variables, ensuring security and flexibility
api_key = os.getenv("GROQ_API_KEY")

# Configure the Streamlit app's page settings, including the title and page icon
st.set_page_config(page_title="SkyChat", page_icon="👽")
st.title("👽SkyChat: Chat with Database")

# Inject custom CSS to style various elements in the Streamlit app for a more personalized UI
st.markdown("""
    <style>
    .stTextInput, .stTextArea, .stChatMessage, .stButton, .stSelectbox, .stRadio, .stSidebar > div {
        color: #ffffff;  /* Sets font color to white for various input and display elements */
    }
    .stMarkdown p {
        color: #ffffff;  /* Ensures all markdown text appears in white */
    }
    .stTitle h1 {
        color: #ffa500;  /* Sets the title color to orange */
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #00ff00;  /* Colors the sidebar headings in green */
    }
    .stSidebar .stTextInput, .stSidebar .stTextArea, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stRadio {
        color: #00ff00;  /* Ensures all inputs in the sidebar are green */
    }
    body {
        background-color: #000000;  /* Sets the background to black for a sleek look */
    }
    </style>
    """, unsafe_allow_html=True)

# Constants for identifying database types
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

# Sidebar radio buttons allow the user to select between an SQLite database and a MySQL database
radio_opt = ["Use SQLite 3 Database - Student.db", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat with", options=radio_opt)

# Depending on the user's selection, set up the appropriate database connection
if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    # Collect MySQL connection details from the user via sidebar inputs
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")  # Password input is masked
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = LOCALDB

# Check if the Groq API key is available, if not, show an error and stop the app
if not api_key:
    st.error("Groq API key is missing. Please ensure it's set in the .env file.")
    st.stop()

# Initialize the language model using Groq's API, specifying the model and enabling streaming responses
llm = ChatGroq(groq_api_key=api_key, model_name="Llama3-8b-8192", streaming=True)

# Use Streamlit's @st.cache_resource to cache the database configuration function for faster access later
# The cache is refreshed every 2 hours (ttl="2h")
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        # Set up a connection to the local SQLite database, ensuring it's read-only
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        print(dbfilepath)  # Print the database file path for debugging purposes
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == MYSQL:
        # If MySQL is selected, ensure all required connection details are provided
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        # Create a connection string and connect to the MySQL database
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

# Depending on the selected database, configure the appropriate SQL database connection
if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

# Set up the SQL toolkit which integrates the database with the language model for natural language processing
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create an SQL agent that uses the language model and toolkit to process natural language queries
# and interact with the database using the ZERO_SHOT_REACT_DESCRIPTION agent type
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Manage the message history between the user and the assistant
# Initialize the message history if it doesn't exist or clear it when the user requests
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display each message in the chat using custom styling
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"], unsafe_allow_html=True)
    else:
        st.chat_message("assistant").write(msg["content"], unsafe_allow_html=True)

# Capture the user's input query and add it to the message history
user_query = st.chat_input(placeholder="Ask anything from the database")

# If the user submits a query, process it
if user_query:
    # Add the user's message to the chat history and display it
    st.session_state["messages"].append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query, unsafe_allow_html=True)

    # Get the agent's response to the user's query
    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        # Run the agent with the user's query, capturing the output and displaying it
        response = agent.run(user_query, callbacks=[streamlit_callback])
        # Add the assistant's response to the message history
        st.session_state["messages"].append({"role": "assistant", "content": response})
        # Display the assistant's response
        st.write(response, unsafe_allow_html=True)

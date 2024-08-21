# SQL Chat Using LangChain

## Description
This Streamlit application allows users to interact with a MySQL database using natural language queries powered by LangChain. Users can explore and manipulate data without needing to write SQL commands directly.

## Deployed Link
- [SQL Chat Using LangChain](https://sqlchatusinglangchain-ddejyrfbabdta5m7zj73rn.streamlit.app/)

## Getting Started

### Prerequisites
Ensure you have the following installed on your system:
- [Anaconda](https://www.anaconda.com/products/individual) (or Miniconda)
- Python 3.8 or higher

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/sql-chat-langchain.git
   cd sql-chat-langchain
2. **Create a Conda Environment**
   ```bash
   conda create -n sqlchat_env python=3

3. **Install Required Packages**
   Install all the required packages from the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
4. **Set Up Environment Variables**
  Create a .env file in the root directory to store your database credentials. Add the following lines:
   ```bash
    MYSQL_HOST=your_mysql_host
    MYSQL_USER=your_mysql_user
    MYSQL_PASSWORD=your_mysql_password
    MYSQL_DATABASE=your_database_name
Replace your_mysql_host, your_mysql_user, your_mysql_password, and your_database_name with your actual MySQL credentials.

5.**Use Streamlit to run the application.**
   ```bash
    streamlit run app.py

import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
import dotenv


# Load environment variables
dotenv.load_dotenv()

loader = PyPDFLoader(
    # "/Users/rafaeldavila/Documents/Duke/Internships/CV  Rafael Davila-Bugarin.pdf"
    "/Users/rafaeldavila/Documents/Duke/Internships/Rafael CV test.pdf"
)
data = loader.load()

# change this to 1_000
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, length_function=len, chunk_overlap=10
)

documents = text_splitter.split_documents(data)


# embedding_openai = OpenAIEmbeddings(model="text-embedding-3-small")


# create the open-source embedding function
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# load it into Chroma
db = Chroma.from_documents(documents, embedding_function)

# query it
query = "What is Rafael Davila experience"
docs = db.similarity_search(query)

# print results
print(docs[0].page_content)


# We can get the source, and page.
# print(data[0].metadata)

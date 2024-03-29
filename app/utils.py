# import pyodbc
from azure.storage.blob import BlobServiceClient
import datetime
import os
from pinecone import Pinecone
# from PyPDF2 import PdfReader
from .cleaning_utils import *
from .uploading_vdb_utils import *
from sqlalchemy import create_engine


def login_to_resources(): 
    '''
    This function logs into the Azure Resources and Pinecone
    Args:
        None
    Returns:
        container_client (BlobClient): The Azure Blob Storage container client
        index (Index): The Pinecone index
        engine (Engine): The SQLAlchemy engine
    '''
    # Create a SQLAlchemy engine using the MySQL connection details
    engine = create_engine(
        f"mysql+mysqlconnector://{os.getenv('MYSQL_ADMIN')}:{os.getenv('MYSQL_PASS')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MY_SQL_DATABASE')}"
    )

    # Pinecone Connection
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("chatarena")

    # Azure Blob Storage Connection String
    blob_connect_str = os.getenv("BLOB_CONNECTION_STR")
    container_name = os.getenv("BLOB_CONTAINER")

    blob_service_client = BlobServiceClient.from_connection_string(blob_connect_str)
    container_client = blob_service_client.get_container_client(container_name)

    # return conn_str, container_client
    return container_client, index, engine


def upload_data_to_server(file, owner_name, owner_netid, owner_affiliation, subject):
    '''
    This function uploads the file to Azure Blob Storage and the metadata 
    to Pinecone and Azure MySQL along with the embeddings and tags
    Args:
        file (FileStorage): The file to be uploaded
        owner_name (str): The name of the owner
        owner_netid (str): The netid of the owner
        owner_affiliation (str): The affiliation of the owner
        subject (str): The subject of the file
    Returns:
        int: 1 if the upload was successful, 0 if it failed
    '''
    # Login to Azure Resources
    # conn_str, container_client = login_to_resources()
    container_client, index, engine = login_to_resources()

    # Get file metadata
    file_type = os.path.splitext(file.filename)[1]
    timestamp = datetime.datetime.now()

    # Create a unique blob name
    blob_name = f"{timestamp.strftime('%Y%m%d%H%M%S')}-{file.filename}"
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the file to Azure Blob Storage
    try:
        blob_client.upload_blob(file.stream, overwrite=True)
    except Exception as e:
        print(e)
        return 0

    # Store Metadata in SQL Database
    blob_url = f"{blob_client.url}"

    # We still need to add what
    # is going to be incorporated from SSO

    metadata = {
        "file name": file.filename,
        "file type": file_type,
        "name": owner_name,
        "dukeNetID": owner_netid,
        "dukePrimaryAffiliation": owner_affiliation,
        "subject": subject,
        "timestamp": timestamp,
        "blob url": blob_url,
    }

    # Embedding
    try:
        embeddings = embeddings_from_type(file_type=file_type, file=file)
    except Exception as e:
        print(f"The embedding didn't worked\n Error: {e}")
        return 0

    # Vectorizing
    try:
        vectors, ids = generating_vetors(embeddings, metadata, netid="rd278")
        embeddings["ID"] = ids
    except Exception as e:
        print(f"The vectorization didn't worked\n Error: {e}")
        return 0

    # Uploading to Pinecone
    try:
        index.upsert(vectors)
    except Exception as e:
        print(f"The uploading to Pinecone didn't worked\n Error: {e}")
        return 0

    # Uploading to Azure MySQL
    try:
        embeddings[["ID", "document"]].to_sql(
            name="documents_values", con=engine, if_exists="append", index=False
        )
    except Exception as e:
        print(f"The uploading to MySQL didn't worked\n Error: {e}")
        return 0

    # print stuff for offline debugging
    # print(f"file name: {file.filename}")
    # print(f"file type: {file_type}")
    # print(f"name: {owner_name}")
    # print(f"subject: {subject}")
    # print(f"timestamp: {timestamp}")
    # print(f"blob url: {blob_url}")

    return 1

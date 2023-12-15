import pyodbc
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Azure SQL Database Connection String
conn_str = os.getenv("DB_CONNECTION_STRING")

# Azure Blob Storage Connection String
blob_connect_str = os.getenv("BLOB_CONNECTION_STRING")
container_name = os.getenv("BLOB_CONTAINER_NAME")
blob_service_client = BlobServiceClient.from_connection_string(blob_connect_str)
container_client = blob_service_client.get_container_client(container_name)

def upload_data_to_server(file, owner_name, subject):
    # Get file metadata
    file_type = os.path.splitext(file.filename)[1]
    timestamp = datetime.now()

    # Create a unique blob name
    blob_name = f"{timestamp.strftime('%Y%m%d%H%M%S')}-{file.filename}"
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the file to Azure Blob Storage
    blob_client.upload_blob(file.stream, overwrite=True)

    # Connect to Azure SQL Database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Store Metadata in SQL Database
    blob_url = f"{blob_client.url}"
    cursor.execute("INSERT INTO FileMetadata (OwnerName, TimeStamp, Subject, FileName, FileType, BlobUrl) VALUES (?, ?, ?, ?, ?, ?)",
                   owner_name, timestamp, subject, file.filename, file_type, blob_url)
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()

    # print stuff for offline debugging
    print(f"file name: {file.filename}")
    print(f"file type: {file_type}")
    print(f"name: {owner_name}")
    print(f"subject: {subject}")
    print(f"timestamp: {timestamp}")
    print(f"blob url: {blob_url}")

    return None


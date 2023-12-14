from datetime import datetime
import os

# Sample function to demonstrate interaction with Azure
def upload_to_azure(file, name, subject):
    # Code to upload file to Azure
    # Get the current timestamp
    timestamp = datetime.now()
    timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
    # Get the file type
    file_type = os.path.splitext(file.filename)[-1]

    # TODO: implement the logic to load the code to the database.

    # For now, just print the values to the console
    # print the file name and return
    print(f"file name: {file.filename}")
    print(f"file type: {file_type}")
    print(f"name: {name}")
    print(f"subject: {subject}")
    print(f"timestamp: {timestamp}")
    
    return None


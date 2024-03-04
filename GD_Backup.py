import hou
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import HttpError

CREDENTIALSFILE = hou.parm('credentialsFile').eval()
TOKENFILE = CREDENTIALSFILE.strip(CREDENTIALSFILE.split("/")[-1]) + "token.json"
BACKUPDIR = hou.parm('BackUpDir').eval()
GOOGLEDRIVEDIR = hou.parm('GoogleDriveDir').eval()
SCOPES =["https://www.googleapis.com/auth/drive"]

creds = None

def authenticate():
    if os.path.exists(TOKENFILE):
        creds = Credentials.from_authorized_user_file(TOKENFILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds._refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALSFILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKENFILE, 'w') as token:
            token.write(creds.to_json())    
    return creds

def getFolderId(): # or create the folder if it doesn't exist yet
    creds = authenticate()
    service = build("drive", "v3", credentials= creds)

    response = service.files().list(
        q="name='"+ GOOGLEDRIVEDIR +"' and mimeType='application/vnd.google-apps.folder' and trashed = false",
        spaces='drive'
    ).execute()

    if not response['files']:
            #print("folder not found so I'll make it") 
            file_metadata = {
                "name": GOOGLEDRIVEDIR,
                "mimeType": "application/vnd.google-apps.folder"
            }
            file = service.files().create(body=file_metadata, fields="id").execute()
            folder_id = file.get('id')

    else:
        folder_id = response['files'][0]['id']

    return(folder_id) 

def uploadFiles():
    try: 
        creds = authenticate() 
        service = build("drive", "v3", credentials= creds)
        folder_id = getFolderId()

        for file in os.listdir(BACKUPDIR):
            file_metadata = {
                "name": file,
                "parents": [folder_id]
            }

            media = MediaFileUpload(f"{BACKUPDIR}/{file}")
            upload_file = service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields="id").execute()
            
            print("Backed up file: " + file)

    except HttpError as error:
        print("Error: " + str(error))

def getList():
    creds = authenticate()
    service = build("drive", "v3", credentials= creds)
    folderId = getFolderId()
    files =[]
    response = service.files().list(
        q= "'" + folderId + "' in parents and trashed = false",
        spaces='drive'
    ).execute()
    FileList = response.get('files',[])

    string = "" # clean the string
    for file in FileList:
        string += file.get("name") + "\n"
        # print(f'Found file: {file.get("name")}, {file.get("id")}')

    files.extend(response.get("files", []))
    resultString = string.rstrip("\n") # remove the last return
    if len(FileList) == 0:
        resultString = "no files found"
    hou.parm('list').set(resultString)   


"""There is a HDA that comes with this code and that needs this code in the Scripts section:
#######
    import hou
    from importlib import reload
    from RebelWay import GD_Backup
    reload(GD_Backup)
######         

    There are 2 steps, first you cache the incomming geo to a backupdir that you can specify.
    Then you can upload the created cache file to a google drive directory that you can also specify.
    If the google Drive directory does not exist, it will be created for you.
    With the getList function you can check if the file is actually on the google drive.
    ToDo: check if the file already exists in the google drive dir and make a versioning system.
"""
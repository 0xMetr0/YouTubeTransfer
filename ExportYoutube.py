import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
outputfile = "youtube_data.json" #File data will be saved to
client_secrets_file = "SECRET.json" #File containing OAuth 2.0 Client ID of target

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    data = {
        "liked_videos": getlikes(youtube),
        "playlists": getplaylists(youtube),
        "subscriptions": getsubscriptions(youtube)
    }

    # Save data to a file
    with open(outputfile, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Data has been collected and saved to {outputfile}")

def getlikes(youtube):
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            myRating="like",
            maxResults=50
        )
        response = request.execute()
        return response["items"]
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
        return []

def getplaylists(youtube):
    try:
        playlists = []
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        )
        response = request.execute()
        playlists.extend(response["items"])

        for playlist in playlists:
            playlist["videos"] = getlistitem(youtube, playlist["id"])

        return playlists
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
        return []

def getlistitem(youtube, playlist_id):
    try:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()
        return response["items"]
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
        return []

def getsubscriptions(youtube):
    try:
        request = youtube.subscriptions().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        )
        response = request.execute()
        return response["items"]
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    main()
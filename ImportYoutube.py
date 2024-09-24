import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


inputfile = "youtube_data.json"############################ Place Youtube Data Here
apikey = "SECRET.json" #File containing OAuth 2.0 Client ID of target
token = "token.json" # Optional token method

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube"
]

QUOTA_LIMIT = 10000

QUOTA_COSTS = {
    "videos.rate": 50,
    "subscriptions.insert": 50,
    "playlists.insert": 50,
    "playlistItems.insert": 50
}

class QuotaExceededError(Exception):
    pass
def getauthenticated():
    creds = None
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                apikey, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token, 'w') as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

def checkquota(quotaused, action):
    newquota = quotaused + QUOTA_COSTS.get(action, 0)
    if newquota > QUOTA_LIMIT:
        raise QuotaExceededError(f"Quota limit exceeded. Current: {quotaused}, Action: {action}, Cost: {QUOTA_COSTS.get(action, 0)}")
    return newquota

def likevideos(youtube, videoIDs, quotaused):
    remaining_videos = []
    for videoID in videoIDs:
        try:
            quotaused = checkquota(quotaused, "videos.rate")
            youtube.videos().rate(
                id=videoID,
                rating="like"
            ).execute()
            quotaused += QUOTA_COSTS["videos.rate"]
            print(f"Liked video: {videoID}")
        except QuotaExceededError:
            remaining_videos.extend(videoIDs[videoIDs.index(videoID):])
            break
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred while liking video {videoID}: {e}")
    return quotaused, remaining_videos

def subtochannels(youtube, channelIDs, quotaused):
    remainingchannels = []
    for channelID in channelIDs:
        try:
            quotaused = checkquota(quotaused, "subscriptions.insert")
            youtube.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": channelID
                        }
                    }
                }
            ).execute()
            quotaused += QUOTA_COSTS["subscriptions.insert"]
            print(f"Subscribed to channel: {channelID}")
        except QuotaExceededError:
            remainingchannels.extend(channelIDs[channelIDs.index(channelID):])
            break
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred while subscribing to channel {channelID}: {e}")
    return quotaused, remainingchannels

def createplaylist(youtube, title, videoIDs, quotacount):
    remainingvideos = []
    try:
        quotacount = checkquota(quotacount, "playlists.insert")
        playlist = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": f"Playlist created from {inputfile}"
                },
                "status": {
                    "privacyStatus": "private"
                }
            }
        ).execute()
        quotacount += QUOTA_COSTS["playlists.insert"]

        playlistID = playlist["id"]
        print(f"Created playlist: {title} (ID: {playlistID})")

        for videoID in videoIDs:
            try:
                quotacount = checkquota(quotacount, "playlistItems.insert")
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlistID,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": videoID
                            }
                        }
                    }
                ).execute()
                quotacount += QUOTA_COSTS["playlistItems.insert"]
                print(f"Added video {videoID} to playlist {playlistID}")
            except QuotaExceededError:
                remainingvideos.extend(videoIDs[videoIDs.index(videoID):])
                break
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred while adding video {videoID} to playlist: {e}")

    except QuotaExceededError:
        remainingvideos = videoIDs
    except googleapiclient.errors.HttpError as e:
        print(f"An error occurred while creating the playlist: {e}")

    return quotacount, remainingvideos

def saveexcessdata(remdata):
    with open("remaining_youtube_data.json", "w") as f:
        json.dump(remdata, f, indent=4)
    print("Remaining data saved to remaining_youtube_data.json")

def main():
    youtube = getauthenticated()
    quotaused = 0

    with open(inputfile, "r") as f: 
        data = json.load(f)

    remainingdata = {}

    # Like videos
    liked_video_ids = [video["id"] for video in data["liked_videos"]]
    quotaused, remaining_videos = likevideos(youtube, liked_video_ids, quotaused)
    if remaining_videos:
        remainingdata["liked_videos"] = remaining_videos

    # Subscribe to channels
    channel_ids = [sub["snippet"]["resourceId"]["channelId"] for sub in data["subscriptions"]]
    quotaused, remaining_channels = subtochannels(youtube, channel_ids, quotaused)
    if remaining_channels:
        remainingdata["subscriptions"] = remaining_channels

    # Create a playlist with videos from the first playlist in the data
    if data["playlists"]:
        playlist = data["playlists"][0]
        playlist_title = playlist["snippet"]["title"]
        video_ids = [video["contentDetails"]["videoId"] for video in playlist["videos"]]
        quotaused, remaining_playlist_videos = createplaylist(youtube, f"Imported: {playlist_title}", video_ids, quotaused)
        if remaining_playlist_videos:
            remainingdata["playlist_videos"] = remaining_playlist_videos

    print(f"Total quota used: {quotaused}")

    if remainingdata:
        saveexcessdata(remainingdata)

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    main()
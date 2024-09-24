# YouTubeTransfer
Tool to transfer likes, subscriptions, and playlists from one account to another

## Scripts

1. `ExportYoutube.py`: Exports data from a YouTube account.
2. `ImportYoutube.py`: Imports data into a YouTube account.

## Prerequisites

- Python 3.6 or higher
- Google account with YouTube access
- Google Cloud Project with YouTube Data API v3 enabled
- OAuth 2.0 Client ID (Desktop app)

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/B0nB0ned/YouTubeTransfer.git
   cd YouTubeTransfer
   ```

2. Install required packages:
   ```
   pip install google-auth-oauthlib google-api-python-client
   ```

3. Set up your Google Cloud Project and obtain OAuth 2.0 credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop app)
   - Download the client configuration and save it as `SECRET.json` in the project directory
   - Go to the OAuth consent screen and add the users you wish to import/export to the "Test users" list

## Usage

### Exporting Data

1. Run the export script:
   ```
   python ExportYoutube.py
   ```
2. Follow the authentication process in your web browser.
3. The script will create a `youtube_data.json` file containing your YouTube data.

### Importing Data

1. Ensure you have the `youtube_data.json` file in the project directory.
2. Run the import script:
   ```
   python ImportYoutube.py
   ```
3. Follow the authentication process for the target YouTube account.
4. The script will import the data into the new account.

## Notes

- The import process is subject to YouTube API quota limits. If the quota is exceeded, the remaining data will be saved to `remaining_youtube_data.json`.
- Imported playlists will be set to "private" by default.
- Be cautious when using these scripts, as they involve sensitive account data.

## Limitations

- The scripts currently handle a limited set of YouTube data (liked videos, playlists, and subscriptions).
- API quota limitations may prevent importing all data in one session.

## Contributing

Contributions to improve these scripts are welcome. Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Google or YouTube. Use these scripts at your own risk and ensure you comply with YouTube's terms of service.

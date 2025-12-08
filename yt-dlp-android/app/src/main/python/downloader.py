import yt_dlp
import os

def download_video(url, target_directory):
    """
    Downloads a video from the given URL to the target directory.
    """
    try:
        # Ensure the target directory exists
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        ydl_opts = {
            # Save the file in the specified directory
            'outtmpl': os.path.join(target_directory, '%(title)s.%(ext)s'),
            # Select the best video and audio format and merge them
            'format': 'bestvideo+bestaudio/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "Download complete!"

    except Exception as e:
        return f"Error: {str(e)}"

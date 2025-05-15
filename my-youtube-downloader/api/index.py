from flask import Flask, request, jsonify, send_file, render_template
from pytubefix import YouTube
import os
import tempfile
import uuid

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    try:
        yt = YouTube(url)
        video_info = {
            'success': True,
            'title': yt.title,
            'author': yt.author,
            'thumbnail': yt.thumbnail_url,
            'available_resolutions': [stream.resolution for stream in yt.streams.filter(progressive=True)]
        }
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'highest')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    try:
        yt = YouTube(url)

        # Create a temporary directory for the download
        temp_dir = tempfile.mkdtemp()

        if quality == 'audio':
            # Download audio only
            stream = yt.streams.filter(only_audio=True).first()
            file_path = stream.download(output_path=temp_dir)

            # Rename to mp3
            base, ext = os.path.splitext(file_path)
            new_file = base + '.mp3'
            os.rename(file_path, new_file)
            file_path = new_file
        else:
            # Handle video quality selection
            if quality == 'highest':
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            else:
                # Try to get the requested resolution
                stream = yt.streams.filter(progressive=True, resolution=quality).first()

                # If not available, get the highest resolution
                if not stream:
                    stream = yt.streams.filter(progressive=True).get_highest_resolution()

            # Download the video
            file_path = stream.download(output_path=temp_dir)

        # Get just the filename
        filename = os.path.basename(file_path)

        # Return the file
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# This is important for Vercel
if __name__ == '__main__':
    app.run(debug=True)
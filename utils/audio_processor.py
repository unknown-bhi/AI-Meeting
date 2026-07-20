import yt_dlp
from pydub import AudioSegment
import os
import tempfile

Download_dir = 'downloades'
os.makedirs(Download_dir, exist_ok= True)

def download_youtube_audio(url):
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        # ----- BOHOT ZAROORI OPTIONS (Shaam ke time ke liye) -----
        'retries': 15,                
        'fragment_retries': 15,       
        'timeout': 600,              # 10 minute timeout (subah default 20 sec tha)
        'sleep_interval': 5,         
        'max_sleep_interval': 30,    
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],  # Android client sab se stable hai
                'skip': ['hls', 'dash'],             # HLS skip karein (timeout kam karega)
            }
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Cache clear karein (purani info expire ho gayi thi)
        ydl.cache.remove()
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        wav_file = filename.rsplit('.', 1)[0] + '.wav'
        return wav_file


def convert_to_wav(input_path : str):
    """Convert any audio/video file to wav format using pydub"""

    output_path =os.path.splitext(input_path)[0] + '_converted.wav'
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)#16khz
    audio.export(output_path, format ='wav')
    
    return output_path





def chunk_audio(wav_path : str ,chunk_minutes : int = 10)  -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks =[]

    for i, start in enumerate(range(0, len(audio),chunk_ms)):
        chunk =audio[start : start + chunk_ms]
        chunk_path =f'{wav_path}_chunk{i}.wav'
        chunk.export(chunk_path , format ="wav")

        chunks.append(chunk_path)

    return chunks

def process_input(source : str) -> list:
    if source.startswith('https://') or source.startswith('http://'):
        print('Detect youtube link. Downloading audio.......')
        wav_path =download_youtube_audio(source)
    else:
        print('Detect local file. converting to wav....')
        wav_path =convert_to_wav(source)

    print('chunking audio ......')
    chunks = chunk_audio(wav_path)  
    print(f'audio ready -- {len(chunks)} chunk(s) created.')

    

    return chunks

def get_audio_only(source : str):
    if source.startswith('https://') or source.startswith('http://'):
        print('Detect youtube link. Downloading audio.......')
        wav_path =download_youtube_audio(source)
    else:
        print('Detect local file. converting to wav....')
        wav_path =convert_to_wav(source)

    orignal_audio = wav_path

    return orignal_audio
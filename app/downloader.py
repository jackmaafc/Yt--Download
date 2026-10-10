import threading
import uuid
import time
import os
import yt_dlp

class DownloadManager:
    def __init__(self):
        self.queue = []
        self.jobs = {}
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def add_job(self, urls, format_type, quality, save_path):
        job_ids = []
        with self.lock:
            for url in urls:
                url = url.strip()
                if not url:
                    continue
                job_id = str(uuid.uuid4())
                self.jobs[job_id] = {
                    'id': job_id,
                    'url': url,
                    'status': 'queued',
                    'progress': 0,
                    'speed': '',
                    'eta': '',
                    'filename': '',
                    'error': '',
                    'format_type': format_type,
                    'quality': quality,
                    'save_path': save_path,
                    'added_at': time.time()
                }
                self.queue.append(job_id)
                job_ids.append(job_id)
        return job_ids

    def get_all_jobs(self):
        with self.lock:
            return list(self.jobs.values())

    def remove_job(self, job_id):
        with self.lock:
            if job_id in self.jobs:
                if self.jobs[job_id]['status'] not in ['downloading', 'processing']:
                    del self.jobs[job_id]
                    if job_id in self.queue:
                        self.queue.remove(job_id)

    def clear_completed(self):
        with self.lock:
            to_remove = [job_id for job_id, job in self.jobs.items() if job['status'] in ['completed', 'failed']]
            for job_id in to_remove:
                del self.jobs[job_id]

    def _worker(self):
        while True:
            job_id = None
            with self.lock:
                if self.queue:
                    job_id = self.queue.pop(0)
            
            if job_id:
                self._process_job(job_id)
            else:
                time.sleep(1)

    def _process_job(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                return
            job = self.jobs[job_id]
            job['status'] = 'downloading'
            url = job['url']
            format_type = job['format_type']
            quality = job['quality']
            save_path = job['save_path']

        # We now have a local ffmpeg binary!
        ffmpeg_path = os.path.join(os.path.dirname(__file__), '..', 'bin', 'ffmpeg')
        
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'keepvideo': False,
            'ffmpeg_location': ffmpeg_path if os.path.exists(ffmpeg_path) else None,
            'merge_output_format': 'mp4',
            'extractor_args': {'youtube': ['player_client=android,web']}
        }

        if format_type == 'audio_mp3':
            # Audio only with high quality conversion to MP3
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif format_type == 'audio_m4a' or format_type == 'audio':
            # Audio only, no conversion (M4A natively provided by YouTube in most cases)
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        else:
            # Video
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                height = ''.join(filter(str.isdigit, quality))
                if height:
                    ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
                else:
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        def progress_hook(d):
            with self.lock:
                if job_id in self.jobs:
                    j = self.jobs[job_id]
                    if d['status'] == 'downloading':
                        j['status'] = 'downloading'
                        total = d.get('total_bytes') or d.get('total_bytes_estimate')
                        if total and d.get('downloaded_bytes'):
                            j['progress'] = round(d['downloaded_bytes'] / total * 100, 1)
                        speed = d.get('speed')
                        if speed:
                            j['speed'] = f"{speed / 1024 / 1024:.2f} MB/s"
                        eta = d.get('eta')
                        if eta:
                            j['eta'] = f"{eta}s"
                        
                        filename = d.get('filename')
                        if filename:
                            j['filename'] = os.path.basename(filename)

                    elif d['status'] == 'finished':
                        j['status'] = 'processing'
                        j['progress'] = 100
                        filename = d.get('filename')
                        if filename:
                            j['filename'] = os.path.basename(filename)

        def postprocessor_hook(d):
            with self.lock:
                if job_id in self.jobs:
                    j = self.jobs[job_id]
                    if d['status'] == 'started':
                        pp = d.get('postprocessor')
                        if pp in ('FFmpegExtractAudio', 'ExtractAudio'):
                            j['status'] = 'converting to mp3...'
                        elif pp in ('FFmpegVideoConvertor', 'FFmpegMerger', 'Merger'):
                            j['status'] = 'merging video...'
                        elif pp == 'MoveFiles':
                            j['status'] = 'finishing up...'
                        else:
                            j['status'] = 'processing...'

        ydl_opts['progress_hooks'] = [progress_hook]
        ydl_opts['postprocessor_hooks'] = [postprocessor_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id]['status'] = 'completed'
                    self.jobs[job_id]['progress'] = 100
                    
        except Exception as e:
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id]['status'] = 'failed'
                    self.jobs[job_id]['error'] = str(e)

manager = DownloadManager()

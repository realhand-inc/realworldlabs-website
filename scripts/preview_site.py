"""Serve the static build locally, including the custom 404 and production cache classes."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import re

PUBLIC=Path(__file__).resolve().parents[1]/'public'

class PreviewHandler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.xml':'application/xml','.webmanifest':'application/manifest+json','.svg':'image/svg+xml','.woff2':'font/woff2','.ico':'image/x-icon'}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(PUBLIC),**kwargs)
    def send_head(self):
        self._video_range = None
        path = Path(self.translate_path(self.path))
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', self.headers.get('Range', ''))
        if path.suffix.lower() != '.mp4' or not path.is_file() or not match:
            return super().send_head()
        size = path.stat().st_size
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last or 0))
        end = min(int(last), size - 1) if first and last else size - 1
        if not size or start >= size or start > end or (not first and not int(last or 0)):
            self.send_response(416)
            self.send_header('Content-Range', 'bytes */' + str(size))
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        source = path.open('rb')
        source.seek(start)
        self._video_range = (start, end)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        return source
    def copyfile(self, source, outputfile):
        if self._video_range is None:
            return super().copyfile(source, outputfile)
        remaining = self._video_range[1] - self._video_range[0] + 1
        while remaining:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)
    def end_headers(self):
        path=urlsplit(self.path).path
        cache='public, max-age=0, must-revalidate'
        if path.startswith('/assets/'):cache='public, max-age=3600, must-revalidate'
        if re.fullmatch(r'/assets/build/(?:pages|ecosystem)\.[0-9a-f]{12}\.(?:css|js)',path):
            cache='public, max-age=31536000, immutable'
        if path.lower().endswith('.mp4'):
            self.send_header('Accept-Ranges','bytes')
        self.send_header('Cache-Control',cache)
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        super().end_headers()
    def send_error(self,code,message=None,explain=None):
        page=PUBLIC/'404.html'
        if code==404 and page.is_file():
            data=page.read_bytes()
            self.send_response(404)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('X-Robots-Tag','noindex')
            self.end_headers()
            if self.command!='HEAD':self.wfile.write(data)
        else:super().send_error(code,message,explain)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=3000)
    args=parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1',args.port),PreviewHandler) as server:
        print('Local preview: http://localhost:'+str(args.port)+'/',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':main()

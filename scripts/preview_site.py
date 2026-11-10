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
    def end_headers(self):
        path=urlsplit(self.path).path
        cache='public, max-age=0, must-revalidate'
        if path.startswith('/assets/'):cache='public, max-age=3600, must-revalidate'
        if re.fullmatch(r'/assets/build/(?:pages|ecosystem)\.[0-9a-f]{12}\.(?:css|js)',path):
            cache='public, max-age=31536000, immutable'
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

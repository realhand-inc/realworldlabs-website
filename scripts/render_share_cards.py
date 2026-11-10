"""Render tracked share PNGs and browser icons. Optional authoring tool, not a deploy step.
Requires a local preview server and an isolated Chromium debug instance on port 9228.
Python dependency for this optional tool: websocket-client.
"""
from pathlib import Path
import argparse
import base64
import json
import time
import struct
import urllib.request
import websocket
from share_cards import ROOT, card_data, render_document, icon_svg

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--origin',default='http://localhost:3000')
    parser.add_argument('--debug-port',type=int,default=9228)
    args=parser.parse_args()
    debug='http://localhost:'+str(args.debug_port)
    targets=json.load(urllib.request.urlopen(debug+'/json',timeout=5))
    target=next(t for t in targets if t['type']=='page')
    ws=websocket.create_connection(target['webSocketDebuggerUrl'],origin=debug,timeout=20)
    count=0
    def call(method,params=None):
        nonlocal count
        count+=1
        ws.send(json.dumps(dict(id=count,method=method,params=params or {})))
        while True:
            response=json.loads(ws.recv())
            if response.get('id')==count:
                if 'error' in response:raise RuntimeError(response['error'])
                return response.get('result',{})
    def ev(code):
        result=call('Runtime.evaluate',dict(expression=code,returnByValue=True,awaitPromise=True))
        if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
        return result.get('result',{}).get('value')
    def document(html,width,height):
        call('Emulation.setDeviceMetricsOverride',dict(width=width,height=height,deviceScaleFactor=1,mobile=False))
        call('Emulation.setEmulatedMedia',dict(features=[dict(name='prefers-reduced-motion',value='reduce')]))
        call('Page.setDocumentContent',dict(frameId=frame,html=html))
        ev("""(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r})));return true})()""")
        missing=ev("[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src)")
        if missing:raise RuntimeError('Missing image assets: '+str(missing))
        time.sleep(.08)
    def png(path):
        data=call('Page.captureScreenshot',dict(format='png',captureBeyondViewport=False))
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(base64.b64decode(data['data']))
    call('Page.enable')
    call('Network.enable')
    call('Network.setCacheDisabled',dict(cacheDisabled=True))
    call('Page.navigate',dict(url=args.origin+'/'))
    time.sleep(.3)
    frame=call('Page.getFrameTree')['frameTree']['frame']['id']
    for card in card_data():
        document(render_document(card,args.origin),1200,630)
        target=ROOT/'public/assets/share'/(card['key']+'.png')
        png(target)
        print('Rendered',target.name,flush=True)
    brand=ROOT/'public/assets/brand'
    (brand/'favicon.svg').write_bytes(icon_svg().encode('utf-8'))
    for size,name in [(16,'favicon-16.png'),(32,'favicon-32.png'),(180,'apple-touch-icon.png'),(192,'icon-192.png'),(512,'icon-512.png')]:
        html='<html><head><base href="'+args.origin+'/"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden}img{display:block;width:100%;height:100%}</style></head><body><img src="/assets/brand/favicon.svg"></body></html>'
        document(html,size,size)
        png(brand/name)
    frames=[(brand/('favicon-'+str(size)+'.png')).read_bytes() for size in [16,32]]
    offset=6+16*len(frames)
    icon=struct.pack('<HHH',0,1,len(frames))
    for size,frame in zip([16,32],frames):
        icon+=struct.pack('<BBBBHHII',size,size,0,0,1,32,len(frame),offset)
        offset+=len(frame)
    (ROOT/'public/favicon.ico').write_bytes(icon+b''.join(frames))
    ws.close()
    print('Rendered 12 share cards, 5 browser icons, and the ICO fallback.',flush=True)

if __name__=='__main__':main()

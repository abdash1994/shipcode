"""Test server for the browser tests: serves the repo root on :8765 with a CSP like claude.ai's,
and mounts the offline Python/SQLite runtime at /rt/ from $SHIPCODE_RT (default /tmp/shipcode-rt,
a folder holding pyodide/ and sqljs/). Run by tests/e2e33-36 automatically."""
import http.server,functools,os,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
RT=os.environ.get('SHIPCODE_RT','/tmp/shipcode-rt')
class H(http.server.SimpleHTTPRequestHandler):
    extensions_map={**http.server.SimpleHTTPRequestHandler.extensions_map,'.wasm':'application/wasm','.zip':'application/zip','.json':'application/json'}
    def translate_path(self,path):
        if path.split('?')[0].startswith('/rt/'):
            return os.path.join(RT,path.split('?')[0][4:].replace('/',os.sep))
        return super().translate_path(path)
    def end_headers(self):
        self.send_header('Content-Security-Policy',"default-src 'self'; connect-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; worker-src 'self' blob:; img-src 'self' data:")
        super().end_headers()
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8765),functools.partial(H,directory=ROOT)).serve_forever()

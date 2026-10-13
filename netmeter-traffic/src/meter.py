"""Host network counters -> atomic snapshot -> internal Umbrel widget endpoint."""
import json
import os
from pathlib import Path
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

STATE = Path('/state/traffic.json')


def counters(text):
    result = {}
    for line in text.splitlines():
        if ':' not in line:
            continue
        name, values = line.rsplit(':', 1)
        fields = values.split()
        if len(fields) >= 16:
            result[name.strip()] = (int(fields[0]), int(fields[8]))
    return result


def select_interface(requested, routes, available):
    if requested != 'auto':
        if requested not in available:
            raise ValueError('Interface not found: ' + requested)
        return requested
    candidates = []
    for line in routes.splitlines()[1:]:
        f = line.split()
        if len(f) >= 8 and f[1] == '00000000' and f[7] == '00000000':
            if int(f[3], 16) & 1 and f[0] in available and f[0] != 'lo':
                candidates.append((int(f[6]), f[0]))
    if not candidates:
        raise ValueError('No IPv4 default route. Set NET_INTERFACE in app settings.')
    return min(candidates)[1]


def rate(previous, current, elapsed):
    if previous is None or elapsed <= 0 or any(b < a for a, b in zip(previous, current)):
        return None
    return [(b - a) * 8 / elapsed / 1_000_000 for a, b in zip(previous, current)]


def collect():
    previous = None
    previous_name = None
    previous_time = time.monotonic()
    while True:
        now = time.monotonic()
        snapshot = {'timestamp': time.time(), 'rates': None, 'interface': '—', 'interfaces': []}
        try:
            available = counters(Path('/proc/net/dev').read_text())
            snapshot['interfaces'] = sorted(available)
            name = select_interface(os.environ.get('NET_INTERFACE', 'auto').strip(),
                                    Path('/proc/net/route').read_text(), available)
            values = available[name]
            snapshot.update(interface=name,
                            rates=rate(previous if previous_name == name else None,
                                       values, now - previous_time))
            snapshot['status'] = 'OK' if snapshot['rates'] is not None else 'Sampling…'
            previous, previous_name = values, name
        except (OSError, ValueError) as exc:
            snapshot['status'] = str(exc)
            previous, previous_name = None, None
        previous_time = now
        temporary = STATE.with_suffix('.tmp')
        temporary.write_text(json.dumps(snapshot), encoding='utf-8')
        temporary.replace(STATE)
        time.sleep(2)


def read_snapshot():
    try:
        data = json.loads(STATE.read_text(encoding='utf-8'))
        age = time.time() - data['timestamp']
        if age > 10 or age < -2:
            data.update(rates=None, status='Collector data is stale')
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return {'rates': None, 'interface': '—', 'interfaces': [], 'status': 'Waiting for collector'}


def widget(data):
    rates = data.get('rates')
    return {'type': 'three-stats', 'refresh': '2s', 'link': '', 'items': [
        {'subtext': 'Download RX', 'text': f'{rates[0]:.2f} Mbps' if rates else '—'},
        {'subtext': 'Upload TX', 'text': f'{rates[1]:.2f} Mbps' if rates else '—'},
        {'subtext': 'Interface' if rates else data['status'], 'text': data['interface']},
    ]}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/':
            body = Path(__file__).with_name('index.html').read_bytes()
            kind = 'text/html; charset=utf-8'
        elif path in ('/widget', '/status'):
            data = read_snapshot()
            body = json.dumps(widget(data) if path == '/widget' else data).encode()
            kind = 'application/json'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    if sys.argv[1:] == ['collect']:
        collect()
    elif sys.argv[1:] == ['serve']:
        HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
    else:
        raise SystemExit('Use: meter.py collect|serve')

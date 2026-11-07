import csv
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
HTTP_METRICS = ROOT / 'data' / 'http_metrics.csv'
DNS_METRICS = ROOT / 'data' / 'dns_metrics.csv'
THRESHOLD = 3
STALE_SECONDS = 90

HTML = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Enterprise Observability V4</title><style>
body{font:15px Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:25px}h1{margin-bottom:6px}p,.muted{color:#94a3b8}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:20px 0}.card,.panel{background:#1e293b;border-radius:12px;padding:20px}.label{color:#94a3b8;font-size:13px}.value{font-size:28px;font-weight:bold;margin-top:10px}.good{color:#4ade80}.bad{color:#fb7185}.warn{color:#fbbf24}.panel{margin-top:20px;overflow-x:auto}table{width:100%;border-collapse:collapse}th,td{padding:10px;text-align:left;border-bottom:1px solid #334155}th{color:#94a3b8}svg{width:100%;height:auto;max-height:240px}
</style></head><body><h1>Enterprise Observability Dashboard V4</h1><p>Local HTTP + DNS synthetic monitoring | Refreshes every 10 seconds</p>
<h2>HTTP Monitoring</h2><div class="cards"><div class="card"><div class="label">HTTP health</div><div class="value" id="http-health">--</div></div><div class="card"><div class="label">HTTP successful checks</div><div class="value" id="http-availability">--</div></div><div class="card"><div class="label">HTTP response time</div><div class="value" id="http-latency">--</div></div><div class="card"><div class="label">HTTP incidents</div><div class="value" id="http-incidents">--</div></div></div>
<h2>DNS Monitoring</h2><div class="cards"><div class="card"><div class="label">DNS health</div><div class="value" id="dns-health">--</div></div><div class="card"><div class="label">DNS successful checks</div><div class="value" id="dns-availability">--</div></div><div class="card"><div class="label">DNS resolution time</div><div class="value" id="dns-latency">--</div></div><div class="card"><div class="label">DNS incidents</div><div class="value" id="dns-incidents">--</div></div></div>
<div class="panel"><h2>Collection freshness</h2><p id="http-freshness">HTTP: Loading...</p><p id="dns-freshness">DNS: Loading...</p></div>
<div class="panel"><h2>HTTP response-time trend</h2><svg id="http-chart" viewBox="0 0 800 240" role="img" aria-label="HTTP latency trend"></svg><p id="http-chart-info"></p></div>
<div class="panel"><h2>DNS resolution-time trend</h2><svg id="dns-chart" viewBox="0 0 800 240" role="img" aria-label="DNS resolution trend"></svg><p id="dns-chart-info"></p></div>
<div class="panel"><h2>Recent HTTP checks</h2><table><thead><tr><th>UTC timestamp</th><th>Status</th><th>Latency</th><th>Error</th></tr></thead><tbody id="http-results"></tbody></table></div>
<div class="panel"><h2>Recent DNS checks</h2><table><thead><tr><th>UTC timestamp</th><th>Domain</th><th>Status</th><th>Resolution</th><th>IP addresses</th><th>Error</th></tr></thead><tbody id="dns-results"></tbody></table></div>
<div class="panel"><h2>HTTP incident history</h2><table><thead><tr><th>ID</th><th>Severity</th><th>Status</th><th>Opened (UTC)</th><th>Recovered (UTC)</th></tr></thead><tbody id="http-history"></tbody></table></div>
<div class="panel"><h2>DNS incident history</h2><table><thead><tr><th>ID</th><th>Severity</th><th>Status</th><th>Opened (UTC)</th><th>Recovered (UTC)</th></tr></thead><tbody id="dns-history"></tbody></table></div>
<script>
function cell(tr,value){const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td)}
function fill(id,rows,keys){const target=document.getElementById(id);target.replaceChildren();rows.forEach(item=>{const tr=document.createElement('tr');keys.forEach(k=>cell(tr,item[k]));target.appendChild(tr)})}
function drawChart(prefix,rows,metric){const svg=document.getElementById(prefix+'-chart'),info=document.getElementById(prefix+'-chart-info');svg.replaceChildren();const data=rows.slice().reverse().filter(r=>r.status==='UP').map(r=>Number(r[metric])).filter(Number.isFinite);if(data.length<2){info.textContent='Waiting for at least two successful measurements.';return}const ns='http://www.w3.org/2000/svg',W=800,H=240,pad=35,max=Math.max(10,...data),points=data.map((v,i)=>[pad+i*(W-2*pad)/(data.length-1),H-pad-v/max*(H-2*pad)]);const line=document.createElementNS(ns,'polyline');line.setAttribute('points',points.map(p=>p.join(',')).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#38bdf8');line.setAttribute('stroke-width','3');svg.appendChild(line);points.forEach((p,i)=>{const circle=document.createElementNS(ns,'circle');circle.setAttribute('cx',p[0]);circle.setAttribute('cy',p[1]);circle.setAttribute('r','4');circle.setAttribute('fill','#4ade80');const title=document.createElementNS(ns,'title');title.textContent=data[i].toFixed(2)+' ms';circle.appendChild(title);svg.appendChild(circle)});info.textContent='Showing '+data.length+' successful checks | Peak: '+Math.max(...data).toFixed(2)+' ms'}
function show(prefix,d,metric){const health=document.getElementById(prefix+'-health');health.textContent=d.health;health.className='value '+(d.health==='UP'?'good':d.health==='DOWN'?'bad':'warn');document.getElementById(prefix+'-availability').textContent=d.availability_pct+'%';document.getElementById(prefix+'-latency').textContent=d.latest_latency_ms===null?'--':d.latest_latency_ms+' ms';document.getElementById(prefix+'-incidents').textContent=d.incidents.length;document.getElementById(prefix+'-freshness').textContent=prefix.toUpperCase()+' freshness: '+d.freshness+' | Last check: '+(d.last_check||'No data');drawChart(prefix,d.recent,metric);fill(prefix+'-history',d.incidents.map((r,i)=>({...r,id:i+1})),['id','severity','status','opened_at','recovered_at'])}
async function refresh(){try{const response=await fetch('/api/status',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);const d=await response.json();show('http',d.http,'latency_ms');show('dns',d.dns,'resolution_ms');fill('http-results',d.http.recent,['timestamp_utc','status','latency_ms','error']);fill('dns-results',d.dns.recent,['timestamp_utc','domain','status','resolution_ms','ip_addresses','error'])}catch(e){document.getElementById('http-freshness').textContent='Dashboard API unavailable: '+e.message;document.getElementById('dns-freshness').textContent='Dashboard API unavailable: '+e.message}}
refresh();setInterval(refresh,10000);
</script></body></html>'''


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8-sig') as handle:
        return list(csv.DictReader(handle))


def summarize(path, metric):
    rows = [r for r in read_rows(path) if r.get('status', '').strip().upper() in ('UP', 'DOWN')]
    up = sum(r['status'].strip().upper() == 'UP' for r in rows)
    incidents, active, failures = [], None, 0
    for row in rows:
        status = row['status'].strip().upper()
        if status == 'DOWN':
            failures += 1
            if failures == THRESHOLD and active is None:
                active = {'opened_at': row.get('timestamp_utc', ''), 'recovered_at': None, 'severity': 'CRITICAL', 'status': 'OPEN'}
                incidents.append(active)
        else:
            failures = 0
            if active is not None:
                active['recovered_at'] = row.get('timestamp_utc', '')
                active['status'] = 'RECOVERED'
                active = None
    latest = rows[-1] if rows else None
    freshness, health = 'NO DATA', 'UNKNOWN'
    if latest:
        try:
            checked = datetime.fromisoformat(latest['timestamp_utc'])
            if checked.tzinfo is None:
                raise ValueError('Timestamp must include UTC offset')
            age = (datetime.now(timezone.utc) - checked).total_seconds()
            freshness = 'FRESH' if 0 <= age <= STALE_SECONDS else 'STALE'
            health = latest['status'].strip().upper() if freshness == 'FRESH' else 'STALE'
        except (ValueError, TypeError, KeyError):
            freshness, health = 'INVALID TIMESTAMP', 'UNKNOWN'
    try:
        latency = float(latest[metric]) if latest and latest.get(metric) else None
    except (ValueError, TypeError):
        latency = None
    return {'health': health, 'freshness': freshness, 'availability_pct': round(100 * up / len(rows), 2) if rows else 0, 'latest_latency_ms': latency, 'last_check': latest.get('timestamp_utc') if latest else None, 'recent': list(reversed(rows[-10:])), 'incidents': incidents}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/':
            content = HTML.encode('utf-8')
            mime = 'text/html; charset=utf-8'
        elif path == '/api/status':
            try:
                payload = {'http': summarize(HTTP_METRICS, 'latency_ms'), 'dns': summarize(DNS_METRICS, 'resolution_ms')}
                content = json.dumps(payload).encode('utf-8')
                mime = 'application/json; charset=utf-8'
            except (OSError, csv.Error, UnicodeError, KeyError, TypeError) as exc:
                self.send_error(500, 'Metrics data unavailable')
                print(f'Metrics error: {exc}', flush=True)
                return
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8769), Handler)
    print('Dashboard V4: http://127.0.0.1:8769', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nDashboard stopped.')
    finally:
        server.server_close()

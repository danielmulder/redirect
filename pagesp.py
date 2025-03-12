import json
import time
import requests
from requests.exceptions import RequestException, Timeout

# ✅ Configuratie voor Rate Limiting
REQUESTS_PER_MINUTE = 25
user_requests = {}

# ✅ Rate Limiting Functie
def is_rate_limited(ip: str) -> bool:
    now = time.time()
    requests = user_requests.get(ip, [])
    requests = [t for t in requests if now - t < 60]

    if len(requests) >= REQUESTS_PER_MINUTE:
        return True

    requests.append(now)
    user_requests[ip] = requests
    return False

# ✅ Retry Functie
def fetch_with_retry(url, params, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                return response.json(), 200
            else:
                print(f"API fout bij poging {attempt + 1}: {response.status_code}")
        except Timeout:
            print(f"Timeout bij poging {attempt + 1} (Timeout: {timeout}s)")
        except RequestException as e:
            print(f"Netwerkfout bij poging {attempt + 1}: {e}")
        time.sleep(2)
    return None, 500

# ✅ Haal data uit PageSpeed Insights
def get_pagespeed_insights(api_key, url, strategy='mobile'):
    endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
    params = {
        'url': url,
        'key': api_key,
        'strategy': strategy
    }

    data, status = fetch_with_retry(endpoint, params)
    if not data:
        return {"status": status, "error": "Failed to retrieve data after multiple attempts."}

    audits = data.get('lighthouseResult', {}).get('audits', {})

    # ✅ Core Web Vitals (Belangrijkste metingen)
    core_web_vitals = {
        "score": data.get('lighthouseResult', {}).get('categories', {}).get('performance', {}).get('score', 0) * 100,
        "fcp": audits.get('first-contentful-paint', {}).get('displayValue', ''),
        "lcp": audits.get('largest-contentful-paint', {}).get('displayValue', ''),
        "fid": audits.get('max-potential-fid', {}).get('displayValue', ''),
        "cls": audits.get('cumulative-layout-shift', {}).get('displayValue', ''),
        "speed_index": audits.get('speed-index', {}).get('displayValue', '')
    }

    # ✅ Opportunities (Waar tijd bespaard kan worden)
    opportunities = []
    for key, audit in audits.items():
        if 'details' in audit and 'overallSavingsMs' in audit['details']:
            opportunities.append({
                "title": audit.get("title"),
                "savings_ms": audit['details']['overallSavingsMs']
            })
            if len(opportunities) >= 3:  # Maximaal 3 tonen voor overzichtelijkheid
                break

    # ✅ Diagnostics (Max 3 grootste problemen tonen)
    diagnostics = []
    for key, audit in audits.items():
        if 'details' in audit and 'items' in audit['details']:
            diagnostics.append({
                "title": audit.get("title"),
                "description": audit.get("description")
            })
            if len(diagnostics) >= 3:
                break

    # ✅ Resultaat formatteren zoals gevraagd
    result = {
        "status": status,
        "url": url,
        "core_web_vitals": core_web_vitals,
        "opportunities": opportunities,
        "diagnostics": diagnostics
    }

    return result

# ✅ Hoofdfunctie voor Serverless Deployment
def main(args):
    start_time = time.perf_counter()

    ip = args.get("__ow_headers", {}).get("x-forwarded-for", "unknown")
    if is_rate_limited(ip):
        return {
            "body": json.dumps({
                "data": [{
                    "status": 429,
                    "error": "Too many requests. Try again later.",
                    "retry_after": 60
                }],
                "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }),
            "statusCode": 429
        }

    url = args.get("url")
    if not url:
        return {"body": json.dumps({
            "data": [{
                "status": 400,
                "error": "No valid URL provided!"
            }],
            "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), "statusCode": 400}

    strategy = args.get("strategy", "mobile")
    if strategy not in ["mobile", "desktop"]:
        return {"body": json.dumps({
            "data": [{
                "status": 400,
                "error": "Invalid strategy! Use 'mobile' or 'desktop'"
            }],
            "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), "statusCode": 400}

    api_key = 'AIzaSyDGX43RfgNyg41L508S_ddD3gET3dXZWRg'
    if not api_key:
        return {"body": json.dumps({
            "data": [{
                "status": 400,
                "error": "Missing API key for PageSpeed Insights!"
            }],
            "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
        }), "statusCode": 400}

    # ✅ Haal resultaten op uit PageSpeed Insights
    result = get_pagespeed_insights(api_key, url, strategy)
    total_time = round((time.perf_counter() - start_time) * 1000, 2)

    # ✅ Resultaat teruggeven in gevraagde structuur
    return {
        "body": json.dumps({
            "data": [result],
            "processing_time_ms": total_time
        }),
        "statusCode": result.get('status', 500)
    }

from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        location = params.get("location", ["Crossville, TN"])[0]
        service = params.get(
            "service",
            ["tree removal dangerous tree storm damage"]
        )[0]

        api_key = os.environ.get("YEP_API_KEY")

        if not api_key:
            return self.send_json(
                {"error": "YEP_API_KEY is not configured."},
                500
            )

        query = f'"{location}" "{service}" need help OR looking for'

        url = (
            "https://api.ahrefs.com/v3/yep/web?"
            + urllib.parse.urlencode({
                "q": query,
                "limit": 10
            })
        )

        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))

            return self.send_json({
                "success": True,
                "location": location,
                "service": service,
                "results": data
            })

        except Exception as e:
            return self.send_json({
                "success": False,
                "error": str(e)
            }, 500)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(body)

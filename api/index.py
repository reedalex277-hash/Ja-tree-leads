from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request
import urllib.error


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        location = params.get("location", ["Crossville, TN"])[0]
        service = params.get(
            "service",
            ["tree removal dangerous tree"]
        )[0]

        api_key = os.environ.get("YEP_API_KEY")

        if not api_key:
            return self.send_json(
                {
                    "success": False,
                    "error": "YEP_API_KEY is not configured."
                },
                500
            )

        query = (
            f'"{location}" '
            f'("{service}" OR "tree service") '
            '("need" OR "looking for" OR "recommend")'
        )

        payload = json.dumps({
            "query": query,
            "type": "basic",
            "limit": 10,
            "language": ["en"],
            "location": "US",
            "safe_search": True
        }).encode("utf-8")

        request = urllib.request.Request(
            "https://platform.yep.com/api/search",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            return self.send_json({
                "success": True,
                "search_location": location,
                "service": service,
                "results": data.get("results", [])
            })

        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8")

            return self.send_json({
                "success": False,
                "status": error.code,
                "error": details
            }, error.code)

        except Exception as error:
            return self.send_json({
                "success": False,
                "error": str(error)
            }, 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
        service = params.get("service", ["tree removal"])[0]

        api_key = os.environ.get("YELP_API_KEY")

        if not api_key:
            return self.send_json(
                {
                    "success": False,
                    "error": "YELP_API_KEY is not configured"
                },
                500
            )

        query = {
            "location": location,
            "term": service,
            "limit": 10,
            "language": "en"
        }

        search_url = (
            "https://api.yelp.com/v3/businesses/search?"
            + urllib.parse.urlencode(query)
        )

        request = urllib.request.Request(
            search_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))

            return self.send_json(
                {
                    "success": True,
                    "search_location": location,
                    "service": service,
                    "results": data.get("businesses", [])
               

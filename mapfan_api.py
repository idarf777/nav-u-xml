import json
import re
import requests
from requests.exceptions import Timeout


def host_from_url(url: str) -> str:
    m = re.match(r'^http.?://(.+?)/.*$', url)
    return m[1] if m else None


def sanitize(s: str) -> str:
    return re.sub(r'[\r\t\n\000"]', '', s)


class MapfanApi:
    URL = {
        "auth": "https://auth.mapfan.com/api/authorization/v1/local",
        "address": "https://mapfan.com/api/addresses/centers/",
        "bookmark": "https://api.mapfan.com/api/bookmarks/v1/spots",
        "origin": "https://mapfan.com",
        "referer": "https://mapfan.com/",
        "referer-address": "https://mapfan.com/map/bookmarks/view-map"
    }
    COMMON_HDR = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, text/plain, */*',
        'Access-Control-Allow-Origin': '*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'
    }
    TIMEOUT = (5.0, 5.0)

    access_token = None

    def authorize(self, loginid: str, password: str):
        payload = {"loginid": sanitize(loginid), "password": sanitize(password)}
        url = self.URL.get('auth')
        hdr = {
            "Cache-Control": "no-cache",
            "Host": host_from_url(url),
            "Origin": self.URL.get("origin"),
            "Referer": self.URL.get("referer")
        }
        response = requests.post(
            url,
            json.dumps(payload),
            headers = dict(self.COMMON_HDR, **hdr),
            timeout = self.TIMEOUT
        )
        data = response.json()
        self.access_token = data["access_token"]    # refresh_tokenは無視する

    def get_address(self, lat: float, lon: float) -> dict:
        url = f"{self.URL.get('address')}%.12f,%.12f" % (lat, lon)
        hdr = {
            "Host": host_from_url(url),
            "Referer": self.URL.get("referer-address"),
            "authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(
            url,
            headers = dict(self.COMMON_HDR, **hdr),
            timeout = self.TIMEOUT
        )
        return response.json()

    def post_bookmark(self, lat: float, lon: float, name: str, address: str):
        payload = {"lat": lat, "lon": lon, "name": sanitize(name), "address": sanitize(address), "genreCodeL": 6, "genreCodeM": 10001, "genreName": "住所"}
        url = self.URL.get('bookmark')
        hdr = {
            "Cache-Control": "no-cache",
            "Origin": self.URL.get("origin"),
            "Referer": self.URL.get("referer"),
            "authorization": f"Bearer {self.access_token}"
        }
        response = requests.post(
            url,
            json.dumps(payload),
            headers = dict(self.COMMON_HDR, **hdr),
            timeout = self.TIMEOUT
        )
        return response.json()


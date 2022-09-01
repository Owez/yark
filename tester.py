import requests

print(
    requests.put(
        "http://127.0.0.1:7667/channel/demo/z6y0mx2flRY", json={"title": "nice one", "timestamp": "1:08"}
    ).json()
)

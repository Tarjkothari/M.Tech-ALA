import socket
from datetime import datetime
from flask import Flask, jsonify
application = Flask(__name__)
NOTICES = [
"Mid-semester exam timetable published",
"Library open till 8 PM during exams",
"Submit Active Learning Activity reports on the GMIU Web Portal",
]
@application.route("/")
def home():
items = "".join(f"<li>{n}</li>" for n in NOTICES)
return f"""
<html><head><title>Campus Notice Board</title></head>
<body style="font-family:Arial;margin:40px">
<h1>Campus Notice Board</h1>
<ul>{items}</ul>
<hr>
<p>Served by instance: <b>{socket.gethostname()}</b></p>
<p>Time (server): {datetime.utcnow():%Y-%m-%d %H:%M:%S} UTC</p>
</body></html>
"""
@application.route("/health")
def health():
return jsonify(status="ok")
if __name__ == "__main__":
application.run(host="0.0.0.0", port=8000) # local testing only
from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>IP Awareness Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        .box {
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 12px;
            background: #f8f8f8;
        }
        code {
            background: #eee;
            padding: 2px 6px;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <h1>Internet Safety Demo</h1>
    <div class="box">
        <p><strong>Notice:</strong> This page logs your IP address for cybersecurity awareness training.</p>
        <p>Your detected IP is: <code>{{ ip }}</code></p>
        <p>This shows that websites you visit can often see your IP address automatically.</p>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    forwarded = request.headers.get("X-Forwarded-For", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.remote_addr

    with open("ip_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | IP: {ip} | User-Agent: {request.headers.get('User-Agent')}\n")

    return render_template_string(HTML, ip=ip)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import assemblyai as aai
from flask import Flask, request, render_template_string, Response

app = Flask(__name__)
import os
aai.settings.api_key = os.environ.get("ASSEMBLYAI_API_KEY")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Transcriber</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; display: flex; justify-content: center; padding: 40px 20px; }
        .card { background: white; border-radius: 16px; padding: 40px; max-width: 620px; width: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        h1 { font-size: 28px; color: #1a1a2e; margin-bottom: 8px; }
        p.subtitle { color: #666; margin-bottom: 30px; }
        label { font-weight: bold; color: #333; display: block; margin-bottom: 6px; }
        input[type=text], input[type=file] { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 16px; font-size: 15px; }
        button { background: #4f46e5; color: white; border: none; padding: 14px 28px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 8px; }
        button:hover { background: #4338ca; }
        .result { margin-top: 30px; }
        .result h2 { color: #1a1a2e; margin-bottom: 12px; }
        pre { background: #f8f9fa; padding: 20px; border-radius: 8px; white-space: pre-wrap; font-size: 15px; line-height: 1.7; border: 1px solid #e0e0e0; }
        .download { display: inline-block; margin-top: 16px; background: #10b981; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-size: 15px; }
        .download:hover { background: #059669; }
        .spinner { display: none; text-align: center; margin-top: 20px; }
        .spinner p { color: #4f46e5; font-size: 16px; margin-top: 10px; }
        .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #4f46e5; margin: 0 4px; animation: bounce 1.2s infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-12px)} }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎙️ Audio Transcriber</h1>
        <p class="subtitle">Upload any audio file and get a full transcript with speaker names.</p>
        <form method="POST" enctype="multipart/form-data" onsubmit="showSpinner()">
            <label>Audio File</label>
            <input type="file" name="audio" accept="audio/*" required><br>
            <label>Speaker A name</label>
            <input type="text" name="speaker_a" placeholder="e.g. Mr. Semir">
            <label>Speaker B name</label>
            <input type="text" name="speaker_b" placeholder="e.g. John">
            <label>Speaker C name (optional)</label>
            <input type="text" name="speaker_c" placeholder="e.g. Mary">
            <button type="submit">Transcribe</button>
        </form>
        <div class="spinner" id="spinner">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            <p>Transcribing your audio, please wait...</p>
        </div>
        {% if transcript %}
        <div class="result">
            <h2>Transcript</h2>
            <pre>{{ transcript }}</pre>
            <a class="download" href="/download?text={{ transcript | urlencode }}">⬇ Download Transcript</a>
        </div>
        {% endif %}
    </div>
    <script>
        function showSpinner() {
            document.getElementById('spinner').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = None
    if request.method == "POST":
        file = request.files["audio"]
        file.save("temp_audio.wav")
        speaker_names = {
            "A": request.form.get("speaker_a") or "Speaker A",
            "B": request.form.get("speaker_b") or "Speaker B",
            "C": request.form.get("speaker_c") or "Speaker C",
        }
        config = aai.TranscriptionConfig(
            speech_models=["universal-2"],
            speaker_labels=True
        )
        transcriber = aai.Transcriber()
        result = transcriber.transcribe("temp_audio.wav", config=config)
        transcript = ""
        for utterance in result.utterances:
            name = speaker_names.get(utterance.speaker, f"Speaker {utterance.speaker}")
            transcript += f"{name}: {utterance.text}\n\n"
    return render_template_string(HTML, transcript=transcript)

@app.route("/download")
def download():
    text = request.args.get("text", "")
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=transcript.txt"}
    )

if __name__ == "__main__":

    app.run(debug=True)

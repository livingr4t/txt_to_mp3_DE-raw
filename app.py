from flask import Flask, request, send_file
from gtts import gTTS
from pydub import AudioSegment
import os

app = Flask(__name__)

# Ręczne ustawienie ścieżek do FFmpeg i FFprobe
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

@app.route('/')
def home():
    return '''
        <h1>Konwersja tekstu na mowę, język niemiecki</h1>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <label>Wczytaj plik TXT:</label><br>
            <input type="file" name="file" accept=".txt" required><br><br>
            <label>Czas pauzy między zdaniami (w sekundach):</label><br>
            <input type="number" name="pause" value="1" min="1" required><br><br>
            <button type="submit">Prześlij i wygeneruj MP3</button>
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    # Sprawdzenie, czy plik został przesłany
    if 'file' not in request.files:
        return "Błąd: Nie przesłano pliku tekstowego!", 400

    file = request.files['file']
    pause = int(request.form.get('pause', 1))  # Pauza między zdaniami w sekundach

    try:
        # Odczytanie treści pliku tekstowego
        content = file.read().decode('utf-8')
        sentences = [sentence.strip() for sentence in content.split('.') if sentence.strip()]

        combined_audio = AudioSegment.empty()

        # Generowanie dźwięku dla każdego zdania
        for sentence in sentences:
            tts = gTTS(sentence, lang='de')  # 'pl' dla polskiego (zmień, jeśli inny język)
            tts.save("temp.mp3")
            audio = AudioSegment.from_file("temp.mp3")
            combined_audio += audio
            # Dodanie ciszy między zdaniami
            combined_audio += AudioSegment.silent(duration=pause * 1000)

        # Eksport wynikowego pliku audio
        output_file = "output.mp3"
        combined_audio.export(output_file, format="mp3")
        os.remove("temp.mp3")  # Usunięcie pliku tymczasowego

        return send_file(output_file, as_attachment=True)

    except FileNotFoundError as e:
        return f"Błąd: Nie znaleziono FFmpeg lub ffprobe. Szczegóły: {str(e)}", 500
    except Exception as e:
        return f"Błąd: Wystąpił nieoczekiwany problem: {str(e)}", 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the port from the environment variable
    app.run(debug=True, host='0.0.0.0', port=port)  # Bind to 0.0.0.0 for external access


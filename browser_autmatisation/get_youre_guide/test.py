import requests
import json
import os
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
def test(model):

    url = f"{ollama_url}/api/generate"

    # Korrigierter Payload basierend auf Ihrer Anfrage:
    # - "model": Der Name des Modells, das Sie verwenden möchten.
    # - "prompt": Der Text, den das Modell generieren soll (fehlt in Ihrem Beispiel).
    # - "keep_alive": 0 (bedeutet, das Modell wird nach der Antwort entladen)

    payload = {
        "model": model,
        "keep_alive": 0,
        "stream": False  # Wichtig: Auf False setzen, um eine einzelne JSON-Antwort zu erhalten
    }

    print(f"Sende Anfrage an {url} mit Payload:")
    print(json.dumps(payload, indent=2))

    try:
        # Sende den POST-Request
        response = requests.post(url, json=payload)

        # Überprüfe den Statuscode
        if response.status_code == 200:
            print("\n--- Erfolgreiche Antwort (200 OK) ---")
            # Antwort als JSON ausgeben
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            
            print("\nInfo: Das Modell wird jetzt aufgrund von 'keep_alive: 0' entladen.")
            
        elif response.status_code == 404:
            print(f"\nFehler (404): Modell '{payload['model']}' nicht gefunden.")
            print("Stellen Sie sicher, dass das Modell mit 'ollama pull' heruntergeladen wurde.")
            
        else:
            print(f"\n--- Fehler: Statuscode {response.status_code} ---")
            print("Antwort-Text:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print(f"\nFehler: Verbindung zu {url} fehlgeschlagen.")
        print("Stellen Sie sicher, dass der Ollama-Server läuft.")
    except Exception as e:
        print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
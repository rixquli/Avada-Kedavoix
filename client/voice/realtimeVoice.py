import sounddevice as sd
import json
import threading
import queue
from vosk import Model, KaldiRecognizer

MODEL_PATH = "client/voice/vosk-model-small-fr-0.22"

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# File thread-safe pour les commandes vocales détectées
voice_commands = queue.Queue()

# Sorts disponibles avec leurs variations/synonymes
SPELLS = {
    "spell": {
        "keywords": ["spell"],
        "message": "Spell lancé",
        "action": "SPELL",
    },
    "feu": {
        "keywords": ["boule de feu", "plus de feu"],
        "message": "Boule de feu lancée",
        "action": "FIREBALL",
    },
    "glace": {
        "keywords": ["pic de glace", "pic de classe"],
        "message": "Jet de glace lancé",
        "action": "ICE",
    },
    "foudre": {
        "keywords": ["éclair", "tonnerre"],
        "message": "Éclair lancé",
        "action": "LIGHTNING",
    },
    "flèche": {
        "keywords": ["flèche"],
        "message": "Flèche lancé",
        "action": "ARROW",
    },
    "avada": {
        "keywords": ["avada", "cadavre"],
        "message": "Sort interdit",
        "action": "DEATH",
    },
}


def detect_spell(text: str) -> dict | None:
    """Détecte un sort dans le texte parlé. Retourne le sort ou None."""
    text = text.lower()
    for spell_name, spell_data in SPELLS.items():
        for keyword in spell_data["keywords"]:
            if keyword in text:
                return {"name": spell_name, **spell_data}
    return None


def voice_listener(verbose=False):
    """
    Thread d'écoute vocale non-bloquant.
    Utilise un callback pour capturer l'audio en continu.
    """
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        """Callback appelé par sounddevice à chaque bloc audio."""
        audio_queue.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=2000,  # Réduit pour plus de réactivité
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        if verbose:
            print("Écoute vocale démarrée...")

        while True:
            data = audio_queue.get()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()

                if text:
                    spell = detect_spell(text)
                    if spell:
                        voice_commands.put(spell)
                        if verbose:
                            print(f"[DÉTECTÉ] {text} → {spell['action']}")
                    else:
                        if verbose:
                            print(f"[IGNORÉ] {text}")


def start_voice_recognition():
    """Démarre le thread de reconnaissance vocale."""
    thread = threading.Thread(target=voice_listener, daemon=True)
    thread.start()
    return thread


def get_voice_command() -> dict | None:
    """
    Récupère une commande vocale si disponible (non-bloquant).
    À appeler dans la boucle de jeu.
    """
    try:
        return voice_commands.get_nowait()
    except queue.Empty:
        return None


def main():
    start_voice_recognition()

    # Simulation de boucle de jeu
    import time

    while True:
        # Dans le vrai jeu, cette fonction serait appelée à chaque frame
        command = get_voice_command()
        if command:
            print(f"\n>>> {command['message']}")
            print(f"    Action à envoyer au serveur: {command['action']}\n")

        time.sleep(0.016)  # ~60 FPS


if __name__ == "__main__":
    main()

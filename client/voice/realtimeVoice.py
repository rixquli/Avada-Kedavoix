try:
    import sounddevice as sd
except Exception:
    sd = None
import json
import os
import sys
import threading
import queue
from vosk import Model, KaldiRecognizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client.classes.spell import SpellList

MODEL_PATH = "client/voice/vosk-model-small-fr-0.22"

# Permet de print ou non dans le terminal utile pour tester
verbose = True

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# File pour les commandes vocales détectées
voice_commands = queue.Queue()

# Sorts disponibles avec leurs variations/synonymes
SPELLS = {
    # "spell": {
    #     "keywords": ["spell"],
    #     "message": "Spell lancé",
    #     "action": "SPELL",
    # },
    "teleportation": {
        "keywords": ["téléportation"],
        "message": "Téléportation lancée",
        "action": SpellList.TELEPORTATION,
    },
    "feu": {
        "keywords": ["boule de feu", "plus de feu"],
        "message": "Boule de feu lancée",
        "action": SpellList.FIREBALL,
    },
    "glace": {
        "keywords": ["pic de glace", "pic de classe"],
        "message": "Jet de glace lancé",
        "action": SpellList.ICE,
    },
    "soin": {
        "keywords": ["soin"],
        "message": "Vie régénérée",
        "action": SpellList.HEAL,
    },
    # "foudre": {
    #     "keywords": ["éclair", "tonnerre"],
    #     "message": "Éclair lancé",
    #     "action": "LIGHTNING",
    # },
    # "flèche": {
    #     "keywords": ["flèche"],
    #     "message": "Flèche lancé",
    #     "action": "ARROW",
    # },
    # "avada": {
    #     "keywords": ["avada", "cadavre"],
    #     "message": "Sort interdit",
    #     "action": "DEATH",
    # },
}


def detect_spell(text: str) -> dict | None:
    """Détecte un sort dans le texte parlé. Retourne le sort ou None."""
    text = text.lower()
    for spell_name, spell_data in SPELLS.items():
        for keyword in spell_data["keywords"]:
            if keyword in text:
                return {"name": spell_name, **spell_data}
    return None


def voice_listener():
    """
    Thread d'écoute vocale non-bloquant.
    Utilise un callback pour capturer l'audio en continu.
    """
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        """Callback appelé par sounddevice à chaque bloc audio."""
        audio_queue.put(bytes(indata))

    if sd is None:
        return

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=800,  # Réduit pour plus de réactivité
        dtype="int16",
        latency="low",
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
        return (
            voice_commands.get_nowait()
        )  # recupere la derniere commande enregistrer et la retire
    except queue.Empty:
        return None


def main():
    global verbose
    verbose = True
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

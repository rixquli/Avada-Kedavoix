try:
    import sounddevice as sd
except Exception:
    sd = None
import json
import os
import re
import sys
import threading
import queue
from vosk import Model, KaldiRecognizer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from client.classes.spell import SpellList

MODEL_PATH = os.path.join(os.path.dirname(__file__), "vosk-model-small-fr-0.22")

# Permet de print ou non dans le terminal utile pour tester
verbose = True

model = None
recognizer = None

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


def count_keyword_occurrences(text: str, keyword: str) -> int:
    """Compte les occurrences exactes d'un mot-clé ou d'une expression."""
    pattern = rf"(?<!\w){re.escape(keyword.lower())}(?!\w)"
    return len(re.findall(pattern, text.lower()))


def detect_spells_stream(text: str, previous_counts: dict[str, int]) -> list[dict]:
    """Retourne les nouveaux sorts détectés dans un résultat partiel ou final."""
    triggered_spells = []
    normalized_text = text.lower().strip()

    for spell_name, spell_data in SPELLS.items():
        current_count = 0
        for keyword in spell_data["keywords"]:
            current_count += count_keyword_occurrences(normalized_text, keyword)

        previous_count = previous_counts.get(spell_name, 0)
        new_occurrences = max(0, current_count - previous_count)

        for _ in range(new_occurrences):
            triggered_spells.append({"name": spell_name, **spell_data})

        previous_counts[spell_name] = current_count

    return triggered_spells


def voice_listener():
    """
    Thread d'écoute vocale non-bloquant.
    Utilise un callback pour capturer l'audio en continu.
    """
    audio_queue = queue.Queue()
    partial_detection_counts = {}

    def audio_callback(indata, frames, time, status):
        """Callback appelé par sounddevice à chaque bloc audio."""
        audio_queue.put(bytes(indata))

    if sd is None or recognizer is None:
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
                    spells = detect_spells_stream(text, partial_detection_counts)
                    if spells:
                        for spell in spells:
                            voice_commands.put(spell)
                            if verbose:
                                print(f"[DÉTECTÉ] {text} → {spell['action']}")
                    elif verbose:
                        if verbose:
                            print(f"[IGNORÉ] {text}")

                partial_detection_counts.clear()
            else:
                partial_result = json.loads(recognizer.PartialResult())
                partial_text = partial_result.get("partial", "").strip()

                if not partial_text:
                    continue

                spells = detect_spells_stream(partial_text, partial_detection_counts)
                for spell in spells:
                    voice_commands.put(spell)
                    if verbose:
                        print(f"[STREAM] {partial_text} → {spell['action']}")


def start_voice_recognition():
    """Démarre le thread de reconnaissance vocale."""
    global model, recognizer

    if sd is None:
        if verbose:
            print("Reconnaissance vocale désactivée: module sounddevice indisponible.")
        return None

    if recognizer is None:
        try:
            model = Model(os.path.abspath(MODEL_PATH))
            recognizer = KaldiRecognizer(model, 16000)
        except Exception as exc:
            if verbose:
                print(
                    "Reconnaissance vocale désactivée: modèle Vosk introuvable/invalide à "
                    f"{os.path.abspath(MODEL_PATH)} ({exc})"
                )
            return None

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

import open_taranis as T

import curses
import json
import os
import platform
import subprocess
import sys
import os

argv = sys.argv
config_file = ".agent_config.json"

# ==============================
# The TUI
# ==============================

LOGO_ASCII = """
░        ░░░      ░░░       ░░░░      ░░░   ░░░  ░░        ░░░      ░░
▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒    ▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒
▓▓▓▓  ▓▓▓▓▓        ▓▓       ▓▓▓        ▓▓  ▓  ▓  ▓▓▓▓▓  ▓▓▓▓▓▓      ▓▓
████  █████  ████  ██  ███  ███  ████  ██  ██    █████  ███████████  █
████  █████  ████  ██  ████  ██  ████  ██  ███   ██        ███      ██"""


# ===================
# CONFIGURATION
# ===================

MIN_HEIGHT = 24
MIN_WIDTH = 72
config_file = ".agent_config.json"

# Liste des commandes affichées dans HELP
commands = [
    "/exit        = quit the TUI",
    "/            = return",
    "/help        = show the command list",
    "/show api    = show registered API",
    "/conf        = configure the agent",
    "/verify conf = check the agent configuration",
    "/load conf   = load the agent configuration",
    "/save conf   = save the agent configuration"
]
nb_commands = len(commands)

# Presets disponibles : (nom, endpoint, modèle par défaut, headers, api key)
PRESETS = [
    ("OpenRouter", "https://openrouter.ai/api/v1", "", {"HTTP-Referer": "https://zanomega.com/open-taranis/","X-Title": "open-taranis"}, "OPENROUTER_API_KEY"),
    ("huggingface", "https://router.huggingface.co/v1", "", {}, "HUGGINGFACE_API_KEY"),
    ("Venice.ai", "https://api.venice.ai/api/v1", "venice-uncensored", {}, "VENICE_API_KEY"),
    ("DeepSeek.ai", "https://api.deepseek.com/v1", "deepseek-chat", {}, "DEEPSEEK_API_KEY"),
    ("X.ai", "https://api.x.ai/v1", "grok-4-1-fast-non-reasoning", {}, "XAI_API_KEY"),
    ("Groq", "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile", {}, "GROQ_API_KEY"),
    ("Mistral.ai", "https://api.mistral.ai/v1", "mistral-large-latest", {}, "MISTRALAI_API_KEY"),
    ("Ollama", "http://localhost:11434/v1", "granite4:7b-a1b-h", {}, "None"),
    ("Kimi Code", "https://api.kimi.com/coding/v1", "defaut", {"User-Agent": "RooCode/3.30.3","HTTP-Referer": "https://github.com/RooVetGit/Roo-Cline","X-Title": "Roo Code"}, "KIMI_CODE_API_KEY"),
]
nb_presets = len(PRESETS)

# ===================
# CLIPBOARD (détection OS)
# ===================

system = platform.system()
clipboard_cmd = None

if system == "Linux":
    try:
        subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, check=True)
        clipboard_cmd = ['xclip', '-selection', 'clipboard', '-o']
    except:
        try:
            subprocess.run(['xsel', '-b'], capture_output=True, check=True)
            clipboard_cmd = ['xsel', '-b']
        except:
            try:
                subprocess.run(['wl-paste'], capture_output=True, check=True)
                clipboard_cmd = ['wl-paste']
            except:
                pass
elif system == "Darwin":
    clipboard_cmd = ['pbpaste']
elif system == "Windows":
    clipboard_cmd = ['powershell', '-command', 'Get-Clipboard']

def get_clipboard():
    """Récupère le contenu du presse-papier selon l'OS détecté."""
    if clipboard_cmd is None:
        return ""
    try:
        result = subprocess.check_output(clipboard_cmd, text=True)
        if system == "Windows":
            result = result.rstrip('\n')
        return result
    except:
        return ""

# ===================
# FONCTIONS AGENT
# ===================

def verify_agent_status(endpoint, api_key, model, default_headers=None):
    """Vérifie que la configuration agent fonctionne avec un appel test."""
    if api_key and os.getenv(api_key):
        api_key = os.getenv(api_key)
    elif not api_key:
        api_key = "None"
    
    request = T.Request(max_tokens=1)
    client = T.Client(None, endpoint, default_headers)

    try:
        request.make(
            client=client,
            model=model,
            messages=[{"role": "user", "content": " "}],
            API_KEY=api_key
        )
    except Exception as e:
        return False, str(e)
    return True, "OK"

def load_agent_config(config=1):
    """Charge la configuration spécifiée depuis le fichier JSON."""
    with open(config_file, "r") as f:
        data = json.load(f)
    conf = data[f"conf{config}"]
    return conf["endpoint"], conf["api_key"], conf["model_used"], conf["default_headers"]

def save_agent_config(endpoint, api_key, model, default_headers=None, config=1):
    """Sauvegarde la configuration dans l'emplacement spécifié."""
    with open(config_file, "r") as f:
        data = json.load(f)
    
    data[f"conf{config}"]["api_key"] = api_key
    data[f"conf{config}"]["endpoint"] = endpoint
    data[f"conf{config}"]["model_used"] = model
    data[f"conf{config}"]["default_headers"] = default_headers or {}
    
    with open(config_file, "w") as f:
        json.dump(data, f, indent=2)

# ===================
# TUI PRINCIPALE
# ===================

def run(stdscr, config=1):
    # Initialisation curses
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()
    
    # Paires de couleurs : (id, foreground, background)
    curses.init_pair(1, curses.COLOR_RED, -1)     # Erreurs / Logo
    curses.init_pair(2, curses.COLOR_WHITE, -1)   # Texte standard
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Avertissements
    curses.init_pair(4, curses.COLOR_GREEN, -1)   # Succès

    # État de l'application
    input_buffer = ""
    display_mode = "NONE"
    text = []
    cursor = 0

    # Rafraîchissement toutes les 100ms (non-bloquant)
    stdscr.timeout(100)

    # Création du fichier de config s'il n'existe pas
    if not os.path.exists(config_file):
        # Détection d'Ollama en local
        default_endpoint = ""
        default_api_key = ""
        default_model = ""
        
        try:
            import urllib.request
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
                data = json.loads(response.read().decode())
                if data.get("models") and len(data["models"]) > 0:
                    default_endpoint = "http://localhost:11434/v1"
                    default_api_key = "None"
                    default_model = data["models"][0].get("name", "")
        except:
            pass
        
        default_config = {
            "version": 1,
            "conf1": {
                "api_key": default_api_key,
                "endpoint": default_endpoint,
                "model_used": default_model,
                "default_headers": {}
            },
            "conf2": {
                "api_key": "",
                "endpoint": "",
                "model_used": "",
                "default_headers": {}
            },
            "conf3": {
                "api_key": "",
                "endpoint": "",
                "model_used": "",
                "default_headers": {}
            },
            "conf4": {
                "api_key": "",
                "endpoint": "",
                "model_used": "",
                "default_headers": {}
            },
            "memory": ["", "", "", ""]
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)

    # Chargement initial de la configuration
    endpoint, API_KEY, model, default_headers = load_agent_config(config)
    agent_status, agent_status_message = verify_agent_status(endpoint, API_KEY, model, default_headers)

    # ===================
    # BOUCLE PRINCIPALE
    # ===================

    while True:
        height, width = stdscr.getmaxyx()
        
        # Vérification taille minimale du terminal
        if height < MIN_HEIGHT or width < MIN_WIDTH:
            stdscr.clear()
            msg = f"Terminal too small: {width}x{height} (min {MIN_WIDTH}x{MIN_HEIGHT})"
            y, x = height // 2, max(0, (width - len(msg)) // 2)
            try:
                stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(y + 1, x, "Resize or press 'q' to quit", curses.color_pair(2))
            except:
                pass
            stdscr.refresh()
            if stdscr.getch() == ord('q'):
                break
            continue
        
        # === AFFICHAGE DU LOGO ===
        stdscr.clear()
        logo_lines = LOGO_ASCII.split('\n')
        logo_height = len(logo_lines)
        
        for i, line in enumerate(logo_lines):
            if i < height - 2:
                try:
                    truncated = line[:width-1]
                    stdscr.addstr(i, 0, truncated, curses.color_pair(1))
                except curses.error:
                    pass
        
        # Zones d'affichage
        content_start = logo_height + 1
        content_end = height - 3
        
        # === GÉNÉRATION DU CONTENU SELON LE MODE ===
        
        if display_mode == "HELP":
            text = ["Commands :"]
            for i, cmd in enumerate(commands):
                prefix = ">" if i == cursor else " "
                text.append(f"{prefix} {cmd}")
                    
        elif display_mode == "API":
            text = [
                "APIs registered :",
                ("- [x]" if os.environ.get('OPENROUTER_API_KEY') else "- [ ]") + " openrouter",
                ("- [x]" if os.environ.get('HUGGINGFACE_API_KEY') else "- [ ]") + " huggingface",
                ("- [x]" if os.environ.get('VENICE_API_KEY') else "- [ ]") + " venice.ai",
                ("- [x]" if os.environ.get('DEEPSEEK_API_KEY') else "- [ ]") + " deepseek.ai",
                ("- [x]" if os.environ.get('XAI_API_KEY') else "- [ ]") + " x.ai",
                ("- [x]" if os.environ.get('MISTRALAI_API_KEY') else "- [ ]") + " mistral.ai",
                ("- [x]" if os.environ.get('GROQ_API_KEY') else "- [ ]") + " groq",
                "",
                "=== Codes ===",
                ("- [x]" if os.environ.get('KIMI_CODE_API_KEY') else "- [ ]") + " Kimi Code",
                "",
                "To show the env var : /show more",
            ]
        
        elif display_mode == 'MORE_API':
            text = [
                "APIs and env_var",
                "- openrouter  = 'OPENROUTER_API_KEY'",
                "- huggingface = 'HUGGINGFACE_API_KEY'",
                "- venice.ai   = 'VENICE_API_KEY'",
                "- deepseek.ai = 'DEEPSEEK_API_KEY'",
                "- x.ai        = 'XAI_API_KEY'",
                "- mistral.ai  = 'MISTRALAI_API_KEY'",
                "- groq        = 'GROQ_API_KEY'",
                "",
                "=== Codes ===",
                "- Kimi Code   = 'KIMI_CODE_API_KEY'"
            ]
        
        elif display_mode == "CONF_AGENT":
            displayed_key = API_KEY if API_KEY.endswith('_API_KEY') else API_KEY[:8] + '*' * 8
            params = [
                ("endpoint ", endpoint),
                ("model    ", model),
                ("api key  ", displayed_key),
            ]
            text = ["Current configuration :"]
            for i, (label, value) in enumerate(params):
                prefix = ">" if i == cursor else " "
                text.append(f"{prefix} {label}: {value}")
            
            # Saut de ligne puis config
            text.append("")
            prefix = ">" if cursor == 3 else " "
            text.append(f"{prefix} config: {config}/4")
        
            # Sauvegarde
            prefix = ">" if cursor == 4 else " "
            text.append(f"{prefix} save config")

            # Vérifier
            prefix = ">" if cursor == 5 else " "
            text.append(f"{prefix} verify config")
            
            # Les preset
            prefix = ">" if cursor == 6 else " "
            text.append(f"{prefix} preset")
        
            # Affichage du message d'erreur si présent
            if not agent_status and agent_status_message and agent_status_message != "OK":
                text.append("")
                text.append(f"{agent_status_message}")
            
            if endpoint == "https://openrouter.ai/api/v1" and not default_headers:
                default_headers = {"HTTP-Referer": "https://zanomega.com/open-taranis/","X-Title": "open-taranis"}
        
        elif display_mode == "PRESET_MENU":
            text = ["Select a preset :"]
            for i, (name, _, _, _, _) in enumerate(PRESETS):
                prefix = ">" if i == cursor else " "
                text.append(f"{prefix} {name}")

        # === AFFICHAGE DU CONTENU ===
        if display_mode != "NONE":
            current_line = content_start
            for line in text:
                if current_line < content_end:
                    try:
                        stdscr.addstr(current_line, 0, line, curses.color_pair(2))
                    except:
                        pass
                    current_line += 1
        
        # === STATUT + SÉPARATEUR ===
        sep_y = height - 2
        input_y = height - 1
        
        separator_width = min(width - 1, MIN_WIDTH - 1)
        dash_color = curses.color_pair(2) | curses.A_DIM
        
        try:
            stdscr.addstr(sep_y, 0, "----", dash_color)
            if agent_status:
                stdscr.addstr(sep_y, 4, " Correct agent configuration ", curses.color_pair(4))
                stdscr.addstr(sep_y, 33, "-" * (separator_width - 33), dash_color)
            else:
                stdscr.addstr(sep_y, 4, " Agent misconfigured. Run '/conf' ! ", curses.color_pair(1))
                stdscr.addstr(sep_y, 40, "-" * (separator_width - 40), dash_color)
        except:
            pass
        
        # === INVITE DE COMMANDE ===
        prompt = f"> {input_buffer}"
        display_prompt = prompt[:width-1]
        try:
            stdscr.addstr(input_y, 0, display_prompt, curses.color_pair(2))
            cursor_x = min(len(prompt), width - 1)
            stdscr.move(input_y, cursor_x)
        except:
            pass
        
        stdscr.refresh()
        
        # === GESTION DES TOUCHES ===
        key = stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            continue

        # Flèches : navigation
        elif key == curses.KEY_UP:
            cursor = max(0, cursor - 1)
        
        elif key == curses.KEY_DOWN:
            if display_mode == "CONF_AGENT":
                max_cursor = 6
            elif display_mode == "PRESET_MENU":
                max_cursor = nb_presets - 1
            else:
                max_cursor = nb_commands - 1
            cursor = min(max_cursor, cursor + 1)
               
        elif key == curses.KEY_LEFT:
            if (display_mode == "CONF_AGENT") and (config > 1) :
                config -= 1
                endpoint, API_KEY, model, default_headers = load_agent_config(config)     
        
        elif key == curses.KEY_RIGHT:
            if (display_mode == "CONF_AGENT") and (config < 4) :
                config += 1
                endpoint, API_KEY, model, default_headers = load_agent_config(config)
        
        # Ctrl+V : coller depuis le presse-papier
        elif key == 22:
            try:
                input_buffer += get_clipboard()
            except:
                pass
        
        # Entrée : validation
        elif key in (10, 13):
            command = input_buffer.strip()

            # Modification des paramètres dans CONF_AGENT
            if display_mode == "CONF_AGENT" and not input_buffer.startswith("/"):
                if cursor == 0:
                    endpoint = input_buffer.strip()
                elif cursor == 1:
                    model = input_buffer.strip()
                elif cursor == 2:
                    API_KEY = input_buffer.strip()
                elif cursor == 3:
                    try:
                        config = int(input_buffer.strip())
                        if 1 <= config <= 4:
                            endpoint, API_KEY, model, default_headers = load_agent_config(config)
                    except ValueError:
                        pass
                elif cursor == 4:
                    if endpoint == "https://openrouter.ai/api/v1" :
                        default_headers = {"HTTP-Referer": "https://zanomega.com/open-taranis/","X-Title": "open-taranis"}
                    save_agent_config(endpoint, API_KEY, model, default_headers, config)
                elif cursor == 5:
                    agent_status, agent_status_message = verify_agent_status(endpoint, API_KEY, model, default_headers)
                elif cursor == 6:
                    display_mode = "PRESET_MENU"
                    cursor = 0
                input_buffer = ""
            
            elif display_mode == "PRESET_MENU" and not input_buffer.startswith("/"):
                if 0 <= cursor < nb_presets:
                    _, endpoint, model, default_headers, API_KEY = PRESETS[cursor]
                display_mode = "CONF_AGENT"
                cursor = 6
                input_buffer = ""
            
            # Sélection par curseur dans HELP
            elif display_mode == "HELP" and not command:
                command = commands[cursor].split("=")[0].strip()
            
            # Commandes
            if command == "/exit":
                break
            
            elif command == "/help":
                display_mode = "HELP"
                cursor = 0
            
            elif command == "/show api":
                display_mode = "API"
            
            elif command == "/show more" and display_mode == "API":
                display_mode = 'MORE_API'
            
            elif command == "/conf":
                display_mode = "CONF_AGENT"
                cursor = 0
            
            elif command == "/verify conf":
                agent_status, agent_status_message = verify_agent_status(endpoint, API_KEY, model, default_headers)

            elif command == "/load conf":
                endpoint, API_KEY, model, default_headers = load_agent_config(config)

            elif command == "/save conf":
                if endpoint == "https://openrouter.ai/api/v1" :
                    default_headers = {"HTTP-Referer": "https://zanomega.com/open-taranis/","X-Title": "open-taranis"}
                save_agent_config(endpoint, API_KEY, model, default_headers, config)
            
            # Commande inconnue : retour au mode par défaut
            elif command and command[0] == "/":
                display_mode = "NONE"
            
            input_buffer = ""
        
        # Backspace : effacer le dernier caractère
        elif key in (127, curses.KEY_BACKSPACE, ord('\b')):
            input_buffer = input_buffer[:-1]
        
        # Échap : vider le buffer
        elif key == 27:
            input_buffer = ""
        
        # Caractères imprimables
        elif 32 <= key <= 126:
            input_buffer += chr(key)

# ==============================
# The args
# ==============================

def main():
    from sys import argv
    
    # Valeur par défaut
    config = 1
    
    # Recherche de config=X dans tous les arguments
    for arg in argv[1:]:
        if arg.startswith("config="):
            try:
                value = int(arg.split("=")[1])
                if 1 <= value <= 4:
                    config = value
            except ValueError:
                pass
    
    if len(argv) == 1 or argv[1] == "help":
        print(f"""=== open-taranis {T.__version__} ===

    help   : Show this...

    open   : Open the TUI

    update : upgrade the framework

Options:
    config=X : Use configuration X (1-4)
""")

    elif argv[1] == "open":
        curses.wrapper(run, config)

    elif argv[1] == "update":
        print("Updating open-taranis via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "open-taranis"])
            print("Update successful.")
        except subprocess.CalledProcessError as e:
            print(f"Error during update: {e}")
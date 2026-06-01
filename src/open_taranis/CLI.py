import open_taranis as T

import subprocess
import sys
import os

# ==============================
# The args
# ==============================

def main():
    from sys import argv
    
    if len(argv) == 1 or argv[1] == "help":
        print(f"""=== open-taranis {T.__version__} ===
░        ░░░      ░░░       ░░░░      ░░░   ░░░  ░░        ░░░      ░░
▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒    ▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒
▓▓▓▓  ▓▓▓▓▓        ▓▓       ▓▓▓        ▓▓  ▓  ▓  ▓▓▓▓▓  ▓▓▓▓▓▓      ▓▓
████  █████  ████  ██  ███  ███  ████  ██  ██    █████  ███████████  █
████  █████  ████  ██  ████  ██  ████  ██  ███   ██        ███      ██

    help    : Show this...

    update  : upgrade the framework
              
    clients : List the clients (API keys in the env)
""")
    
    elif argv[1] == "clients" and len(argv) == 2:
        print("\n\nRegistered API keys :")
        print(("- [x]" if os.environ.get('OPENROUTER_API_KEY') else "- [ ]")," openrouter")
        print(("- [x]" if os.environ.get('HUGGINGFACE_API_KEY') else "- [ ]")," huggingface")
        print(("- [x]" if os.environ.get('VENICE_API_KEY') else "- [ ]")," venice.ai")
        print(("- [x]" if os.environ.get('DEEPSEEK_API_KEY') else "- [ ]")," deepseek.ai")
        print(("- [x]" if os.environ.get('XAI_API_KEY') else "- [ ]")," x.ai")
        print(("- [x]" if os.environ.get('MISTRALAI_API_KEY') else "- [ ]")," mistral.ai")
        print(("- [x]" if os.environ.get('GROQ_API_KEY') else "- [ ]")," groq")
        print()
        print("=== Codes ==="),
        print(("- [x]" if os.environ.get('KIMI_CODE_API_KEY') else "- [ ]")," Kimi Code")
        print()
        print('To show the env var : "taranis clients names"\n')

    elif argv[1] == "clients" and argv[2] == "names":
        print("\n\nEnvironment variable names for API keys")
        print("- openrouter  = 'OPENROUTER_API_KEY'")
        print("- huggingface = 'HUGGINGFACE_API_KEY'")
        print("- venice.ai   = 'VENICE_API_KEY'")
        print("- deepseek.ai = 'DEEPSEEK_API_KEY'")
        print("- x.ai        = 'XAI_API_KEY'")
        print("- mistral.ai  = 'MISTRALAI_API_KEY'")
        print("- groq        = 'GROQ_API_KEY'")
        print()
        print("=== Codes ===",)
        print("- Kimi Code   = 'KIMI_CODE_API_KEY'")
        print()

    elif argv[1] == "update":
        print("Updating open-taranis via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "open-taranis"])
            print("Update successful.")
        except subprocess.CalledProcessError as e:
            print(f"Error during update: {e}")
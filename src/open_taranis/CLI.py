import open_taranis as T

import subprocess
import sys
import os
import curses

argv = sys.argv

# ==============================
# The TUI
# ==============================

LOGO_ASCII = """
░        ░░░      ░░░       ░░░░      ░░░   ░░░  ░░        ░░░      ░░
▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒    ▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒
▓▓▓▓  ▓▓▓▓▓        ▓▓       ▓▓▓        ▓▓  ▓  ▓  ▓▓▓▓▓  ▓▓▓▓▓▓      ▓▓
████  █████  ████  ██  ███  ███  ████  ██  ██    █████  ███████████  █
████  █████  ████  ██  ████  ██  ████  ██  ███   ██        ███      ██"""


MIN_HEIGHT = 24
MIN_WIDTH = 80

def run(stdscr):
    curses.curs_set(1)
    curses.start_color()
    curses.use_default_colors()
    
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    
    input_buffer = ""
    display_mode = "NONE"
    text = []
    
    while True:
        height, width = stdscr.getmaxyx()
        
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
        
        content_start = logo_height + 1
        content_end = height - 3
        
        if display_mode == "HELP":
            text = [
                "Commands :",
                "- /exit     = quit the TUI",
                "- /help     = show the command list",
                "- /show api = show registered API"
            ]
                    
        elif display_mode == "API":
            text = [
                "APIs registered :",
                ("- [x]" if os.environ.get('OPENROUTER_API') else "- [ ]") + " openrouter",
                ("- [x]" if os.environ.get('HF_API') else "- [ ]") + " huggingface",
                ("- [x]" if os.environ.get('VENICEAI_API') else "- [ ]") + " venice.ai",
                ("- [x]" if os.environ.get('DEEPSEEK_API') else "- [ ]") + " deepseek.ai",
                ("- [x]" if os.environ.get('XAI_API') else "- [ ]") + " x.ai",
                ("- [x]" if os.environ.get('GROQ_API') else "- [ ]") + " groq",
                "",
                "To show the env var : /show more"
            ]
        
        elif display_mode == 'MORE_API':
            text = [
                "APIs and env_var",
                "- openrouter  = 'OPENROUTER_API'",
                "- huggingface = 'HF_API'",
                "- venice.ai   = 'VENICEAI_API'",
                "- deepseek.ai = 'DEEPSEEK_API'",
                "- x.ai        = 'XAI_API'",
                "- groq        = 'GROQ_API'",
            ]
        
        if display_mode != "NONE" :
            current_line = content_start
            for line in text:
                if current_line < content_end:
                    try:
                        stdscr.addstr(current_line, 0, line, curses.color_pair(2))
                    except:
                        pass
                    current_line += 1
        
        sep_y = height - 2
        input_y = height - 1
        
        separator = "-" * min(width-1, 60)
        try:
            stdscr.addstr(sep_y, 0, separator, curses.color_pair(2) | curses.A_DIM)
        except:
            pass
        
        prompt = f"> {input_buffer}"
        display_prompt = prompt[:width-1]
        try:
            stdscr.addstr(input_y, 0, display_prompt, curses.color_pair(2))
            cursor_x = min(len(prompt), width - 1)
            stdscr.move(input_y, cursor_x)
        except:
            pass
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            continue
            
        elif key in (10, 13):
            command = input_buffer.strip()
            
            if command == "/exit":
                break
            
            elif command == "/help":
                display_mode = "HELP"
            
            elif command == "/show api":
                display_mode = "API"
            
            elif command == "/show more" and display_mode == "API" :
                display_mode = 'MORE_API'
            
            else:
                display_mode = None
            
            input_buffer = ""
            
        elif key in (127, curses.KEY_BACKSPACE, ord('\b')):
            input_buffer = input_buffer[:-1]
            
        elif key == 27:
            input_buffer = ""
            
        elif 32 <= key <= 126:
            input_buffer += chr(key)

# ==============================
# The args
# ==============================

def main():
    if len(argv) == 1 or argv[1] == "help" :
        print(f"""=== open-taranis {T.__version__} ===

    help   : Show this...

    open   : Open the TUI

    update : upgrade the framework
""")

    elif argv[1] == "open":
        curses.wrapper(run)

    elif argv[1] == "update":
        print("Updating open-taranis via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "open-taranis"])
            print("Update successful.")
        except subprocess.CalledProcessError as e:
            print(f"Error during update: {e}")
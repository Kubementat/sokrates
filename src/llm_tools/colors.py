# ANSI Color codes for beautiful console output
"""
A class for managing color definitions.
"""
class Colors:
    # Regular colors
    BLACK: str = '\033[30m'
    RED: str = '\033[91m'
    GREEN: str = '\033[92m'
    YELLOW: str = '\033[93m'
    BLUE: str = '\033[94m'
    MAGENTA: str = '\033[95m'
    CYAN: str = '\033[96m'
    WHITE: str = '\033[37m'

    # Bright colors
    BRIGHT_BLACK: str = '\033[90m'
    BRIGHT_RED: str = '\033[91m'
    BRIGHT_GREEN: str = '\033[92m'
    BRIGHT_YELLOW: str = '\033[93m'
    BRIGHT_BLUE: str = '\033[94m'
    BRIGHT_MAGENTA: str = '\033[95m'
    BRIGHT_CYAN: str = '\033[96m'
    BRIGHT_WHITE: str = '\033[97m'

    # Styles
    BOLD: str = '\033[1m'
    DIM: str = '\033[2m'
    ITALIC: str = '\033[3m'
    UNDERLINE: str = '\033[4m'
    BLINK: str = '\033[5m'
    REVERSE: str = '\033[7m'
    STRIKETHROUGH: str = '\033[9m'

    # Reset
    RESET: str = '\033[0m'

    # Background colors
    BG_BLACK: str = '\033[40m'
    BG_RED: str = '\033[41m'
    BG_GREEN: str = '\033[42m'
    BG_YELLOW: str = '\033[43m'
    BG_BLUE: str = '\033[44m'
    BG_MAGENTA: str = '\033[45m'
    BG_CYAN: str = '\033[46m'
    BG_WHITE: str = '\033[47m'

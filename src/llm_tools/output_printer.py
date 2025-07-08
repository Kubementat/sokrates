from .colors import Colors

class OutputPrinter:
  
  @staticmethod
  def print_header(title, color=Colors.BRIGHT_CYAN, width=60):
    """Print a beautiful header with decorative borders"""
    border = "═" * width
    print(f"\n{color}{Colors.BOLD}╔{border}╗{Colors.RESET}")
    print(f"{color}{Colors.BOLD}║{title.center(width)}║{Colors.RESET}")
    print(f"{color}{Colors.BOLD}╚{border}╝{Colors.RESET}\n")

  @staticmethod
  def print_section(title, color=Colors.BRIGHT_BLUE, char="─"):
      """Print a section separator"""
      print(f"\n{color}{Colors.BOLD}{char * 50}{Colors.RESET}")
      print(f"{color}{Colors.BOLD} {title}{Colors.RESET}")
      print(f"{color}{Colors.BOLD}{char * 50}{Colors.RESET}")

  @staticmethod
  def print_info(label, value, label_color=Colors.BRIGHT_GREEN, value_color=Colors.WHITE):
      """Print formatted info with colored labels"""
      print(f"{label_color}{Colors.BOLD}{label}:{Colors.RESET} {value_color}{value}{Colors.RESET}")

  @staticmethod
  def print_success(message):
      """Print success message"""
      print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}✓ {message}{Colors.RESET}")

  @staticmethod
  def print_warning(message):
      """Print warning message"""
      print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}⚠ {message}{Colors.RESET}")

  @staticmethod
  def print_error(message):
      """Print error message"""
      print(f"{Colors.BRIGHT_RED}{Colors.BOLD}✗ {message}{Colors.RESET}")

  @staticmethod
  def print_progress(message):
      """Print progress message"""
      print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}⟳ {message}{Colors.RESET}")

  @staticmethod
  def print_file_created(filename):
      """Print file creation message"""
      print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}📄 Created: {Colors.RESET}{Colors.CYAN}{filename}{Colors.RESET}")
from sokrates import FileHelper
from sokrates import OutputPrinter
from sokrates import Colors
from sokrates.config import Config

class Helper:
  
    @staticmethod
    def construct_context_from_arguments(context_text: str = None, context_directories: str = None, context_files: str = None):
        context = []
        if context_text:
            context.append(context_text)
            OutputPrinter.print_info("Appending context text to prompt:", context_text , Colors.BRIGHT_MAGENTA)
        if context_directories:
            directories = [s.strip() for s in context_directories.split(",")]
            context.extend(FileHelper.read_multiple_files_from_directories(directories))
            OutputPrinter.print_info("Appending context directories to prompt:", context_directories , Colors.BRIGHT_MAGENTA)
        if context_files:
            files = [s.strip() for s in context_files.split(",")]
            context.extend(FileHelper.read_multiple_files(files))
            OutputPrinter.print_info("Appending context files to prompt:", context_files , Colors.BRIGHT_MAGENTA)
        return context

    @staticmethod
    def print_configuration_section(config: Config, args=None):
        api_endpoint_config_source = f"Configuration File: {config.config_path}"
        api_endpoint = config.api_endpoint
        
        api_endpoint_config_source = "CLI Parameter: --api-endpoint"
        
        if args and args.api_endpoint:
            api_endpoint = args.api_endpoint
            api_endpoint_config_source = "CLI Parameter: --api-endpoint"

        OutputPrinter.print_section("Sokrates Configuration")
        OutputPrinter.print_info("home directory", config.home_path)
        OutputPrinter.print_info("configuration file", api_endpoint_config_source)
        OutputPrinter.print_info("LLM API Endpoint", str(api_endpoint))
        OutputPrinter.print_info("config_path", config.config_path)
        print("")
        OutputPrinter.print_info("default_model", str(config.default_model))
        OutputPrinter.print_info("default_model_temperature", str(config.default_model_temperature))
        print("")
        OutputPrinter.print_info("database_path", config.database_path)
        OutputPrinter.print_info("daemon_logfile_path", config.daemon_logfile_path)
        OutputPrinter.print_info("daemon_processing_interval", str(config.daemon_processing_interval))
        OutputPrinter.print_info("file_watcher_enabled", str(config.file_watcher_enabled))
        OutputPrinter.print_info("file_watcher_directories", str(config.file_watcher_directories))
        OutputPrinter.print_info("file_watcher_extensions", str(config.file_watcher_extensions))
        print("──────────────────────────────────────────────────")
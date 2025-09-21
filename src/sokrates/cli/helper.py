from typing import Any
from sokrates import FileHelper
from sokrates import OutputPrinter
from sokrates import Colors
from sokrates.config import Config

class Helper:

    @staticmethod
    def load_config() -> Config:
        config = Config()
        config.load_from_file(
            config_filepath=config.get('config_path')
        )
        return config
    
    @staticmethod
    def get_provider_value(key, config: Config, args, key_in_provider_config=None):
        if key_in_provider_config == None:
            key_in_provider_config = key

        if getattr(args, key):
            return getattr(args, key)
        
        # if a provider is specified -> load the config from that provider configuration
        if args.provider:
            provider = config.get_provider(args.provider)
            if not provider:
                raise ValueError(f"Could not find configuration for provider: {args.provider}")
            return provider.get(key_in_provider_config)
        
        # if nothing is specified in the args -> return default provider config
        provider = config.get_default_provider()
        return provider.get(key_in_provider_config)
  
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
        OutputPrinter.print_section("Sokrates Configuration")
        OutputPrinter.print_info("home directory", config.get('home_path'))
        OutputPrinter.print_info("config_path", config.get('config_path'))
        OutputPrinter.print_info("database_path", config.get('database_path'))
        OutputPrinter.print_info("daemon.logfile_path", config.get('daemon.logfile_path'))
        OutputPrinter.print_info("daemon.processing_interval", config.get('daemon.processing_interval'))
        OutputPrinter.print_info("daemon.file_watcher.enabled", config.get('daemon.file_watcher.enabled'))
        OutputPrinter.print_info("daemon.file_watcher.watched_directories", config.get('daemon.file_watcher.watched_directories'))
        OutputPrinter.print_info("daemon.file_watcher.file_extensions", config.get('daemon.file_watcher.file_extensions'))
        print("")
        default_provider = config.get_default_provider()
        if default_provider:
            OutputPrinter.print_info("default_provider", default_provider.get("name"))
            OutputPrinter.print_info("default_provider_endpoint", default_provider.get("api_endpoint"))
            OutputPrinter.print_info("default_provider_model", default_provider.get("default_model"))
            OutputPrinter.print_info("default_provider_model_temperature", default_provider.get("default_temperature"))
        else:
            OutputPrinter.print(f"No default provider configured. Consider checking your configuration file in {config.get('config_path')}", Colors.RED)
        print("")
        print("──────────────────────────────────────────────────")
        OutputPrinter.print_section("Execution Configuration")
        if args and args.provider:
            OutputPrinter.print_info("provider", args.provider)
        OutputPrinter.print_info("api_endpoint", Helper.get_provider_value('api_endpoint',config, args))
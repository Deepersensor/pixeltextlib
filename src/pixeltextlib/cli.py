import argparse
import logging
import sys
from pixeltextlib import __version__
from pixeltextlib.config import load_config, set_config_value, save_config, DEFAULT_CONFIG
from pixeltextlib.core import PixelTextCore
from pixeltextlib.watcher import DirectoryWatcher

_logger = logging.getLogger(__name__)

def main(args=None):
    """
    Main function for the pixeltextlib CLI.
    """
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="PixelText: Index and search text in images.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"pixeltextlib {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure PixelText settings")
    # config_parser.add_argument("key", help="Configuration key to set")
    # config_parser.add_argument("value", help="Value to set for the configuration key")

    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Start watching directories for changes")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for text in indexed images")
    search_parser.add_argument("query", help="Text to search for")

    # Add directory command
    add_dir_parser = subparsers.add_parser("add_directory", help="Add a directory to watch")
    add_dir_parser.add_argument("directory", help="Directory to add to watch list")

    # Remove directory command
    remove_dir_parser = subparsers.add_parser("remove_directory", help="Remove a directory from watch list")
    remove_dir_parser.add_argument("directory", help="Directory to remove from watch list")

    args = parser.parse_args(args)

    config = load_config()
    log_level = config.get('log_level', 'INFO').upper()
    logging.basicConfig(level=log_level, format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s")

    core = PixelTextCore(config)

    if args.command == "config":
        config = load_config()
        # Ensure all default config entries are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        save_config(config)
        print("Configuration initialized/updated.")
    elif args.command == "watch":
        watcher = DirectoryWatcher(core, config)
        watcher.run()
    elif args.command == "search":
        results = core.search_index(args.query)
        if results:
            print("Results:")
            for result in results:
                print(result)
        else:
            print("No results found.")
    elif args.command == "add_directory":
        directory_to_add = args.directory
        watch_directories = config.get("watch_directories", [])
        if directory_to_add not in watch_directories:
            watch_directories.append(directory_to_add)
            set_config_value("watch_directories", watch_directories)
            print(f"Added directory {directory_to_add} to watch list.")
        else:
            print(f"Directory {directory_to_add} is already in the watch list.")
    elif args.command == "remove_directory":
        directory_to_remove = args.directory
        watch_directories = config.get("watch_directories", [])
        if directory_to_remove in watch_directories:
            watch_directories.remove(directory_to_remove)
            set_config_value("watch_directories", watch_directories)
            print(f"Removed directory {directory_to_remove} from watch list.")
        else:
            print(f"Directory {directory_to_remove} is not in the watch list.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

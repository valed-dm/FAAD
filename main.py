import os
from pathlib import Path


def get_data_path_from_user() -> Path:
    """
    Prompts the user to enter the path to their data folder and validates it.
    This is Windows-friendly and handles path normalization.
    """
    while True:
        # Prompt the user for input
        raw_path = input(
            "--> Please enter the full path to your data folder"
            " (e.g., C:\\Users\\YourName\\Desktop\\FreenetData): "
        )

        # Use pathlib.Path to handle any kind of slash ( \ or / )
        user_path = Path(raw_path)

        # Validate that the path exists and is a directory
        if user_path.exists() and user_path.is_dir():
            print(f"✔️  Data folder found: {user_path}\n")
            return user_path
        else:
            print(
                f"❌ ERROR: The path '{user_path}' does not exist or is not a folder."
                f" Please try again.\n"
            )


def main():
    """Main function to run the application."""
    print("--- Freenet Alias Adder ---")

    # Step 1: Get the data path from the user.
    data_path = get_data_path_from_user()

    # Step 2: Set an environment variable with the path.
    os.environ["DATA_DIR_INPUT"] = str(data_path)

    # Step 3: We import the modules that depend on the configuration.
    # This delayed import is crucial.
    from alias_adder.manager import FreenetAliasManager
    from core.config import settings

    # Step 4: Ensure other necessary directories and files exist.
    # The data files are the user's responsibility.
    settings.OUTPUT_DIR.mkdir(exist_ok=True)
    settings.LOGS_DIR.mkdir(exist_ok=True)
    if not settings.OUTPUT_FILE.exists():
        settings.OUTPUT_FILE.touch()
    if not settings.CRITICAL_ERRORS_FILE.exists():
        settings.CRITICAL_ERRORS_FILE.touch()

    # Step 5: Run the application.
    manager = FreenetAliasManager()
    manager.run()


if __name__ == "__main__":
    main()

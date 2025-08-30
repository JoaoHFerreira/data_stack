from src.ingestion.kaggle import KaggleDatasetDownloader
from src.cleanup.dataset import DatasetCleaner


def show_menu():
    print("\n=== Data Stack Menu ===")
    print("1. Pull Kaggle Dataset")
    print("2. Manage Datasets")
    print("0. Exit")
    return input("\nSelect option: ")


def handle_kaggle_pull():
    dataset_name = input("Enter dataset name (e.g., titanic): ")
    downloader = KaggleDatasetDownloader()
    downloader.run(dataset_name)


def show_cleanup_menu():
    print("\n=== Dataset Management ===")
    print("1. List Datasets")
    print("2. Delete Specific Dataset")
    print("3. Delete All Datasets")
    print("0. Back to Main Menu")
    return input("\nSelect option: ")


def handle_dataset_management():
    while True:
        choice = show_cleanup_menu()
        cleaner = DatasetCleaner()
        
        match choice:
            case "1":
                cleaner.run("list")
            case "2":
                dataset_name = input("Enter dataset name to delete: ")
                cleaner.run("delete_specific", dataset_name)
            case "3":
                cleaner.run("delete_all")
            case "0":
                break
            case _:
                print("Invalid option!")

def main():
    while True:
        choice = show_menu()
        
        match choice:
            case "1":
                handle_kaggle_pull()
            case "2":
                handle_dataset_management()
            case "0":
                print("Goodbye!")
                break
            case _:
                print("Invalid option!")


if __name__ == "__main__":
    main()

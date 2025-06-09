# VS Code Extension Downloader [English | 中文](README_zh.md)

This script downloads VS Code extensions listed in `extensions.txt`.

## Prerequisites

- Python 3
- Pip (Python package installer)

## Setup

1.  **Clone the repository or download the files.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Populate `extensions.txt`:**
    Add the VS Code extension IDs you want to download, one per line. For example:
    ```
    ms-python.python
    ritwickdey.liveserver
    ```
    You can find the extension ID on the VS Code Marketplace. It's usually in the format `publisher.extensionName`.

## Usage

Run the script from the project's root directory:

```bash
python download_vsix.py
```

## Output

-   **`.vsix` files:** The downloaded extension files will be saved in the `vsix_files/` directory.
-   **Log file:** A log of the download process will be created at `download_vsix.log`.

## How it Works

The script reads each extension ID from `extensions.txt`, constructs the download URL for the VS Code Marketplace, downloads the `.vsix` file, and saves it to the `vsix_files/` directory. It logs its progress and any errors to `download_vsix.log`.

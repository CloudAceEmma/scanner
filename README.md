# Git Secret Scanner

An LLM-powered tool that scans the last N commits of a Git repository for secrets and other sensitive data.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CloudAceEmma/scanner.git
    cd scanner
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Set your Gemini API Key:**
    ```bash
    export GEMINI_API_KEY='your-api-key'
    ```

## Usage

Run the scanner with the following command:

```bash
scanner --repo <path|url> --n <commits> --out report.json
```

### Example

Scan the last 20 commits of a local repository:
```bash
scanner --repo /path/to/my/project --n 20 --out detailed_report.json
```

Scan a remote repository:
```bash
scanner --repo https://github.com/someuser/somerepo.git --n 50
```
*(The default output file is `report.json`)*

# Contributing to VCut2DAW

First off, thank you for considering contributing to VCut2DAW! This tool is built to solve a very specific pain point in Post-Production, and community help makes it better for everyone.

## How to Contribute

### 1. Reporting Bugs
Please use the GitHub Issue Tracker to report bugs. When reporting, make sure to include:
* Your OS version (Windows 10/11, macOS Sonoma, etc.)
* Your DAW version (Pro Tools, Nuendo, Reaper, etc.).
* The exact error message or crash behavior.
* A small sample video or CSV if it helps reproduce the bug.

### 2. Suggesting Features
If you have an idea for a new feature (like supporting a different NLE XML format), please open an issue first to discuss it before you start writing code. 

### 3. Submitting Pull Requests
1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature/my-cool-feature`
3. Make your changes and test them locally.
4. Commit your changes: `git commit -m "Add cool feature"`
5. Push to the branch: `git push origin feature/my-cool-feature`
6. Open a Pull Request.

## Local Development Setup

We use Python 3.9+.

1. Clone the repo:
   ```bash
   git clone https://github.com/rhinofug/VCut2DAW.git
   cd VCut2DAW
   ```
2. Run the setup script to create a virtual environment and install dependencies:
   * **Windows:** `setup_and_run.bat`
   * **macOS:** `sh setup_and_run.sh`

3. Run the application from source:
   ```bash
   # Make sure your virtual environment is active!
   python app.py
   ```

## Code Guidelines
- Keep it simple. This is a lightweight script, not a massive framework.
- Avoid introducing huge external dependencies unless absolutely necessary (we try to keep the frozen `.exe` size under control).
- Use `logging` or print to the GUI console rather than strict CLI-only printing.

Thanks!
F.Utku Gercik

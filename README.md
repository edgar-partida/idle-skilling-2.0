# Idle Skilling Clicker 2.0

Automated macro tool for interacting with an Idle Skilling game window on Windows.

This app lets you capture clickable areas of the game, save named actions, and build both sequential and parallel routines for automatic execution.

## Features

- Capture screen coordinates using `Shift + left click` inside the game window
- Save named actions to `resources/relative-coords.json`
- Create sequential routines with delays
- Create parallel routines that repeat actions at configurable intervals
- Execute saved routines against the target game window
- Safely stop execution using `Esc`

## Requirements

- Python 3.8+ on Windows
- `pygetwindow`
- `pywin32`
- `keyboard`
- `pynput`
- `tkinter` (built into most Python Windows installs)

## Installation

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Install the required packages:

```powershell
pip install pygetwindow pywin32 keyboard pynput
```

## Usage

1. Run the application:

```powershell
python IdleSkillingApp.py
```

2. The app will search for a window with the title `Idle Skilling` by default.
3. Use the menu options:

- `1` – Capture new coordinates using `Shift + left click` on the game window
- `2` – Create a new routine interactively
- `3` – Execute a saved sequential routine
- `4` – Execute a saved parallel routine
- `0` – Exit the app

4. While capturing coordinates:

- Hold `Shift`
- Click the desired point in the game window
- Enter a name for the action in the popup dialog
- Press `Enter` in the terminal to stop capture mode

5. While executing routines:

- Press `Esc` to stop execution safely

## Files and folders

- `IdleSkillingApp.py` – main application entry point
- `utils/coordinate_utils.py` – coordinate capture logic
- `utils/routine_utils.py` – routine creation and execution logic
- `utils/menu_utils.py` – console menu helper functions
- `utils/screen_finder.py` – window focus and bring-to-front logic
- `resources/relative-coords.json` – saved named coordinate actions
- `resources/routines-sequential.json` – saved sequential routines
- `resources/routines-parallel.json` – saved parallel routines

## Customization

- Change the default target window title by passing a different `titulo_objetivo` to `IdleSkillingApp()` in `IdleSkillingApp.py`.
- Coordinates are stored as normalized percentages, so actions adapt to window size.

## Notes

- This tool is designed for Windows and uses native Windows APIs for background clicks and window focus.
- The game window title must match exactly when searching for the target window.

## License

Use this project for personal automation and testing. Modify as needed for your own game macros.

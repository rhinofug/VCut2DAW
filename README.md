# VCut2ProTools (Open Source Conform Assistant)

VCut2ProTools is an open-source video-to-DAW pipeline tool designed specifically for Sound Editors and Assistant Editors. It automatically detects visual cuts from a video (or parses CMX3600 EDLs) and generates **100% compliant Dummy AAFs and MIDI Markers** perfectly synced for Pro Tools.

## Why This Exists? (The Technical Edge)
- **Pro Tools AAF Strictness:** Pro Tools 12.5+ aggressively rejects standard OTIO AAFs. VCut2ProTools uses `pyaaf2` to build compliant `SourceMob` and `MasterMob` hierarchies with valid `PCMDescriptor`s so Pro Tools never throws an import error.
- **The "1-Frame Drift" Fix:** AI cut detection often places the cut on the first *new* frame, resulting in a 1-frame offset compared to traditional NLE edits. This tool automatically mathematically shifts all cuts 1 frame left and fills the timeline gap to ensure perfect frame sync with the picture department.
- **The "120 BPM" MIDI Sync Issue:** Pro Tools forces its session tempo (default 120 BPM) onto imported MIDI markers unless you overwrite the tempo map. This tool mathematically hardcodes the MIDI tick scale to assume 120 BPM (`ticks_per_beat = 12000`), ensuring 01:00:00:00 lands exactly at 1 hour, not 30 minutes!

## Features
- **Video to Cuts:** Drag and drop an MP4/MOV and get a frame-accurate CSV.
- **EDL Support:** Got an EDL from the editor? Drop the `.edl` file directly into Step 2!
- **Dummy AAF Generation:** Generates a Clip Track allowing you to use `Tab to Transient` to jump between scenes.
- **Session Start Timecode Offset:** Input your session start (e.g., `01:00:00:00`) and the files will spot perfectly without manual offset mapping.

## Installation

### For Windows
Double click the `setup_and_run.bat` file. It will automatically create a virtual environment, install dependencies, and launch the app.

### For macOS / Linux
Open your terminal, navigate to the folder, and run:
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

## License
This project is licensed under the **Creative Commons Attribution-NonCommercial (CC BY-NC 4.0)** license.
You are free to use, share, and modify this code for your personal or studio workflows, but **you may not use this software for commercial monetization or sell it as a paid product/service**. 

## Author
**F.Utku Gerçik**  
Email: utkugercik@gmail.com  
GitHub: [github.com/rhinofug/VCut2ProTools](https://github.com/rhinofug/VCut2ProTools) 

*Protected with Watermark technology.*

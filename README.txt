# VCut2DAW (Open Source Conform Assistant)

VCut2DAW is an open-source video-to-DAW pipeline tool designed specifically for Sound Editors and Assistant Editors. 
It automatically detects visual cuts from a video (or parses CMX3600 EDLs) and generates 100% compliant Dummy AAFs 
and MIDI Markers perfectly synced for DAWs (Pro Tools, Nuendo, Reaper, Logic, etc.).

Support the project: https://buymeacoffee.com/rhinofug

-------------------------------------------------------------------------------------------------

## Why This Exists? (The Technical Edge)

1. DAW AAF Strictness: Pro Tools 12.5+ aggressively rejects standard OTIO AAFs. VCut2DAW uses pyaaf2 
   to build compliant hierarchies so DAWs never throw an import error.
2. The '1-Frame Drift' Fix: AI cut detection often places the cut on the first new frame, resulting 
   in a 1-frame offset compared to traditional NLE edits. This tool automatically shifts all cuts 1 frame left.
3. The '120 BPM' MIDI Sync Issue: DAWs tie MIDI marker timecodes to the session tempo map. This tool mathematically 
   hardcodes the MIDI tick scale to assume 120 BPM ensuring timecodes land exactly correctly.

-------------------------------------------------------------------------------------------------

## Features

- Video to Cuts: Drag and drop an MP4/MOV and get a frame-accurate CSV.
- EDL Support: Drop a standard .edl file directly into Step 2!
- Dummy AAF Generation: Generates a Clip Track allowing you to use 'Tab to Transient' to jump between scenes.
- Session Start Timecode Offset: Input your session start (e.g., 01:00:00:00) and the files will spot perfectly.

-------------------------------------------------------------------------------------------------

## Installation & Usage

For Windows:
Double click the compile_windows.bat file. It will automatically download dependencies, compile the source code 
into a standalone .exe, and place it in the 'builds/' folder for you to run!

For macOS / Linux:
Open your terminal, navigate to the folder, and run:
chmod +x compile_mac.sh
./compile_mac.sh

-------------------------------------------------------------------------------------------------

## Important Pro Tools / DAW Tips (FAQ)

1. "My MIDI markers don't line up with the video!" (The 120 BPM Rule)
Your DAW session tempo MUST be set to exactly 120 BPM when you import the MIDI file. 
If your session is set to 120 BPM, the markers will be 100% frame-accurate.

2. Session Start Timecode Mismatch
The 'Session Start Timecode' you type into the VCut2DAW app (e.g. 01:00:00:00) must exactly match 
your DAW's Session Start Time.

3. The AAF Audio is Offline / Empty?
This is intentional. The tool generates a 'Dummy' AAF track. It has no real audio. Its sole purpose is 
to create empty clips on your timeline so you can use the 'Tab to Transient' shortcut to jump to cuts.

-------------------------------------------------------------------------------------------------

## Author & License

Developed by F.Utku Gercik
Email: utkugercik@gmail.com
GitHub: github.com/rhinofug/VCut2DAW

This project is licensed under the Creative Commons Attribution-NonCommercial (CC BY-NC 4.0) license.
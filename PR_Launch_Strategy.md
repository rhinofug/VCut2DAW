# VCut2DAW - Ultimate Launch & PR Strategy

## 1. LAUNCH TEXT (COPY & PASTE)
*(Use this text for Forums, Reddit, and Facebook groups. For LinkedIn, add a personal touch at the beginning.)*

**Title:**
[Free / Open-Source] VCut2DAW - Auto Scene Detect to AAF & MIDI Markers for Pro Tools/Nuendo

**Body:**

Hey everyone,

As an audio post professional, I got tired of manually spotting scene cuts and dealing with broken EDLs or non-compliant AAFs that DAWs (especially Pro Tools) constantly refuse to import. 

So, I built **VCut2DAW**, a completely free and open-source pipeline tool designed specifically for Sound Editors and Assistants. It analyzes your video (or parses an EDL) and generates 100% compliant DAW markers (AAF and MIDI).

**Why did I build this? (Free Alternative to Commercial Tools):**
While there are great commercial tools out there like HAL Audio's *Cut-It* (39€) or *EdiLoad* (+) that do similar things, I believe fundamental workflow utilities should be accessible to independent sound editors and assistants. So, I built a free, completely open-source alternative.

**The Technical Edge:**
* **Pro Tools AAF Strictness:** Most standard open-source AAFs fail to import in modern Pro Tools. VCut2DAW builds strictly compliant *SourceMob/MasterMob* hierarchies with valid *PCMDescriptors*. No more "Could not parse" errors.
* **The "1-Frame Drift" Fix:** Standard AI cut detectors place the marker on the first *new* frame, causing a 1-frame offset compared to traditional NLE edits. This tool mathematically shifts all cuts 1 frame left, ensuring perfect frame-sync with the picture department.
* **The "120 BPM" MIDI Sync Issue:** Importing standard MIDI markers often forces your DAW session to 120 BPM or scales incorrectly. VCut2DAW hardcodes the MIDI tick scale (	icks_per_beat = 12000), so a 01:00:00:00 timecode lands exactly at 1 hour, without messing up your tempo map.

**How it works:**
1. **Select** your Video (MP4/MOV) via the Browse button for auto-detection, OR **load** a CMX3600 .edl from the picture editor.
2. Enter your Session Start Timecode.
3. Hit generate. It spits out a perfectly synced MIDI file and an AAF Clip Track.
4. **Open your DAW** and import the MIDI or dummy AAF files directly into your timeline!

It's completely free, open-source, and available for both **Windows and macOS**.

You can grab the .exe or Mac app from the Releases page and check out the source code here:
🔗 **Download & Source:** https://github.com/rhinofug/VCut2DAW/releases/latest

*(Note for Mac users: Since this is an unsigned open-source app, macOS Gatekeeper might block it. Just drag it to your Applications folder and run xattr -cr /Applications/VCut2DAW.app in the terminal to clear the quarantine flag, or right-click -> Open!)*
🔗 **My Portfolio / Upcoming Projects:** https://rhinofug.github.io

I’d love to hear your feedback, bug reports, or feature requests. I built this to help our community speed up the conform process. Hope it saves you some hours!

Cheers,
F. Utku Gercik

---

## 2. REDDIT COMMUNITIES (High Priority)
*   **r/AudioPost** -> Main target! Audio post professionals.
*   **r/protools** -> The crowd suffering most from AAF issues.
*   **r/Reaper** -> They love independent workflow tools.
*   **r/editors** -> Video editors preparing deliverables for sound.
*   **r/sounddesign** -> Creative folks who still need scene markers.

## 3. TRADITIONAL AUDIO FORUMS (Veterans & Studios)
*   **Gearspace (Post Production Forum)** -> Post it as a "New Product Alert" or in the Post Production section.
*   **Avid Pro Audio Community (DUC)** -> The official Avid forums.
*   **VI-Control (Sound Design & Post Production)** -> Huge for film composers scoring to picture.
*   **Steinberg Forums (Nuendo)** -> Dedicated Nuendo users.
*   **KVR Audio (Hosts & Applications)** -> Good for general audio tech.

## 4. FACEBOOK GROUPS (Fast Social Spread)
*   **Post Production Audio** (30k+ members)
*   **Pro Tools Users Group**
*   **Audio Post Production Professionals**
*   **Sound Design**

## 5. LINKEDIN GROUPS (B2B & Networking)
*   **Audio Post Production Professionals**
*   **Pro Tools Expert Group**
*   **Sound Designers**
*   **Film and Television Post Production**
*   **Audio Engineering Society (AES)**

## 6. NEWSLETTERS & BLOGS (Pitch via Email / Contact Form)
*   **Production Expert (formerly Pro Tools Expert)** -> The holy grail. Pitch them via their contact form.
*   **A Sound Effect** -> Huge newsletter for sound designers.
*   **Bedroom Producers Blog (BPB)** -> They run a very popular "Freeware" segment.
*   **Sonic Scoop** -> Tech reviews and news.
*   **KVR Audio News** -> You can submit news yourself via "Submit News".

## 7. DISCORD / DEVELOPER COMMUNITIES
*   **Sound Design Discord**
*   **REAPER Discord**
*   **Hacker News (YCombinator)** -> Pitch as Show HN: VCut2DAW – Open-source video cut detection to Pro Tools AAF.



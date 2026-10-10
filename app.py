__version__ = "1.0.0"
import os
import subprocess
import sys
import threading
import tkinter as tk
import customtkinter as ctk
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import csv
import mido
from mido import MetaMessage, MidiFile, MidiTrack

if getattr(sys, 'frozen', False):
    if sys.platform == 'darwin' and 'MacOS' in sys.executable:
        # For Mac .app bundles, go up 4 directories to get OUT of the .app entirely
        APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))))
    else:
        APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    
DEFAULT_OUT_DIR = os.path.join(APP_DIR, "VCut_Exports")

def log_message(msg):
    log_area.configure(state="normal")
    log_area.insert(tk.END, msg + "\n")
    log_area.see(tk.END)
    log_area.configure(state="disabled")

def select_video_file():
    filepath = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=(("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*"))
    )
    if filepath:
        video_entry.delete(0, tk.END)
        video_entry.insert(0, filepath)
        log_message(f"Selected video: {filepath}")

def select_csv_file():
    filepath = filedialog.askopenfilename(
        title="Select CSV/EDL File",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if filepath:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, filepath)
        log_message(f"Selected CSV/EDL: {filepath}")
        
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        if base_name.endswith("-Scenes"):
            base_name = base_name.replace("-Scenes", "")
        proj_name_entry.delete(0, tk.END)
        proj_name_entry.insert(0, base_name)

class RedirectStdout:
    def __init__(self, log_cb):
        self.log_cb = log_cb
    def write(self, text):
        if text.strip():
            self.log_cb(text.strip())
    def flush(self):
        pass

def run_step1_process(video_path, csv_out_dir, success_msg, expected_csv):
    global _auto_proceed_step2
    """
    Analyzes a video file to detect scene cuts and exports a CSV file.
    Uses PySceneDetect with adaptive content detection.
    
    Args:
        video_path (str): Absolute path to the input video file.
        csv_out_dir (str): Absolute directory path where the CSV should be saved.
        success_msg (str): Message to display upon success.
        expected_csv (str): The expected output path of the CSV file.
    """
    try:
        log_area.after(0, log_message, f"Running PySceneDetect in-process on: {video_path}")
        
        import sys
        from scenedetect.__main__ import main as scenedetect_main
        
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_argv = sys.argv
        
        sys.stdout = RedirectStdout(lambda m: log_area.after(0, log_message, m))
        sys.stderr = sys.stdout
        
        sys.argv = ["scenedetect", "-i", video_path, "-o", csv_out_dir, "detect-content", "list-scenes"]
        
        try:
            scenedetect_main()
            log_area.after(0, log_message, success_msg)
            if os.path.exists(expected_csv):
                csv_entry.after(0, lambda: csv_entry.delete(0, tk.END))
                csv_entry.after(0, lambda: csv_entry.insert(0, expected_csv))
            
            if _auto_proceed_step2:
                _auto_proceed_step2 = False
                log_area.after(100, lambda: log_message(">>> Auto-Proceeding to Step 2..."))
                btn_convert.after(500, start_convert)
            else:
                messagebox.showinfo("Success", success_msg)
        except SystemExit as e:
            if e.code == 0:
                log_area.after(0, log_message, success_msg)
                if os.path.exists(expected_csv):
                    csv_entry.after(0, lambda: csv_entry.delete(0, tk.END))
                    csv_entry.after(0, lambda: csv_entry.insert(0, expected_csv))
                
                
                if _auto_proceed_step2:
                    _auto_proceed_step2 = False
                    log_area.after(100, log_message, ">>> Auto-Proceeding to Step 2...")
                    btn_convert.after(500, start_convert)
                else:
                    messagebox.showinfo("Success", success_msg)
            else:
                log_area.after(0, log_message, f"PROCESS EXITED WITH CODE: {e.code}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.argv = old_argv

    except Exception as e:
        log_area.after(0, log_message, f"EXCEPTION: {str(e)}")
        messagebox.showerror("Error", str(e))
    finally:
        btn_detect.configure(state="normal")
        btn_convert.configure(state="normal")

def start_detect():
    video_path = video_entry.get()
    if not video_path or not os.path.exists(video_path):
        messagebox.showerror("Error", "Please select a valid video file.")
        return

    out_base = output_entry.get().strip()
    if not out_base:
        out_base = DEFAULT_OUT_DIR
    
    csv_out_dir = os.path.join(out_base, "CSV")
    os.makedirs(csv_out_dir, exist_ok=True)

    btn_detect.configure(state="disabled")
    btn_convert.configure(state="disabled")
    
    video_filename = os.path.basename(video_path)
    video_name_no_ext = os.path.splitext(video_filename)[0]
    expected_csv_name = f"{video_name_no_ext}-Scenes.csv"
    csv_full_path = os.path.join(csv_out_dir, expected_csv_name)

    threading.Thread(target=run_step1_process, args=(video_path, csv_out_dir, "Step 1 Complete: Scene list (CSV) generated successfully.", csv_full_path), daemon=True).start()

def parse_timecode_to_frames(tc_str, fps):
    try:
        parts = str(tc_str).replace(';', ':').split(':')
        if len(parts) == 4:
            h, m, s, f = map(int, parts)
            math_fps = int(round(fps))
            total_frames = (h * 3600 + m * 60 + s) * math_fps + f
            return total_frames
    except:
        pass
    return 0

def run_step2_process(csv_path, midi_path, aaf_path, tc_string, log_cb, done_cb):
    try:
        log_cb(f"Reading scenes from {os.path.basename(csv_path)}...")
        scenes = []
        fps = 25.0
        
        # Check if CSV or EDL
        is_edl = csv_path.lower().endswith('.edl')
        raw_scenes = []
        
        if is_edl:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                scene_count = 1
                for line in lines:
                    line = line.strip()
                    # A standard CMX3600 event line starts with a 3-digit number
                    if line[:3].isdigit() and len(line) > 20:
                        parts = line.split()
                        if len(parts) >= 4:
                            rec_in = parts[-2]
                            rec_out = parts[-1]
                            try:
                                in_frames = parse_timecode_to_frames(rec_in, fps)
                                out_frames = parse_timecode_to_frames(rec_out, fps)
                                length = out_frames - in_frames
                                raw_scenes.append([in_frames, length, f"VCut {scene_count}"])
                                scene_count += 1
                            except:
                                pass
        else:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row: continue
                    if not row[0].isdigit():
                        if 'Frame Rate:' in row[0]:
                            try:
                                fps_str = row[0].split('Frame Rate:')[1].strip().split(' ')[0]
                                fps = float(fps_str)
                            except: pass
                        continue
                    
                    try:
                        scene_num = int(row[0])
                        start_frame = int(row[1])
                        length = int(row[7])
                        raw_scenes.append([start_frame, length, f"VCut {scene_num}"])
                    except: continue

        if not raw_scenes:
            raise ValueError("No scenes found in the CSV or EDL file. Is the format correct?")

        # 1-Frame Cut Offset: Shift all cuts 1 frame back as requested
        for i in range(1, len(raw_scenes)):
            if raw_scenes[i][0] > 0:
                raw_scenes[i][0] -= 1
                
        # Recalculate contiguous lengths
        scenes = []
        for i in range(len(raw_scenes)):
            frame = raw_scenes[i][0]
            name = raw_scenes[i][2]
            if i < len(raw_scenes) - 1:
                next_frame = raw_scenes[i+1][0]
                length = next_frame - frame
            else:
                length = raw_scenes[i][1] # Keep original length for the very last scene
            if length > 0:
                scenes.append((frame, length, name))

        log_cb(f"Found {len(scenes)} scenes. Video Framerate: {fps}")
        
        # Calculate Timecode Offset
        offset_frames = parse_timecode_to_frames(tc_string, fps)
        log_cb(f"Session Start Timecode parsed as {offset_frames} frames offset.")

        # ---- MIDI MARKER GENERATION ----
        log_cb("Generating Frame-Accurate MIDI Marker file...")
        mid = MidiFile(type=0)
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Name the track so the DAW knows what to label it
        track.append(MetaMessage('track_name', name='VCut2DAW Markers', time=0))
        
        # Insert a dummy zero-velocity note to force strict DAWs to recognize this as a valid MIDI track
        track.append(mido.Message('note_on', note=0, velocity=0, time=0))
        track.append(mido.Message('note_off', note=0, velocity=0, time=0))
        
        # Secret Watermark
        track.append(MetaMessage('text', text='VCut2DAW (c) Antigravity', time=0))
        
        # We assume Pro Tools default 120 BPM (500000 microseconds per beat) 
        # so the offset scales correctly without needing tempo map import!
        track.append(MetaMessage('set_tempo', tempo=500000, time=0))
        mid.ticks_per_beat = 12000
        ticks_per_second = 24000
        
        scenes.sort(key=lambda x: x[0])
        
        # Add offset to all MIDI ticks so they drop exactly at the right timecode in Pro Tools
        offset_ticks = int(round((offset_frames / fps) * ticks_per_second))
        
        last_tick = 0
        for frame, length, name in scenes:
            abs_tick = offset_ticks + int(round((frame / fps) * ticks_per_second))
            delta_tick = abs_tick - last_tick
            track.append(MetaMessage('marker', text=name, time=delta_tick))
            last_tick = abs_tick

        mid.save(midi_path)
        
        # ---- AAF OFFLINE CLIP TRACK GENERATION ----
        log_cb("Generating Compliant AAF Clip Track for Pro Tools...")
        import aaf2
        
        # Determine exact video edit rate for Timecode metadata
        video_edit_rate = int(fps) if isinstance(fps, float) and fps.is_integer() else fps
        if abs(fps - 23.976) < 0.001: video_edit_rate = aaf2.rational.AAFRational(24000, 1001)
        elif abs(fps - 29.97) < 0.001: video_edit_rate = aaf2.rational.AAFRational(30000, 1001)
        
        # Audio operates perfectly at Sample Rate (48000 Hz) to avoid fractional frame drift
        sample_rate = 48000

        with aaf2.open(aaf_path, "w") as f:
            # 1. Source Mob (Represents physical missing file)
            source_mob = f.create.SourceMob("Dummy_Audio_File")
            f.content.mobs.append(source_mob)
            
            descriptor = f.create.PCMDescriptor()
            locator = f.create.NetworkLocator()
            locator['URLString'].value = "file:///dummy_scene_audio.wav"
            descriptor.locator.append(locator)
            descriptor['SampleRate'].value = sample_rate
            descriptor['AudioSamplingRate'].value = sample_rate
            descriptor['Channels'].value = 1
            descriptor['QuantizationBits'].value = 16
            
            # Required properties for PCMDescriptor
            descriptor['BlockAlign'].value = 2 # 1 channel * (16 bits / 8)
            descriptor['AverageBPS'].value = 96000 # 48000 * 2
            
            # Find total length in video frames
            total_frames = max(frame + length for frame, length, name in scenes) if scenes else 1000
            
            # Length in exactly calculated audio samples
            audio_samples = int(round((total_frames / fps) * sample_rate)) if fps > 0 else sample_rate
            descriptor['Length'].value = audio_samples
            
            source_mob.descriptor = descriptor
            
            # Sound slot runs at 48000 EditRate
            source_slot = source_mob.create_sound_slot(edit_rate=sample_rate)
            source_slot.segment.length = audio_samples
            
            # Add Timecode to Source Mob (Timecode tracks run at video_edit_rate)
            src_tc_slot = source_mob.create_timeline_slot(edit_rate=video_edit_rate)
            src_tc_clip = f.create.Timecode(int(round(fps)), drop=False)
            src_tc_clip.start = offset_frames
            src_tc_slot.segment = src_tc_clip
            
            # 2. Master Mob (Represents imported clip)
            master_mob = f.create.MasterMob("Scene_Clips_Master")
            f.content.mobs.append(master_mob)
            master_slot = master_mob.create_sound_slot(edit_rate=sample_rate)
            master_clip = source_mob.create_source_clip(slot_id=source_slot.slot_id, start=0, length=audio_samples)
            master_slot.segment.components.append(master_clip)
            
            # Add Timecode to Master Mob to stamp it
            tc_slot = master_mob.create_timeline_slot(edit_rate=video_edit_rate)
            tc_clip = f.create.Timecode(int(round(fps)), drop=False)
            tc_clip.start = offset_frames
            tc_slot.segment = tc_clip
            
            # 3. Composition Mob (The Timeline/Track)
            comp_mob = f.create.CompositionMob("Scene Cuts Timeline")
            f.content.mobs.append(comp_mob)
            comp_slot = comp_mob.create_sound_slot(edit_rate=sample_rate)
            
            # Add Timecode to Composition Mob to stamp the sequence
            comp_tc_slot = comp_mob.create_timeline_slot(edit_rate=video_edit_rate)
            comp_tc_clip = f.create.Timecode(int(round(fps)), drop=False)
            comp_tc_clip.start = offset_frames
            comp_tc_slot.segment = comp_tc_clip
            
            # Add all cuts with Sample-Frame Accumulation (fractional rounding)
            current_timeline_sample = 0
            for frame, length, name in scenes:
                # Calculate exact absolute start and end in samples
                scene_start_sample = int(round((frame / fps) * sample_rate))
                scene_end_sample = int(round(((frame + length) / fps) * sample_rate))
                scene_sample_length = scene_end_sample - scene_start_sample
                
                # Fill any gap with silence/filler to maintain perfect absolute time sync
                if scene_start_sample > current_timeline_sample:
                    gap_samples = scene_start_sample - current_timeline_sample
                    filler = f.create.Filler("Sound", gap_samples)
                    comp_slot.segment.components.append(filler)
                
                # Minimum 1 sample length
                scene_sample_length = max(1, scene_sample_length)
                clip = master_mob.create_source_clip(slot_id=master_slot.slot_id, start=scene_start_sample, length=scene_sample_length)
                comp_slot.segment.components.append(clip)
                
                current_timeline_sample = scene_start_sample + scene_sample_length
                
        success_msg = f"Step 2 Complete!\n\n1) MIDI Markers saved at:\n{midi_path}\n\n2) Empty Clip Track (AAF) saved at:\n{aaf_path}"
        log_cb(success_msg)
        done_cb(success_msg, True)

    except Exception as e:
        err_msg = f"Error during Generation: {str(e)}"
        log_cb(err_msg)
        done_cb(err_msg, False)

def on_step2_done(msg, success):
    btn_detect.configure(state="normal")
    btn_convert.configure(state="normal")
    if success:
        messagebox.showinfo("Success", msg)
    else:
        messagebox.showerror("Error", msg)

def start_convert():
    csv_path = csv_entry.get()
    if not csv_path or not os.path.exists(csv_path):
        messagebox.showerror("Error", "Please select a valid CSV/EDL file first.")
        return

    tc_string = tc_entry.get().strip()
    if not tc_string:
        tc_string = "01:00:00:00"
        
    out_base = output_entry.get().strip()
    if not out_base:
        out_base = DEFAULT_OUT_DIR
        
    midi_out_dir = os.path.join(out_base, "MIDI")
    aaf_out_dir = os.path.join(out_base, "AAF")
    os.makedirs(midi_out_dir, exist_ok=True)
    os.makedirs(aaf_out_dir, exist_ok=True)

    proj_name = proj_name_entry.get().strip()
    if not proj_name:
        csv_filename = os.path.basename(csv_path)
        proj_name = os.path.splitext(csv_filename)[0]
        if proj_name.endswith("-Scenes"):
            proj_name = proj_name.replace("-Scenes", "")
            
    output_midi = os.path.join(midi_out_dir, f"{proj_name}_Markers.mid")
    output_aaf = os.path.join(aaf_out_dir, f"{proj_name}_ClipTrack.aaf")

    btn_detect.configure(state="disabled")
    btn_convert.configure(state="disabled")
    
    def cb_log(m): log_area.after(0, log_message, m)
    def cb_done(m, s): log_area.after(0, lambda: on_step2_done(m, s))
    
    threading.Thread(target=run_step2_process, args=(csv_path, output_midi, output_aaf, tc_string, cb_log, cb_done), daemon=True).start()


def start_full_run():
    global _auto_proceed_step2
    
    _auto_proceed_step2 = True
    start_detect()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- GUI Setup ---

import multiprocessing
if __name__ == "__main__":
    multiprocessing.freeze_support()

    root = ctk.CTk()
    root.title("VCut2DAW - Video to Scene Markers for DAWs | by F.Utku Gercik")
    root.geometry("700x740")
    root.minsize(700, 740)
    root.resizable(True, True)
    
    try:
        root.iconbitmap(resource_path("icon.ico"))
    except:
        pass
    
    def show_about():
        about_text = (
            "VCut2DAW v1.0\n"
            "A Video to Scene Markers tool for DAWs (Pro Tools, Nuendo, Logic, etc.)\n\n"
            "Developed by: F.Utku Gercik\n"
            "Email: utkugercik@gmail.com\n"
            "GitHub: https://github.com/rhinofug/VCut2DAW\n\n"
            "License: CC BY-NC 4.0 (Non-Commercial)\n"
            "(c) 2026 - Built with Antigravity"
        )
        messagebox.showinfo("About VCut2DAW", about_text)
    
    
    
    frame = ctk.CTkFrame(root, corner_radius=10)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # ---- STEP 1 SECTION ----
    step1_frame = ctk.CTkFrame(frame, corner_radius=8)
    step1_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    ctk.CTkLabel(step1_frame, text="Phase 1: Video Analysis (Creates CSV)", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    
    video_file_frame = ctk.CTkFrame(step1_frame, fg_color="transparent")
    video_file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    video_entry = ctk.CTkEntry(video_file_frame)
    video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    video_browse_btn = ctk.CTkButton(video_file_frame, text="Browse Video...", command=select_video_file, width=120)
    video_browse_btn.pack(side=tk.RIGHT)
    
    btn_detect = ctk.CTkButton(step1_frame, text="Step 1: Detect Scenes", command=start_detect, fg_color="#2196F3", hover_color="#1976D2", font=("Arial", 14, "bold"), height=40)
    btn_detect.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    
    # ---- STEP 2 SECTION ----
    step2_frame = ctk.CTkFrame(frame, corner_radius=8)
    step2_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    ctk.CTkLabel(step2_frame, text="Phase 2: Convert to DAW (Creates MIDI & AAF)", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    
    csv_file_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
    csv_file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    csv_entry = ctk.CTkEntry(csv_file_frame)
    csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    csv_browse_btn = ctk.CTkButton(csv_file_frame, text="Browse CSV...", command=select_csv_file, width=120)
    csv_browse_btn.pack(side=tk.RIGHT)
    
    tc_frame = ctk.CTkFrame(step2_frame, fg_color="transparent")
    tc_frame.pack(fill=tk.X, padx=10, pady=5)
    tc_label = ctk.CTkLabel(tc_frame, text="Session Start Timecode (e.g. 01:00:00:00):")
    tc_label.pack(side=tk.LEFT)
    tc_entry = ctk.CTkEntry(tc_frame, width=150, justify="center")
    tc_entry.insert(0, "01:00:00:00")
    tc_entry.pack(side=tk.LEFT, padx=10)
    
    btn_convert = ctk.CTkButton(step2_frame, text="Step 2: Generate MIDI & AAF", command=start_convert, fg_color="#2196F3", hover_color="#1976D2", font=("Arial", 14, "bold"), height=40)
    btn_convert.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    
    
    # ---- FULL RUN SECTION ----
    full_run_frame = ctk.CTkFrame(frame, fg_color="transparent")
    full_run_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    btn_full_run = ctk.CTkButton(full_run_frame, text="Video to Markers (Full Run)", command=start_full_run, fg_color="#4CAF50", hover_color="#388E3C", font=("Arial", 16, "bold"), height=50)
    btn_full_run.pack(fill=tk.X)
    
    # ---- OUTPUT DIRECTORY SECTION ----
    out_frame = ctk.CTkFrame(frame, corner_radius=8, fg_color="transparent")
    out_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    ctk.CTkLabel(out_frame, text="Global Output Folder & Project Prefix (Optional)", font=("Arial", 12), text_color="gray").pack(anchor="w", padx=10, pady=(5, 0))
    
    out_file_frame = ctk.CTkFrame(out_frame, fg_color="transparent")
    out_file_frame.pack(fill=tk.X, padx=10, pady=2)
    
    proj_name_frame = ctk.CTkFrame(out_frame, fg_color="transparent")
    proj_name_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
    ctk.CTkLabel(proj_name_frame, text="Project / Output Prefix:", text_color="gray").pack(side=tk.LEFT)
    proj_name_entry = ctk.CTkEntry(proj_name_frame, placeholder_text="Default: Auto from Video/CSV", fg_color="#2b2b2b", text_color="gray")
    proj_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    output_entry = ctk.CTkEntry(out_file_frame, fg_color="#2b2b2b", text_color="gray")
    output_entry.insert(0, DEFAULT_OUT_DIR)
    output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def select_output_dir():
        dirpath = filedialog.askdirectory(title="Select Output Folder")
        if dirpath:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, dirpath)
            log_message(f"Output folder set to: {dirpath}")
    
    out_browse_btn = ctk.CTkButton(out_file_frame, text="Browse...", command=select_output_dir, width=80, fg_color="#333333", hover_color="#444444", text_color="gray")
    out_browse_btn.pack(side=tk.RIGHT)
    
    
    # ---- CONSOLE ----
    
    log_label = ctk.CTkLabel(frame, text="Console Output:", font=("Arial", 12, "bold"))
    log_label.pack(anchor="w", padx=10, pady=(5, 0))
    
    import webbrowser
    
    def open_coffee():
        webbrowser.open("https://buymeacoffee.com/rhinofug")
    
    coffee_btn = ctk.CTkButton(frame, text="☕ Buy me a coffee", command=open_coffee, fg_color="#FFDD00", hover_color="#FFC300", text_color="black", font=("Arial", 12, "bold"), width=150, height=30)
    coffee_btn.pack(side=tk.BOTTOM, pady=(0, 5))
    
    footer = ctk.CTkLabel(frame, text="Developed by F.Utku Gercik | VCut2DAW v1.0 | License: CC BY-NC 4.0 | (i) Click for About", text_color="gray", font=("Arial", 10), cursor="hand2")
    footer.pack(side=tk.BOTTOM, pady=(10, 0))
    footer.bind("<Button-1>", lambda e: show_about())
    
    
    log_area = ctk.CTkTextbox(frame, height=120, state="disabled", fg_color="#1e1e1e", text_color="#00ff00", font=("Consolas", 12))
    log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    root.mainloop()

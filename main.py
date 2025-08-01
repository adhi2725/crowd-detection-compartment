import cv2
from ultralytics import YOLO
import tkinter
from tkinter import messagebox
import pyttsx3

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Crowd threshold: if people < this → free
CROWD_THRESHOLD = 5

# List of 4 video file paths
video_paths = [
    r"C:\Users\Adhi\Downloads\cmpartment_cctv.mp4.mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (2).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (3).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (4).mp4",
    r"C:\Users\Adhi\Downloads\cmpartment_cctv.mp4.mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (2).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (3).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (4).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (3).mp4",
    r"C:\Users\Adhi\Downloads\videoplayback (4).mp4",
]

# Setup text-to-speech
engine = pyttsx3.init()

def speak(message):
    engine.say(message)
    engine.runAndWait()

def show_popup(message):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("Available Compartments", message)

# Count people in one frame
def count_people(frame):
    results = model(frame)
    count = 0
    for result in results:
        for cls in result.boxes.cls:
            if int(cls) == 0:  # class 0 = person
                count += 1
    return count

# Analyze multiple frames for better accuracy
def analyze_video(path, sample_frames=5):
    cap = cv2.VideoCapture(path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    counts = []

    if total_frames == 0:
        return -1  # unreadable

    frame_indices = [int(total_frames * i / sample_frames) for i in range(sample_frames)]

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        count = count_people(frame)
        counts.append(count)

    cap.release()
    return max(counts) if counts else -1  # Use max crowd seen

# Main logic
compartment_counts = []
free_compartments = []

print("🔎 Analyzing compartments...\n")

for i, path in enumerate(video_paths):
    print(f"Checking Compartment {i + 1}...")
    people_count = analyze_video(path, sample_frames=5)

    if people_count == -1:
        print(f"[ERROR] Could not analyze Compartment {i + 1}")
        continue

    print(f"Compartment {i + 1}: {people_count} people")
    compartment_counts.append(people_count)

    if people_count < CROWD_THRESHOLD:
        free_compartments.append(i + 1)

# Result message
if free_compartments:
    message = f"Compartments {', '.join(map(str, free_compartments))} are free. Please consider this compartments others are full."
else:
    message = "⚠️ All compartments are currently crowded."

print(f"\n✅ {message}")
show_popup(message)
speak(message)

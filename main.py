import cv2
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from zipfile import ZipFile

FORMATTED_FILENAME = ""
FORMATTED_ZIP_FILENAME = ""
MAX_WIDTH = 800
MAX_HEIGHT = 600

screenshot_count = 0
frozen_screenshot_count = 0
freeze = False

def zip_screenshots(video_dir):
    images = []
    for root, dirs, files in os.walk(video_dir):
        for file in files:
            if file.endswith(".png"):
                images.append(os.path.join(root, file))
    zip_path = os.path.join(video_dir, f"{FORMATTED_ZIP_FILENAME}.zip")
    with ZipFile(zip_path, 'w') as zip:
        for image in images:
            zip.write(image, os.path.basename(image))
    print(f"--------zipped {zip_path}--------")
def take_screenshot(frame, video_dir):
    global screenshot_count, frozen_screenshot_count, freeze
    if freeze:
        frozen_screenshot_count += 1
        screenshot_filename = f'{screenshot_count}.{frozen_screenshot_count}.png'
    else:
        screenshot_count += 1
        screenshot_filename = f'{screenshot_count}.png'
    screenshot_path = os.path.join(video_dir, screenshot_filename)
    cv2.imwrite(screenshot_path, frame)
    print(f"Screenshot saved as {screenshot_path}")
def resize_frame(frame):
    # frame.shape returns (height, width, channels)
    height, width = frame.shape[:2]

    # Calculate aspect ratio（宽高比）
    aspect_ratio = width / height

    # Resize frame to fit within MAX_WIDTH x MAX_HEIGHT while maintaining aspect ratio
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        if aspect_ratio > 1:  # Landscape orientation
            new_width = MAX_WIDTH
            new_height = int(new_width / aspect_ratio)
        else:  # Portrait or square orientation
            new_height = MAX_HEIGHT
            new_width = int(new_height * aspect_ratio)
        
        # Resize the frame
        frame = cv2.resize(frame, (new_width, new_height))

    return frame

def ask_video_path():
    Tk().withdraw()
    video_path = askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.webm")])
    return video_path
def main(video_path):
    global freeze, frozen_screenshot_count
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate the number of frames to skip for 2 seconds
    frame_skip = int(fps * 2)

    # Flag to toggle pause/play
    paused = False

    while cap.isOpened():
        # Check if paused
        if not paused:
            ret, frame = cap.read()

            if not ret:
                # loop the video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = resize_frame(frame)

            # Display the frame
            cv2.imshow('Video Frame', frame)

        # Keyboard input handling
        key = cv2.waitKey(25) & 0xFF

        if key == ord('q'):
            # quit the program
            zip_screenshots(os.path.dirname(video_path))
            break
        elif key == ord('s'):
            # Toggle pause/play
            paused = not paused
        elif key == ord('p'):
            # Take screenshot
            take_screenshot(frame, os.path.dirname(video_path))
        elif key == ord('z'):
            # Move backward 2 seconds
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = max(current_frame - frame_skip, 0)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        elif key == ord('x'):
            # Move forward 2 seconds
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = min(current_frame + frame_skip, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        elif key == ord('f'):
            # toggle freeze/unfreezed
            freeze = not freeze
            frozen_screenshot_count = 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_path = ask_video_path()
    main(video_path)

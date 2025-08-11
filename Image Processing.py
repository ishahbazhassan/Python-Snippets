import os
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse

BLANK_THRESHOLD = 245      # Intensity to consider "blank" (0-255)
MIN_LINE_HEIGHT = 5        # Minimum height for blank rows/columns
MIN_SEGMENT_SIZE = 250     # Discard segments smaller than this (shortest edge)
CROP_TOLERANCE = 30        # Tolerance for color difference when cropping borders
FINAL_TRIM = 2             # Additional pixels trimmed from final crops
SAVE_AS_PNG = False        # True = PNG (lossless), False = JPEG (95% quality)

download_dir = os.path.join(os.path.expanduser("~"), "Output_pics", "downloaded")
processed_dir = os.path.join(os.path.expanduser("~"), "Output_pics", "processed")
os.makedirs(download_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)


def download_image(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.alibaba.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert('RGB')
        filename = os.path.join(download_dir, os.path.basename(urlparse(url).path))
        img.save(filename)
        return filename
    else:
        raise Exception(f"Failed to download image from {url}")

def find_blank_lines(gray, axis='horizontal'):
    blank_spans = []
    size = gray.shape[0 if axis == 'horizontal' else 1]
    in_blank = False
    start = 0

    for i in range(size):
        line = gray[i, :] if axis == 'horizontal' else gray[:, i]
        if np.mean(line) >= BLANK_THRESHOLD:
            if not in_blank:
                start = i
                in_blank = True
        else:
            if in_blank and (i - start) >= MIN_LINE_HEIGHT:
                blank_spans.append((start, i))
                in_blank = False
    return blank_spans

def trim_pixels(image, trim=FINAL_TRIM):
    h, w = image.shape[:2]
    if h > 2 * trim and w > 2 * trim:
        return image[trim:h-trim, trim:w-trim]
    return image

def remove_large_blank_edges(image, threshold=BLANK_THRESHOLD, min_content_height=MIN_SEGMENT_SIZE):
    """Remove big white/blank bands from top/bottom/left/right."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Top
    top = 0
    for i in range(gray.shape[0]):
        if np.mean(gray[i, :]) < threshold:
            top = i
            break

    # Bottom
    bottom = gray.shape[0]
    for i in range(gray.shape[0] - 1, -1, -1):
        if np.mean(gray[i, :]) < threshold:
            bottom = i + 1
            break

    # Left
    left = 0
    for i in range(gray.shape[1]):
        if np.mean(gray[:, i]) < threshold:
            left = i
            break

    # Right
    right = gray.shape[1]
    for i in range(gray.shape[1] - 1, -1, -1):
        if np.mean(gray[:, i]) < threshold:
            right = i + 1
            break

    cropped = image[top:bottom, left:right]

    if min(cropped.shape[:2]) >= min_content_height:
        return cropped
    return image

def crop_borders_robust(image, tolerance=CROP_TOLERANCE):
    h, w = image.shape[:2]
    corners = np.array([
        image[0, 0], image[0, w-1], image[h-1, 0], image[h-1, w-1]
    ])
    bg_color = np.median(corners, axis=0).astype(np.uint8)

    diff = np.sqrt(np.sum((image.astype(np.float32) - bg_color)**2, axis=2))
    mask = (diff > tolerance).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    coords = cv2.findNonZero(closed)
    if coords is not None:
        x, y, w_box, h_box = cv2.boundingRect(coords)
        cropped = image[y:y+h_box, x:x+w_box]
        cropped = trim_pixels(cropped)
        cropped = remove_large_blank_edges(cropped)
        return cropped
    return image

def split_vertical_segments(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blank_cols = find_blank_lines(gray, axis='vertical')
    segments = []
    prev_x = 0
    for (start_x, end_x) in blank_cols:
        seg = image[:, prev_x:start_x]
        if min(seg.shape[:2]) >= MIN_SEGMENT_SIZE:
            seg = crop_borders_robust(seg)
            segments.append(seg)
        prev_x = end_x
    last = image[:, prev_x:]
    if min(last.shape[:2]) >= MIN_SEGMENT_SIZE:
        last = crop_borders_robust(last)
        segments.append(last)
    return segments

def split_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blank_rows = find_blank_lines(gray, axis='horizontal')
    segments = []
    prev_y = 0
    for (start_y, end_y) in blank_rows:
        seg = image[prev_y:start_y]
        if min(seg.shape[:2]) >= MIN_SEGMENT_SIZE:
            seg = crop_borders_robust(seg)
            segments.append(seg)
        prev_y = end_y
    last = image[prev_y:]
    if min(last.shape[:2]) >= MIN_SEGMENT_SIZE:
        last = crop_borders_robust(last)
        segments.append(last)

    final_segments = []
    for seg in segments:
        sub_segs = split_vertical_segments(seg)
        final_segments.extend(sub_segs)
    return final_segments

def process_image(file_path):
    image = cv2.imread(file_path)
    name = os.path.splitext(os.path.basename(file_path))[0]
    segments = split_image(image)
    for idx, seg in enumerate(segments):
        h, w = seg.shape[:2]
        if min(h, w) >= MIN_SEGMENT_SIZE:
            ext = ".png" if SAVE_AS_PNG else ".jpg"
            out_path = os.path.join(processed_dir, f"{name}_segment_{idx+1}{ext}")
            if SAVE_AS_PNG:
                cv2.imwrite(out_path, seg)  # lossless
            else:
                cv2.imwrite(out_path, seg, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"✅ Saved: {out_path}")

def main(image_urls):
    for url in image_urls:
        try:
            file_path = download_image(url)
            process_image(file_path)
        except Exception as e:
            print(f"❌ Error with {url}: {e}")

image_urls = [
    "https://img.alicdn.com/imgextra/i2/1712484042/TB2Ki20qFXXXXclXpXXXXXXXXXX_!!1712484042.jpg",
    "https://img.alicdn.com/imgextra/i3/1712484042/O1CN01RtCBpB1fjHVLX1oBK_!!1712484042.jpg"
]

if __name__ == "__main__":
    main(image_urls)

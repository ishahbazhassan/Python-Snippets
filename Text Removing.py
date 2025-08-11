import cv2
import numpy as np
import easyocr
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import os

# Initialize EasyOCR reader (Chinese + English)
reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

# Create output folder
os.makedirs("output", exist_ok=True)

def download_image(url):
    response = requests.get(url, timeout=10)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def get_product_mask(image):
    """Rough segmentation of product area using largest contour detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    kernel = np.ones((5,5), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)

    return mask

def create_text_mask(image, product_mask):
    results = reader.readtext(image)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    for (bbox, text, conf) in results:
        if conf > 0.3:
            pts = np.array(bbox, dtype=np.int32)
            text_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.fillPoly(text_mask, [pts], 255)

            # Keep only text outside product
            overlap = cv2.bitwise_and(product_mask, product_mask, mask=text_mask)
            if np.sum(overlap) == 0:
                cv2.fillPoly(mask, [pts], 255)

    kernel = np.ones((5,5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    return mask

def remove_text(image, mask):
    # Natural inpainting with larger radius
    cleaned = cv2.inpaint(image, mask, 7, cv2.INPAINT_TELEA)
    # Light smoothing to blend edges
    blurred = cv2.GaussianBlur(cleaned, (3,3), 0)
    return blurred

def process_and_save(url, idx):
    image = download_image(url)
    product_mask = get_product_mask(image)
    text_mask = create_text_mask(image, product_mask)
    cleaned = remove_text(image, text_mask)

    output_path = os.path.join("output", f"cleaned_{idx}.png")
    cv2.imwrite(output_path, cleaned)  # Always PNG, no compression
    print(f"[✔] Saved cleaned image: {output_path}")

    # Optional: preview
    plt.figure(figsize=(12,6))
    plt.subplot(1,3,1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Original")
    plt.axis('off')

    plt.subplot(1,3,2)
    plt.imshow(product_mask, cmap="gray")
    plt.title("Product Mask")
    plt.axis('off')

    plt.subplot(1,3,3)
    plt.imshow(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB))
    plt.title("Cleaned")
    plt.axis('off')
    plt.show()

# Example URLs
urls = [
    "https://img.alicdn.com/imgextra/i1/1712484042/O1CN01mLN6kk1fjHZODL77S_!!1712484042.jpg",
    "https://img.alicdn.com/imgextra/i3/1712484042/O1CN01btXCXm1fjHZYStUBU_!!1712484042.jpg"
]

for i, url in enumerate(urls, start=1):
    process_and_save(url, i)

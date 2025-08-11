import cv2
import numpy as np
from rembg import remove
import io
from PIL import Image

def remove_background(input_path, output_path):
    # Load the image using OpenCV
    image = cv2.imread(input_path)

    # Convert image to RGBA (OpenCV loads as BGR)
    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

    # Convert OpenCV image to bytes for rembg
    pil_image = Image.fromarray(image_rgba)
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    # Remove background
    result_bytes = remove(img_bytes)

    # Convert result bytes back to image
    result_image = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    result_np = np.array(result_image)

    # Save the result
    cv2.imwrite(output_path, cv2.cvtColor(result_np, cv2.COLOR_RGBA2BGRA))
    print(f"Background removed and saved to {output_path}")

# Example usage
input_image_path = "C:/Users/hp/Desktop/premium_photo-1666672388644-2d99f3feb9f1.jpeg"   # Replace with your image
output_image_path = "C:/Users/hp/Desktop/Output image/Output_image.png"
remove_background(input_image_path, output_image_path)
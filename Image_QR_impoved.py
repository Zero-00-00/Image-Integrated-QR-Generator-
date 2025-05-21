import qrcode
import numpy as np
import requests
from PIL import Image, ImageEnhance
from tqdm import tqdm  # Progress bar

def crop_to_square(image):
    """Crops the image to a square while keeping the center."""
    width, height = image.size
    min_size = min(width, height)
    left = (width - min_size) // 2
    top = (height - min_size) // 2
    right = left + min_size
    bottom = top + min_size
    return image.crop((left, top, right, bottom))

def generate_qr_with_adaptive_bg(url, bg_image_path, adjust_brightness, output_path=r"C:\Users\pralo\OneDrive\Desktop\out.png"):
    # Load Background Image (Handle URLs)
    if bg_image_path.startswith("http"):
        response = requests.get(bg_image_path, stream=True)
        response.raise_for_status()
        bg_img = Image.open(response.raw).convert("RGBA")
    else:
        bg_img = Image.open(bg_image_path).convert("RGBA")

    # Determine QR size based on image size
    img_width, img_height = bg_img.size
    qr_size = min(img_width, img_height)  # Fit QR within the smallest dimension
    qr_size = max(300, qr_size)  # Ensure a minimum size for readability

    # Crop to square only if the image is large
    if min(img_width, img_height) > 500:
        bg_img = crop_to_square(bg_img)
    
    # Resize background to match QR code size
    bg_img = bg_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Generate QR Code
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image in black & white
    qr_img = qr.make_image(fill="black", back_color="white").convert("L")
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.NEAREST)

    # Convert images to NumPy arrays
    qr_array = np.array(qr_img)
    bg_array = np.array(bg_img)
    bg_gray = np.array(bg_img.convert("L"))

    final_img = None  # Placeholder for final image

    if adjust_brightness == "yes":
        # Adjust brightness adaptively
        new_img_array = np.copy(bg_array)

        for i in tqdm(range(qr_size), desc="Adjusting Brightness", unit="rows"):
            for j in range(qr_size):
                bg_brightness = bg_gray[i, j]

                if qr_array[i, j] < 128:  # QR code black area
                    new_img_array[i, j] = [0, 0, 0, 200]  # Keep QR black
                else:  # QR code white area
                    if bg_brightness < 120:
                        # Lighten dark areas just enough for QR to be visible
                        new_img_array[i, j] = np.clip(bg_array[i, j] + 80, 0, 255)

        final_img = Image.fromarray(new_img_array.astype("uint8"))

    else:
        # Make the QR white parts transparent
        qr_img_rgba = Image.new("RGBA", (qr_size, qr_size), (0, 0, 0, 0))  # Transparent background
        
        for i in tqdm(range(qr_size), desc="Making QR Transparent", unit="rows"):
            for j in range(qr_size):
                if qr_array[i, j] < 128:  # Black QR code part
                    qr_img_rgba.putpixel((i, j), (0, 0, 0, 200))  # Black (fully visible)
                else:
                    qr_img_rgba.putpixel((i, j), (255, 255, 255, 0))  # White (fully transparent)

        # Overlay QR code onto background
        final_img = bg_img.copy()
        final_img.paste(qr_img_rgba, (0, 0), qr_img_rgba)

    # Save the final image
    final_img.save(output_path)
    print(f"✅ QR code saved at: {output_path}")

# Example Usage
url = input("Enter the URL for the QR code: ")
bg_image_path = input("Enter the path to the background image (local path or URL): ")

# Ask user for permission to adjust brightness
adjust_brightness = input("Would you like to adjust brightness for better visibility? (yes/no): ").strip().lower()

generate_qr_with_adaptive_bg(url, bg_image_path, adjust_brightness)

import qrcode
import numpy as np
import requests
from PIL import Image, ImageEnhance

def generate_qr_with_embedded_bg(url, bg_image_path, output_path=r"C:\Users\pralo\OneDrive\Desktop\final.png", qr_size=500, darken_factor=0.3):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=6,  # Slightly higher version for more data & clarity
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image in black & white
    qr_img = qr.make_image(fill="black", back_color="white").convert("L")
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.NEAREST)

    # Load Background Image (Handle URLs)
    if bg_image_path.startswith("http"):
        response = requests.get(bg_image_path, stream=True)
        response.raise_for_status()  # Raise error for failed requests
        bg_img = Image.open(response.raw).convert("RGB")
    else:
        bg_img = Image.open(bg_image_path).convert("RGB")

    bg_img = bg_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)

    # Darken the background for QR black areas
    enhancer = ImageEnhance.Brightness(bg_img)
    bg_darkened = enhancer.enhance(darken_factor)  # Reduce brightness for black QR areas

    # Convert images to NumPy arrays
    qr_array = np.array(qr_img)[:, :, np.newaxis]  # Expand dimensions to (500,500,1)
    qr_array = np.repeat(qr_array, 3, axis=2)  # Convert to (500,500,3)

    bg_array = np.array(bg_img)
    bg_darkened_array = np.array(bg_darkened)

    # Replace black QR areas with the darkened background
    new_img_array = np.where(qr_array < 128, bg_darkened_array, bg_array)

    # Convert back to an image
    final_img = Image.fromarray(new_img_array)

    # Save the final image
    final_img.save(output_path)
    print(f"QR code saved at: {output_path}")

# Example Usage
url = input("Enter the URL for the QR code: ")
bg_image_path = input("Enter the path to the background image (local path or URL)Recomonded evenly lit bright clear image: ")
generate_qr_with_embedded_bg(url, bg_image_path)

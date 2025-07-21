from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np


DEFAULT_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def remove_white_background(img: Image.Image, threshold=240) -> Image.Image:
    """
    Converts white-ish background to transparent in an RGBA image.
    Pixels where R, G, B > threshold are made fully transparent.
    """
    img = img.convert("RGBA")
    data = np.array(img)

    # Extract RGBA channels
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Create mask of white-ish pixels
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # Set alpha to 0 where white
    data[white_mask, 3] = 0

    # Create new image
    return Image.fromarray(data, mode="RGBA")

def add_text_to_image(image: Image.Image, text: str, font_path=DEFAULT_FONT_PATH, font_size=60, padding=60) -> Image.Image:
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    img_width, img_height = image.size

    # Create dummy image to measure text size
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)

    # Get bounding box of the text (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # New canvas with space for the image and text
    total_height = img_height + padding + text_height + 50
    new_img = Image.new("RGBA", (img_width, total_height), (0, 0, 0, 0))

    # Paste original image
    new_img.paste(image, (0, 0), image)

    # Draw the text centered
    draw = ImageDraw.Draw(new_img)
    text_x = (img_width - text_width) // 2
    text_y = img_height + padding
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0, 255))

    return new_img

def generate_mug_mockup(user_img, mug_base_path,text, output_size=(800, 600)):
    # Load base mug image
    mug = Image.open(mug_base_path).convert("RGBA")
    
    # Load user's image and resize to fit printable area
    user_img.convert("RGBA")  # Ensure user image is RGBA
    user_img = remove_white_background(user_img)  # Remove white background if needed
    user_img = add_text_to_image(user_img, text)  # Add text if desired
    
    # Define print area on mug (manually set based on your template)
    # Example: x=200, y=300, w=400, h=200
    print_area = (480, 300, 350, 350)
    x, y, w, h = print_area
    
    # Resize user's image to fit print area
    user_img_resized = user_img.resize((w, h))
    
    # Paste onto mug
    mug.paste(user_img_resized, (x, y), user_img_resized)  # Use alpha channel for transparency

    # Optional: apply mug lighting overlay for realism
    # overlay = Image.open("mug_overlay.png").convert("RGBA")
    # mug = Image.alpha_composite(mug, overlay)

    # Resize for frontend if needed
    #mug = mug.resize(output_size)

    # Save to in-memory buffer
    img_bytes = io.BytesIO()
    mug.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes  # ready to send via HTTP response

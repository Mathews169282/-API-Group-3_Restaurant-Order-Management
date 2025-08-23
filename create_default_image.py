from PIL import Image, ImageDraw, ImageFont
import os

def create_default_image():
    # Create a 400x300 image with a light gray background
    img = Image.new('RGB', (400, 300), color='#f0f0f0')
    d = ImageDraw.Draw(img)
    
    # Add text
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        # Fall back to default font
        font = ImageFont.load_default()
    
    # Draw text in the center
    text = "Menu Item\nNo Image Available"
    text_bbox = d.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (400 - text_width) / 2
    y = (300 - text_height) / 2
    
    d.text((x, y), text, fill="#888888", font=font, align="center")
    
    # Create media directory if it doesn't exist
    os.makedirs("media/menu_items", exist_ok=True)
    
    # Save the image
    img.save("media/menu_items/default_food.jpg")
    print("Default food image created at: media/menu_items/default_food.jpg")

if __name__ == "__main__":
    create_default_image()

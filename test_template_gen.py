from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

# Coordinates extracted from previous analysis
# Yellow (Product Image): (16, 65, 171, 214) - W: 155, H: 149
# Green (Shop Name): (77, 12, 293, 48) - W: 216, H: 36
# Red (Product Title): (178, 58, 496, 99) - W: 318, H: 41
# Purple 1 (Price): (535, 65, 564, 93) - W: 29, H: 28 (Upper one, unit price maybe? Or total?)
# Purple 2 (Total): (530, 223, 559, 252) - W: 29, H: 29 (Lower one, actual payment?)

# Let's assume Purple 1 is unit price and Purple 2 is total price. Usually they are the same for x1.
# Wait, looking at the template structure description from user:
# "Purple box represents price" -> It seems there are two purple boxes.
# Usually top right is unit price, bottom right is total payment.
# I should fill both with the price.

TEMPLATE_PATH = "/Users/mico/Documents/trae_projects/Sceneu-agent/template/image.png"
OUTPUT_DIR = "/Users/mico/Documents/trae_projects/Sceneu-agent/static/generate"

def get_font(size=20):
    """Attempt to load a font that supports Chinese characters."""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def generate_test_card():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    template = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(template)
    
    # 1. Product Image (Yellow Box)
    # Box: (16, 65, 171, 214)
    # Load a placeholder image
    try:
        resp = requests.get("https://via.placeholder.com/300", timeout=5)
        prod_img = Image.open(BytesIO(resp.content)).convert("RGBA")
        # Resize to fit yellow box (155x149)
        prod_img = prod_img.resize((155, 149), Image.Resampling.LANCZOS)
        template.paste(prod_img, (16, 65))
    except Exception as e:
        print(f"Failed to load product image: {e}")
        # Create a dummy image
        prod_img = Image.new('RGBA', (155, 149), color=(200, 200, 200, 255))

    # 2. Shop Name (Green Box)
    # Box: (77, 12, 293, 48)
    # Center vertically in the box?
    shop_name = "心疆农哥新疆生鲜店"
    font_size = 20
    font = get_font(font_size)
    # Position: (77, 12) is top-left. Let's add some padding.
    # Text color: Black or Dark Gray? The original text "淘宝" is orange.
    # Usually shop name is black.
    draw.text((80, 15), shop_name, font=font, fill=(0, 0, 0, 255))
    
    # 3. Product Title (Red Box)
    # Box: (178, 58, 496, 99) -> This seems to be the first line of title?
    # Or maybe multi-line? Height is 41, enough for 2 lines of small text or 1 line of large text.
    # Let's assume 1 line for now or truncate.
    title = "【顺丰包邮】新疆库尔勒香梨精选全"
    title_font = get_font(18)
    draw.text((178, 60), title, font=title_font, fill=(0, 0, 0, 255))
    
    # 4. Price (Purple Boxes)
    # Box 1: (535, 65, 564, 93) -> Unit Price integer part?
    # Box 2: (530, 223, 559, 252) -> Total Price integer part?
    # Wait, the boxes are very small (29x28). It might just cover the number area.
    # The "¥" symbol might be outside or inside?
    # The template has "¥" printed next to the box usually?
    # Let's look at the user description: "purple box represents price".
    # I should fill the price into these boxes.
    # But 29px width is very small for a price like "90".
    # Maybe the box indicates where the START of the price should be?
    # Or maybe the box covers the specific digits?
    # Let's assume we align the price text at these coordinates.
    
    price = "90"
    price_font = get_font(18)
    
    # Unit Price
    # Align right or left? Usually right aligned if it's a column?
    # Let's try drawing at top-left of the box.
    draw.text((535, 65), price, font=price_font, fill=(0, 0, 0, 255))
    
    # Total Price
    draw.text((530, 225), price, font=price_font, fill=(0, 0, 0, 255))

    # Clean up colored boxes?
    # The user said: "fill corresponding info... then eliminate the three colored boxes".
    # Since we are pasting OVER the boxes, if our content covers them, it's fine.
    # But text doesn't cover the background color.
    # So we need to "eliminate" the boxes, i.e., turn them white (or background color) BEFORE drawing text.
    
    # Let's refill the box areas with white first.
    
    # Re-open template to clean
    template_clean = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw_clean = ImageDraw.Draw(template_clean)
    
    # Fill White
    # Yellow (Product) - will be covered by image paste, so strictly speaking no need to fill white, but good practice.
    draw_clean.rectangle((16, 65, 171, 214), fill=(255, 255, 255, 255))
    
    # Green (Shop)
    draw_clean.rectangle((77, 12, 293, 48), fill=(255, 255, 255, 255))
    
    # Red (Title)
    draw_clean.rectangle((178, 58, 496, 99), fill=(255, 255, 255, 255))
    
    # Purple (Prices)
    draw_clean.rectangle((535, 65, 564, 93), fill=(255, 255, 255, 255))
    draw_clean.rectangle((530, 223, 559, 252), fill=(255, 255, 255, 255))
    
    # Now draw content on template_clean
    
    # Paste Image
    template_clean.paste(prod_img, (16, 65))
    
    # Draw Text
    draw_clean.text((80, 15), shop_name, font=font, fill=(0, 0, 0, 255))
    draw_clean.text((178, 65), title, font=title_font, fill=(0, 0, 0, 255))
    draw_clean.text((535, 65), price, font=price_font, fill=(0, 0, 0, 255))
    draw_clean.text((530, 225), price, font=price_font, fill=(0, 0, 0, 255))
    
    save_path = os.path.join(OUTPUT_DIR, "test_template_gen.png")
    template_clean.save(save_path)
    print(f"Saved to {save_path}")

if __name__ == "__main__":
    generate_test_card()

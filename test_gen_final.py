import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import uuid

# Config
TEMPLATE_PATH = os.path.join(os.getcwd(), "template", "image.png")
GENERATED_DIR = os.path.join(os.getcwd(), "static", "generate")

def get_font(size=20):
    """Attempt to load a font that supports Chinese characters."""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux (Debian/Ubuntu)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def generate_order_card(product_title: str, shop_name: str, price: str, product_image_url: str):
    """
    Generate an order screenshot card based on the template.
    Returns the relative URL path of the generated image.
    """
    try:
        if not os.path.exists(TEMPLATE_PATH):
            print(f"Template not found: {TEMPLATE_PATH}")
            return None
            
        # Clean the template first (remove colored boxes)
        template = Image.open(TEMPLATE_PATH).convert("RGBA")
        draw_clean = ImageDraw.Draw(template)
        
        # Fill White to clear colored boxes
        draw_clean.rectangle((16, 65, 171, 214), fill=(255, 255, 255, 255))
        draw_clean.rectangle((77, 12, 293, 48), fill=(255, 255, 255, 255))
        draw_clean.rectangle((178, 58, 496, 99), fill=(255, 255, 255, 255))
        draw_clean.rectangle((535, 65, 564, 93), fill=(255, 255, 255, 255))
        draw_clean.rectangle((530, 223, 559, 252), fill=(255, 255, 255, 255))

        # 1. Product Image
        try:
            # Mock image for test
            product_img = Image.new('RGBA', (155, 149), color=(255, 200, 0, 255)) # Orange mock
            # Add some text to mock image
            d = ImageDraw.Draw(product_img)
            d.text((10, 70), "PROD", fill=(0,0,0,255))
            
            product_img = product_img.resize((155, 149), Image.Resampling.LANCZOS)
            template.paste(product_img, (16, 65))
        except Exception as e:
            print(f"Failed to load product image: {e}")

        # Draw Text
        draw = ImageDraw.Draw(template)
        
        # 2. Shop Name
        shop_font = get_font(20)
        draw.text((80, 18), shop_name, font=shop_font, fill=(0, 0, 0, 255))
        
        # 3. Product Title
        title_font = get_font(18)
        
        # Truncate logic
        max_width = 496 - 178
        display_title = product_title
        while display_title:
            bbox = draw.textbbox((0, 0), display_title + "...", font=title_font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                break
            display_title = display_title[:-1]
            
        if len(display_title) < len(product_title):
            display_title += "..."
            
        draw.text((178, 60), display_title, font=title_font, fill=(0, 0, 0, 255))
        
        # 4. Price
        price_font = get_font(18)
        draw.text((535, 65), price, font=price_font, fill=(0, 0, 0, 255))
        draw.text((530, 225), price, font=price_font, fill=(0, 0, 0, 255))
        
        # Save result
        if not os.path.exists(GENERATED_DIR):
            os.makedirs(GENERATED_DIR)
            
        filename = f"test_final_{uuid.uuid4().hex}.png"
        save_path = os.path.join(GENERATED_DIR, filename)
        template.save(save_path, "PNG")
        
        return f"/static/generate/{filename}"
        
    except Exception as e:
        print(f"Error generating order card: {e}")
        return None

def test():
    # Long title to test truncation
    long_title = "【顺丰包邮】新疆库尔勒香梨精选全果特大果超甜多汁当季新鲜水果整箱批发包邮坏果包赔"
    shop = "心疆农哥新疆生鲜店"
    price = "90"
    img_url = "http://mock.url/img.png"

    print(f"Generating card for: {long_title}")
    
    output_path = generate_order_card(long_title, shop, price, img_url)
    
    if output_path:
        print(f"Success! Generated image at relative path: {output_path}")
        full_path = os.path.join(os.getcwd(), output_path.lstrip("/"))
        print(f"Full path: {full_path}")
    else:
        print("Failed to generate image.")

if __name__ == "__main__":
    test()

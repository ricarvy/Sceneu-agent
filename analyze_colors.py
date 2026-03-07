from PIL import Image
import numpy as np
from collections import Counter

def analyze_colors(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    
    # Flatten
    pixels = arr.reshape(-1, 3)
    
    # Convert to tuples
    pixel_tuples = [tuple(p) for p in pixels]
    
    # Count
    counts = Counter(pixel_tuples)
    
    # Print most common colors
    print("Top 20 colors:")
    for color, count in counts.most_common(20):
        print(f"Color: {color}, Count: {count}")

if __name__ == "__main__":
    analyze_colors("/Users/mico/Documents/trae_projects/Sceneu-agent/template/image.png")

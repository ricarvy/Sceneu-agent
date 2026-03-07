from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects

def analyze_boxes_scipy(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    
    # Masks (refined from analyze_colors)
    # Yellow: High R, High G, Low B (Found: 255, 255, 84)
    # Broaden slightly: R>200, G>200, B<150
    yellow_mask = (arr[:,:,0] > 200) & (arr[:,:,1] > 200) & (arr[:,:,2] < 150)
    
    # Green: Found: 126, 172, 85.
    # Broaden: R in [50, 180], G in [120, 255], B in [50, 150]
    green_mask = (arr[:,:,0] > 50) & (arr[:,:,0] < 180) & (arr[:,:,1] > 120) & (arr[:,:,2] < 150)
    
    # Red: Found: 234, 51, 35.
    # Broaden: R > 200, G < 100, B < 100
    red_mask = (arr[:,:,0] > 200) & (arr[:,:,1] < 100) & (arr[:,:,2] < 100)
    
    # Purple: High R, Low G, High B.
    # R > 100, G < 100, B > 100
    purple_mask = (arr[:,:,0] > 100) & (arr[:,:,1] < 100) & (arr[:,:,2] > 100)
    
    def process_mask(mask, name):
        # Connected components
        labeled_array, num_features = label(mask)
        slices = find_objects(labeled_array)
        
        print(f"\nAnalyzing {name} ({num_features} components)...")
        
        found_any = False
        for i, sl in enumerate(slices):
            if sl is None: continue
            
            # Get slice coordinates
            y_slice, x_slice = sl
            ymin, ymax = y_slice.start, y_slice.stop
            xmin, xmax = x_slice.start, x_slice.stop
            
            height = ymax - ymin
            width = xmax - xmin
            area = height * width
            
            # Filter small noise (e.g. single pixels or thin lines that are just artifacts)
            # Boxes should be significant.
            if area > 500: # Threshold can be tuned
                print(f"  Box {i}: ({xmin}, {ymin}, {xmax}, {ymax}) - W: {width}, H: {height}, Area: {area}")
                found_any = True
        
        if not found_any:
            print("  No significant boxes found.")

    process_mask(yellow_mask, "Yellow")
    process_mask(green_mask, "Green")
    process_mask(red_mask, "Red")
    process_mask(purple_mask, "Purple")

if __name__ == "__main__":
    analyze_boxes_scipy("/Users/mico/Documents/trae_projects/Sceneu-agent/template/image.png")

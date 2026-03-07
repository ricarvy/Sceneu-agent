from PIL import Image
import numpy as np

def find_color_boxes(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    
    # Define color ranges (approximate)
    # Yellow: High R, High G, Low-ish B (Found: 255, 255, 84)
    yellow_mask = (arr[:,:,0] > 200) & (arr[:,:,1] > 200) & (arr[:,:,2] < 150)
    
    # Green: (Found: 126, 172, 85)
    green_mask = (arr[:,:,0] > 50) & (arr[:,:,0] < 180) & (arr[:,:,1] > 120) & (arr[:,:,2] < 120)
    
    # Red: High R, Low G, Low B (Found: 234, 51, 35)
    red_mask = (arr[:,:,0] > 200) & (arr[:,:,1] < 100) & (arr[:,:,2] < 100)
    
    # Purple: High R, Low G, High B
    purple_mask = (arr[:,:,0] > 100) & (arr[:,:,1] < 100) & (arr[:,:,2] > 100)
    
    def get_bounds(mask, name):
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not np.any(rows) or not np.any(cols):
            print(f"No {name} box found")
            return []
        
        # Find contours or connected components would be better, but simple bounding box of all pixels might work if only one box per color
        # For purple, there are likely two boxes.
        
        # Let's verify if we have multiple disjoint regions for purple
        # A simple way is to find min/max y for each scanline?
        # Or just use cv2 if available? No, let's stick to numpy/PIL logic for simplicity if possible.
        # Actually, for purple, since there might be multiple, the simple bounding box will cover all of them.
        # Let's assume the user wants separate boxes.
        
        # Simple clustering for disjoint boxes:
        # Get all (y, x) coordinates
        coords = np.argwhere(mask)
        if len(coords) == 0:
            return []

        # If it's purple, we might want to split.
        # For now, let's just print the global bounds and see if it makes sense.
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        # Heuristic check for multiple boxes: empty rows/cols in between
        # Check rows between rmin and rmax
        sub_rows = rows[rmin:rmax+1]
        empty_rows = np.where(~sub_rows)[0]
        
        boxes = []
        
        if len(empty_rows) > 0 and name == 'purple':
            # Identify split points
            # This is a bit manual. Let's just return the whole bounding box for now and refine if needed.
            # Actually, let's just print coordinates and I'll hardcode them or use them.
            pass
            
        print(f"{name}: ({cmin}, {rmin}, {cmax}, {rmax}) - Width: {cmax-cmin}, Height: {rmax-rmin}")
        return (cmin, rmin, cmax, rmax)

    print(f"Analyzing {image_path}...")
    get_bounds(yellow_mask, "yellow")
    get_bounds(green_mask, "green")
    get_bounds(red_mask, "red")
    get_bounds(purple_mask, "purple")

if __name__ == "__main__":
    find_color_boxes("/Users/mico/Documents/trae_projects/Sceneu-agent/template/image.png")

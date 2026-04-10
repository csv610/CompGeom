import cv2
import numpy as np
from compgeom.mesh.algorithms.image_triangulation import BinaryImageTriangulation

def create_sample_image(path: str):
    # Create a 64x64 black image
    img = np.zeros((64, 64), dtype=np.uint8)
    # Draw a white rectangle
    cv2.rectangle(img, (10, 10), (50, 50), 255, -1)
    # Draw a black square inside the white rectangle (hole)
    cv2.rectangle(img, (20, 20), (40, 40), 0, -1)
    
    cv2.imwrite(path, img)
    print(f"Sample image created at {path}")

def main():
    img_path = "sample_binary.png"
    create_sample_image(img_path)
    
    bit = BinaryImageTriangulation()
    print("Reading image...")
    bit.read_image(img_path)
    print("Cleaning image...")
    bit.clean_image()
    print("Detecting edges...")
    bit.detect_edges()
    print("Creating bounding box...")
    bit.create_bounding_box()
    
    print("Computing triangulations...")
    white_tris, black_tris = bit.compute_triangulations()
    print("Done computing triangulations.")
    
    print(f"White part: {len(white_tris)} triangles")
    print(f"Black part: {len(black_tris)} triangles")
    
    # Save the triangulations as images for verification (optional)
    # We can use our visualize_with_pyvista if we were running interactively,
    # but here we just check the counts.
    
    if len(white_tris) > 0 and len(black_tris) > 0:
        print("Success: Both white and black parts triangulated.")
    else:
        print("Error: One or both parts failed to triangulate.")

if __name__ == "__main__":
    main()

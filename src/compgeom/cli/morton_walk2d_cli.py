import argparse, math
from compgeom.space_filling_curves import SpaceFillingCurves

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=128); parser.add_argument("--height", type=int, default=128)
    args = parser.parse_args()
    side = min(args.width, args.height)
    level = int(math.log2(side)) or 1
    
    print(f"--- 2D Morton (Z-Order) Curve ---\nLevel: {level} ({2**level}x{2**level})")
    path_indices = SpaceFillingCurves.morton(level)
    num_points = len(path_indices)
    
    width = 2**level
    def to_coords(idx):
        return (idx % width, idx // width)
        
    start_p, end_p = to_coords(path_indices[0]), to_coords(path_indices[-1])
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    print(f"\n--- Walk Results ---\nTotal Steps: {num_points-1}\nUnique Cells: {len(set(path_indices))}\nFinal Cell Index: {path_indices[-1]}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()

import argparse, math
from compgeom.space_filling_curves import SpaceFillingCurves

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=81); parser.add_argument("--height", type=int, default=81); parser.add_argument("--level", type=int)
    args = parser.parse_args()
    level = args.level if args.level is not None else (int(math.log(min(args.width, args.height), 3)) or 1)
    
    print(f"--- 2D Peano Curve ---\nLevel: {level} ({3**level}x{3**level})")
    path_indices = SpaceFillingCurves.peano(level)
    num_points = len(path_indices)
    
    # Map index back to coordinates for displacement calculation
    width = 3**level
    def to_coords(idx):
        return (idx % width, idx // width)
    
    start_p, end_p = to_coords(path_indices[0]), to_coords(path_indices[-1])
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    
    print(f"\n--- Walk Results ---\nTotal Steps: {num_points-1}\nUnique Cells: {len(set(path_indices))}\nFinal Cell Index: {path_indices[-1]}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()

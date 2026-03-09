import argparse, math
from compgeom.space_filling_curves import SpaceFillingCurves

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=128); parser.add_argument("--height", type=int, default=128); parser.add_argument("--order", type=int)
    args = parser.parse_args()
    order = args.order if args.order is not None else (int(math.log2(min(args.width, args.height))) or 1)
    
    print(f"--- 2D Hilbert Curve ---\nOrder: {order} ({2**order}x{2**order})")
    path_indices = SpaceFillingCurves.hilbert(order)
    num_points = len(path_indices)
    
    width = 2**order
    def to_coords(idx):
        return (idx % width, idx // width)
        
    start_p, end_p = to_coords(path_indices[0]), to_coords(path_indices[-1])
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    print(f"\n--- Walk Results ---\nTotal Steps: {num_points-1}\nUnique Cells: {len(set(path_indices))}\nFinal Cell Index: {path_indices[-1]}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()

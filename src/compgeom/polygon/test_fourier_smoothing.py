
from compgeom.kernel import Point
from compgeom.polygon import Polygon

def test_fourier_smoothing():
    print("--- Running Fourier Smoothing Tests ---")
    
    # 1. Create a noisy square
    noisy_square = Polygon([
        Point(0,0), Point(5, 0.1), Point(10,0), 
        Point(10.1, 5), Point(10,10), 
        Point(5, 9.9), Point(0,10), 
        Point(-0.1, 5)
    ])
    
    print(f"Original noisy vertices: {len(noisy_square.vertices)}")
    
    # Apply Fourier smoothing
    # With very few harmonics, it should look like a circle/ellipse
    smoothed_3 = noisy_square.fourier_smooth(n_harmonics=2, resample_points=64)
    print(f"Smoothed (3 harmonics) vertices: {len(smoothed_3.vertices)}")
    
    # With more harmonics, it should follow the square better but be smoother
    smoothed_10 = noisy_square.fourier_smooth(n_harmonics=10, resample_points=64)
    print(f"Smoothed (10 harmonics) vertices: {len(smoothed_10.vertices)}")

    # Check that it's still roughly in the same area
    centroid_orig = noisy_square.properties().centroid
    centroid_smooth = smoothed_10.properties().centroid
    print(f"Original centroid: {centroid_orig}")
    print(f"Smoothed centroid: {centroid_smooth}")

    print("--- Tests Completed ---")

if __name__ == "__main__":
    test_fourier_smoothing()

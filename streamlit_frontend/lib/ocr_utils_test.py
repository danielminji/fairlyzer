import os
from io import BytesIO
from PIL import Image
from ocr_utils import highlight_booths_on_map
import random

# Correct path to the map images
MAPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database/seeders/assets/job_fair_maps'))

MAPS = [
    ("jobfairmap.png", [str(i) for i in range(1, 31)], "jobfairmap"),
    ("jobfairmap2.png", [str(i) for i in range(1, 4)], "jobfairmap2"),
]

LIB_DIR = os.path.dirname(os.path.abspath(__file__))

def print_all_boxes(map_filename):
    map_path = os.path.join(MAPS_DIR, map_filename)
    print(f"\n[DEBUG] Printing all detected booth boxes for {map_filename}")
    with open(map_path, "rb") as f:
        image_bytes = BytesIO(f.read())
    import ocr_utils
    pil_image = Image.open(image_bytes).convert("RGB")
    cv_img = __import__('cv2').cvtColor(__import__('numpy').array(pil_image), __import__('cv2').COLOR_RGB2BGR)
    booth_boxes = ocr_utils.detect_booth_rectangles(cv_img)
    for i, box in enumerate(booth_boxes):
        print(f"Box {i}: {box}")

def run_test(map_filename, booth_numbers, debug_name, out_prefix="highlighted_"):
    map_path = os.path.join(MAPS_DIR, map_filename)
    out_dir = os.path.dirname(__file__)
    out_path = os.path.join(out_dir, f"{out_prefix}{debug_name}.png")
    print(f"[TEST] Saving highlighted map to {out_path}")
    # --- Use the correct debug_name for cache ---
    if "jobfairmap2" in map_filename or len(booth_numbers) <= 3:
        cache_debug_name = "all_3"
    else:
        cache_debug_name = "all_30"
    img = highlight_booths_on_map(map_path, booth_numbers, debug_name=cache_debug_name, out_dir=out_dir)
    img.save(out_path)
    print(f"[TEST] Saved highlighted map to {out_path}")

def run_full_detection_test(map_filename, booth_range, out_prefix="highlighted_all_"):
    all_booths = [str(i) for i in booth_range]
    debug_name = "jobfairmap" if "jobfairmap" in map_filename else "jobfairmap2"
    print(f"\n[Full Detection Test] Testing all booths: {all_booths}")
    run_test(map_filename, all_booths, debug_name, out_prefix=out_prefix)

def main():
    print_all_boxes("jobfairmap.png")
    # Test: highlight 7 random booths in the 30-booth map
    all_booths_30 = [str(i) for i in range(1, 31)]
    random.seed(42)
    selected_booths_30 = random.sample(all_booths_30, 7)
    print(f"\n[Selected Booths Test - 30 Booth] Highlighting only these booths: {selected_booths_30}")
    run_test("jobfairmap.png", selected_booths_30, "jobfairmap_selected_custom", out_prefix="highlighted_selected_")
    # Test: highlight 2 different booths in the 3-booth map
    all_booths_3 = ["1", "2", "3"]
    selected_booths_3 = random.sample(all_booths_3, 2)
    print(f"\n[Selected Booths Test - 3 Booth] Highlighting only these booths: {selected_booths_3}")
    run_test("jobfairmap2.png", selected_booths_3, "jobfairmap2_selected_custom", out_prefix="highlighted_selected_")

if __name__ == "__main__":
    import time
    # Highlight all booths for 30-booth layout
    map_path_30 = os.path.join(os.path.dirname(__file__), "..", "..", "database", "seeders", "assets", "job_fair_maps", "jobfairmap.png")
    booth_numbers_30 = [str(i) for i in range(1, 31)]
    with open(map_path_30, "rb") as f:
        image_bytes_30 = BytesIO(f.read())
    print(f"Testing map: {map_path_30} with all booths: {booth_numbers_30}")
    start_30 = time.time()
    highlighted_30 = highlight_booths_on_map(image_bytes_30, booth_numbers_30, test_mode=True, debug_name="all_30")
    end_30 = time.time()
    out_path_30 = os.path.join(os.path.dirname(__file__), f"highlighted_all_30.png")
    highlighted_30.save(out_path_30)
    print(f"Saved highlighted map to {out_path_30} (Time: {end_30 - start_30:.2f}s)")

    # Highlight all booths for 3-booth layout
    map_path_3 = os.path.join(os.path.dirname(__file__), "..", "..", "database", "seeders", "assets", "job_fair_maps", "jobfairmap2.png")
    booth_numbers_3 = [str(i) for i in range(1, 4)]
    with open(map_path_3, "rb") as f:
        image_bytes_3 = BytesIO(f.read())
    print(f"Testing map: {map_path_3} with all booths: {booth_numbers_3}")
    start_3 = time.time()
    highlighted_3 = highlight_booths_on_map(image_bytes_3, booth_numbers_3, test_mode=True, debug_name="all_3")
    end_3 = time.time()
    out_path_3 = os.path.join(os.path.dirname(__file__), f"highlighted_all_3.png")
    highlighted_3.save(out_path_3)
    print(f"Saved highlighted map to {out_path_3} (Time: {end_3 - start_3:.2f}s)")

    # --- New: Test recommendation-driven highlighting ---
    # 30-booth: [1,2,8,15,16,14,21]
    recommended_30 = ["1", "2", "8", "15", "16", "14", "21"]
    print(f"Testing map: {map_path_30} with recommended booths: {recommended_30}")
    highlighted_recommended_30 = highlight_booths_on_map(image_bytes_30, recommended_30, test_mode=True, debug_name="all_30")
    out_path_recommended_30 = os.path.join(os.path.dirname(__file__), f"highlighted_recommended_30.png")
    highlighted_recommended_30.save(out_path_recommended_30)
    print(f"Saved highlighted map to {out_path_recommended_30}")

    # 3-booth: [1,3]
    recommended_3 = ["1", "3"]
    print(f"Testing map: {map_path_3} with recommended booths: {recommended_3}")
    highlighted_recommended_3 = highlight_booths_on_map(image_bytes_3, recommended_3, test_mode=True, debug_name="all_3")
    out_path_recommended_3 = os.path.join(os.path.dirname(__file__), f"highlighted_recommended_3.png")
    highlighted_recommended_3.save(out_path_recommended_3)
    print(f"Saved highlighted map to {out_path_recommended_3}") 
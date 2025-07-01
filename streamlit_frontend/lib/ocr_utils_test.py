import os
from io import BytesIO
from PIL import Image
from ocr_utils import highlight_booths_on_map

# Paths to the map images
MAPS = [
    ("jobfairmap.png", [str(i) for i in range(1, 31)], "jobfairmap"),
    ("jobfairmap2.png", [str(i) for i in range(1, 4)], "jobfairmap2"),
]

LIB_DIR = os.path.dirname(os.path.abspath(__file__))

def run_test(map_filename, booth_numbers, debug_name, out_prefix="highlighted_"):
    map_path = os.path.join(LIB_DIR, map_filename)
    print(f"Testing map: {map_path} with booths: {booth_numbers}")
    with open(map_path, "rb") as f:
        image_bytes = BytesIO(f.read())
    from ocr_utils import highlight_booths_on_map
    result_img = highlight_booths_on_map(image_bytes, booth_numbers, test_mode=True, debug_name=debug_name)

def run_full_detection_test(map_filename, booth_range, out_prefix="highlighted_all_"):
    all_booths = [str(i) for i in booth_range]
    debug_name = "jobfairmap" if "jobfairmap" in map_filename else "jobfairmap2"
    print(f"\n[Full Detection Test] Testing all booths: {all_booths}")
    run_test(map_filename, all_booths, debug_name, out_prefix=out_prefix)

def main():
    for map_filename, booth_numbers, debug_name in MAPS:
        run_test(map_filename, booth_numbers, debug_name)
    # After current tests, run full detection for all possible booths
    run_full_detection_test("jobfairmap.png", range(1, 31))
    run_full_detection_test("jobfairmap2.png", range(1, 4))

if __name__ == "__main__":
    main() 
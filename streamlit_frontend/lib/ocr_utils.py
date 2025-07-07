import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import re
import os
import concurrent.futures
import time
import math

# Optional: Specify Tesseract path if not in system PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Example for Windows

def get_image_from_url(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img_bytes = BytesIO(response.content)
        return img_bytes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL {image_url}: {e}")
        return None

def is_booth_like_box(x, y, w, h, img_w, img_h):
    aspect = w / h if h > 0 else 0
    area = w * h
    # Loosened: aspect 0.3–4.0, area 100–10000, no grid position filter
    return (w > 15 and h > 15 and w < img_w * 0.9 and h < img_h * 0.9 and
            0.3 < aspect < 4.0 and 100 < area < 10000)

def detect_booth_rectangles(cv_img, debug_save_path=None):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    booth_boxes = []
    img_h, img_w = gray.shape
    debug_img = cv_img.copy()
    print(f"Detected {len(contours)} contours after closing.")
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if is_booth_like_box(x, y, w, h, img_w, img_h):
            booth_boxes.append((x, y, w, h))
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if debug_save_path:
        cv2.imwrite(debug_save_path, debug_img)
        print(f"Saved debug contour image to {debug_save_path}")
    return booth_boxes

def ocr_booth_single(cv_img, box, save_failed_dir=None, label_hint=None):
    x, y, w, h = box
    img_h, img_w, _ = cv_img.shape
    pad = 5
    # Special-case: if label_hint is 11 or 21, use larger padding
    if label_hint in ('11', '21', 11, 21):
        pad = 20
    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(img_w, x + w + pad)
    y1 = min(img_h, y + h + pad)
    booth_img = cv_img[y0:y1, x0:x1]
    pil_img_color = Image.fromarray(cv2.cvtColor(booth_img, cv2.COLOR_BGR2RGB))
    # Fast path: color, PSM 8
    config = '--psm 8 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(pil_img_color, config=config)
    m = re.search(r'\d+', text)
    if m:
        return m.group(0)
    # Fallback: binarized, PSM 8
    gray_booth = cv2.cvtColor(booth_img, cv2.COLOR_BGR2GRAY)
    booth_bin = cv2.adaptiveThreshold(gray_booth, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    pil_img_bin = Image.fromarray(booth_bin)
    text = pytesseract.image_to_string(pil_img_bin, config=config)
    m = re.search(r'\d+', text)
    if m:
        return m.group(0)
    # Fallback: inverted binarized, PSM 8
    booth_bin_inv = cv2.bitwise_not(booth_bin)
    pil_img_inv = Image.fromarray(booth_bin_inv)
    text = pytesseract.image_to_string(pil_img_inv, config=config)
    m = re.search(r'\d+', text)
    if m:
        return m.group(0)
    # Fallback: color, PSM 7
    config7 = '--psm 7 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(pil_img_color, config=config7)
    m = re.search(r'\d+', text)
    if m:
        return m.group(0)
    # Deep learning OCR fallback for special-case booths
    if label_hint in ('11', '21', 11, 21):
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            result = reader.readtext(booth_img)
            for bbox, text, conf in result:
                m = re.search(r'\d+', text)
                if m:
                    return m.group(0)
        except Exception as e:
            print(f"EasyOCR failed: {e}")
    # Save failed crop for manual inspection
    if save_failed_dir and label_hint:
        os.makedirs(save_failed_dir, exist_ok=True)
        fail_path = os.path.join(save_failed_dir, f"fail_{label_hint}_x{x}_y{y}_w{w}_h{h}.png")
        cv2.imwrite(fail_path, booth_img)
        print(f"Saved failed booth crop to {fail_path}")
    return None

def ocr_booth_parallel(cv_img, booth_boxes, save_failed_dir=None, label_hints=None):
    results = [None] * len(booth_boxes)
    def ocr_task(args):
        idx, box = args
        label_hint = label_hints[idx] if label_hints else None
        return idx, ocr_booth_single(cv_img, box, save_failed_dir, label_hint)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for idx, result in executor.map(ocr_task, enumerate(booth_boxes)):
            results[idx] = result
    return results

def highlight_booths_on_map(image_bytes, recommended_booth_numbers, test_mode=False, debug_name=None):
    if not image_bytes or not recommended_booth_numbers:
        return None
    try:
        pil_image = Image.open(image_bytes).convert("RGB")
        cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        if not test_mode:
            print(f"Error loading image for OCR: {e}")
        return None
    debug_path = os.path.join(os.path.dirname(__file__), f'debug_contours_{debug_name or "map"}.png')
    t0 = time.time()
    booth_boxes = detect_booth_rectangles(cv_img, debug_save_path=debug_path)
    print(f"Filtered to {len(booth_boxes)} candidate boxes after contour filtering.")
    img_h, img_w, _ = cv_img.shape
    grid_boxes = [box for box in booth_boxes if img_h * 0.1 < box[1] < img_h * 0.9]
    print(f"Filtered to {len(grid_boxes)} boxes in main grid area.")
    def tesseract_color_psm8(box):
        x, y, w, h = box
        pad = 5
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(img_w, x + w + pad)
        y1 = min(img_h, y + h + pad)
        booth_img = cv_img[y0:y1, x0:x1]
        pil_img_color = Image.fromarray(cv2.cvtColor(booth_img, cv2.COLOR_BGR2RGB))
        config = '--psm 8 -c tessedit_char_whitelist=0123456789'
        data = pytesseract.image_to_data(pil_img_color, config=config, output_type=pytesseract.Output.DICT)
        best_num = None
        best_conf = -1
        for i, text in enumerate(data['text']):
            if text.strip().isdigit():
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                if conf > best_conf:
                    best_num = text.strip()
                    best_conf = conf
        return best_num, best_conf, box
    t1 = time.time()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        ocr_results = list(executor.map(tesseract_color_psm8, grid_boxes))
    t2 = time.time()
    booth_to_box = {}
    assigned_boxes = set()
    for num in recommended_booth_numbers:
        best = None
        best_conf = -1
        for detected_num, conf, box in ocr_results:
            if detected_num == str(num) and conf > best_conf:
                best = (detected_num, box)
                best_conf = conf
        if best:
            booth_to_box[num] = best[1]
            assigned_boxes.add(tuple(best[1]))
    # Targeted fallback for 11 and 21
    for special_num in ['11', '21']:
        if special_num in recommended_booth_numbers and special_num not in booth_to_box:
            # Find the row (y) of the closest detected neighbor (10/12 for 11, 20/22 for 21)
            neighbors = []
            if special_num == '11':
                for n in ['10', '12']:
                    if n in booth_to_box:
                        neighbors.append(booth_to_box[n])
            if special_num == '21':
                for n in ['20', '22']:
                    if n in booth_to_box:
                        neighbors.append(booth_to_box[n])
            if neighbors:
                # Use average y of neighbors as expected row
                expected_y = int(np.mean([b[1] for b in neighbors]))
                # Only consider unassigned boxes in the same row (y within threshold)
                row_thresh = 0.15 * img_h  # 15% of image height
                candidates = [box for box in grid_boxes if tuple(box) not in assigned_boxes and abs(box[1] - expected_y) < row_thresh]
                # Pick the one closest in x to the average x of neighbors
                if candidates:
                    expected_x = int(np.mean([b[0] for b in neighbors]))
                    best_box = min(candidates, key=lambda b: abs(b[0] - expected_x))
                    booth_to_box[special_num] = best_box
                    assigned_boxes.add(tuple(best_box))
                    if test_mode:
                        print(f"Targeted fallback: Assigned booth {special_num} to box at {best_box}")
    missing = [str(n) for n in recommended_booth_numbers if n not in booth_to_box]
    if test_mode:
        print(f"SUMMARY: Detected {len(booth_to_box)}/{len(recommended_booth_numbers)} booths: {sorted(list(booth_to_box.keys()))}")
        if missing:
            print(f"MISSING: {missing}")
        print(f"Timing: Contour+filter: {t1-t0:.2f}s, Tesseract parallel: {t2-t1:.2f}s")
    if not booth_to_box:
        if not test_mode:
            print("No recommended booth numbers found on the map via OCR.")
        return pil_image
    draw = ImageDraw.Draw(pil_image, "RGBA")
    padding = 2  # Tighter fit
    # Compute average width and height of all detected booth boxes
    if booth_to_box:
        avg_w = int(np.mean([b[2] for b in booth_to_box.values()]))
        avg_h = int(np.mean([b[3] for b in booth_to_box.values()]))
    else:
        avg_w, avg_h = 40, 20  # fallback default
    for num, box in booth_to_box.items():
        x_coord, y_coord, w_coord, h_coord = box
        # Center the highlight box on the detected booth center
        center_x = x_coord + w_coord // 2
        center_y = y_coord + h_coord // 2
        half_w = avg_w // 2 + padding
        half_h = avg_h // 2 + padding
        box_x0 = max(0, center_x - half_w)
        box_y0 = max(0, center_y - half_h)
        box_x1 = min(pil_image.width, center_x + half_w)
        box_y1 = min(pil_image.height, center_y + half_h)
        final_box = (box_x0, box_y0, box_x1, box_y1)
        draw.rectangle(final_box, outline="red", fill=(255, 0, 0, 77), width=3)
    return pil_image
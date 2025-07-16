import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os
import json
import sys

def highlight_booths_on_map(image_bytes, recommended_booth_numbers, test_mode=False, debug_name=None):
    if not image_bytes or not recommended_booth_numbers:
        return None
    try:
        pil_image = Image.open(image_bytes).convert("RGB")
        cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        draw = ImageDraw.Draw(pil_image)
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
    # Detect rectangles (booths)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    img_h, img_w = gray.shape
    booth_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / h if h > 0 else 0
        area = w * h
        if w > 15 and h > 15 and w < img_w * 0.9 and h < img_h * 0.9 and 0.3 < aspect < 4.0 and 100 < area < 10000:
            booth_boxes.append((x, y, w, h))
    booth_boxes = sorted(booth_boxes, key=lambda b: (b[1], b[0]))
    # --- Load or create cache ---
    cache_file = os.path.join(os.path.dirname(__file__), f'ocr_psm_cache_{debug_name or "map"}.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            booth_cache = json.load(f)
    else:
        booth_cache = {}
    # --- Enhanced OCR for each detected rectangle with debug ---
    def ocr_all_strategies_debug(booth_img, booth_num, rect):
        results = []
        pil_img_color = Image.fromarray(cv2.cvtColor(booth_img, cv2.COLOR_BGR2RGB))
        gray_booth = cv2.cvtColor(booth_img, cv2.COLOR_BGR2GRAY)
        booth_bin = cv2.adaptiveThreshold(gray_booth, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        pil_img_bin = Image.fromarray(booth_bin)
        pil_img_bin_resized = pil_img_bin.resize((pil_img_bin.width*2, pil_img_bin.height*2), Image.BICUBIC)
        denoised = cv2.fastNlMeansDenoising(gray_booth, None, 30, 7, 21)
        pil_img_denoised = Image.fromarray(denoised)
        pil_img_sharp = pil_img_color.filter(ImageFilter.SHARPEN)
        pil_img_contrast = pil_img_color.point(lambda p: min(255, int(p*1.5)))
        pil_img_invert = Image.fromarray(255 - np.array(pil_img_bin))
        variants = [
            ("color", pil_img_color),
            ("bin", pil_img_bin),
            ("bin_resized", pil_img_bin_resized),
            ("denoised", pil_img_denoised),
            ("sharp", pil_img_sharp),
            ("contrast", pil_img_contrast),
            ("invert", pil_img_invert)
        ]
        psm_modes = [3, 4, 6, 7, 8, 10, 11, 12, 13]
        for variant_name, img in variants:
            for psm in psm_modes:
                config = f'--psm {psm} -c tessedit_char_whitelist=0123456789'
                text = pytesseract.image_to_string(img, config=config)
                text = text.strip().replace('\n', '').replace(' ', '')
                print(f"[DEBUG] Booth {booth_num} Rect {rect} Variant {variant_name} PSM {psm} -> '{text}'")
                if text.isdigit():
                    results.append((text, variant_name, psm))
        for text, variant_name, psm in results:
            if text == str(booth_num):
                print(f"[MATCH] Booth {booth_num} found at {rect} with variant {variant_name} and PSM {psm}")
                return text
        return None
    # --- Assignment logic: Use cache if available, OCR otherwise ---
    booth_to_rect = {}
    used_rects = set()
    # 1. Use cached coordinates for recommended booths if available
    for num in recommended_booth_numbers:
        num_str = str(num)
        coords = booth_cache.get(num_str, [])
        if coords:
            box = tuple(coords)
            booth_to_rect[num_str] = box
            used_rects.add(box)
            print(f"[CACHE] Booth {num} at {box}")
    # 2. For remaining booths, run OCR and only draw if a new, confident coordinate is found
    for num in recommended_booth_numbers:
        num_str = str(num)
        coords = booth_cache.get(num_str, [])
        if coords:
            continue  # Already in cache
        found = False
        for box in booth_boxes:
            if box in used_rects:
                continue
            x, y, w, h = box
            pad = 5
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(img_w, x + w + pad)
            y1 = min(img_h, y + h + pad)
            booth_img = cv_img[y0:y1, x0:x1]
            detected_num = ocr_all_strategies_debug(booth_img, num_str, box)
            if detected_num == num_str:
                booth_to_rect[num_str] = box
                booth_cache[num_str] = list(box)
                used_rects.add(box)
                found = True
                print(f"[NEW] Booth {num} at {box}")
                break
        if not found:
            print(f"[MISSING] Booth {num} not found by OCR or cache")
            booth_cache[num_str] = []
            # Optionally save the crop for manual inspection
            try:
                crop_dir = os.path.join(os.path.dirname(__file__), 'debug_crops')
                os.makedirs(crop_dir, exist_ok=True)
                crop_path = os.path.join(crop_dir, f'booth_{num_str}_crop.png')
                Image.fromarray(cv_img[y0:y1, x0:x1]).save(crop_path)
            except Exception as e:
                print(f"[DEBUG] Could not save crop for booth {num_str}: {e}")
    # Draw highlights only for recommended booths that are in the cache or newly detected
    for num in recommended_booth_numbers:
        num_str = str(num)
        if num_str in booth_to_rect:
            x, y, w, h = booth_to_rect[num_str]
            draw.rectangle([x, y, x+w, y+h], outline=(255,0,0), fill=(255,200,200), width=4)
            font_size = max(16, int(h * 0.5))
            try:
                font = ImageFont.truetype("arial.ttf", size=font_size)
            except:
                font = ImageFont.load_default()
            text = str(num)
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except AttributeError:
                text_w, text_h = draw.textsize(text, font=font)
            text_x = x + (w - text_w) // 2
            text_y = y + (h - text_h) // 2
            draw.text((text_x, text_y), text, fill=(0,0,0), font=font)
    # Save updated cache
    with open(cache_file, 'w') as f:
        json.dump(booth_cache, f, indent=2)
    return pil_image
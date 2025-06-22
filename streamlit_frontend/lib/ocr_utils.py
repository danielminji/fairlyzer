import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw
import requests
from io import BytesIO

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

def highlight_booths_on_map(image_bytes, recommended_booth_numbers):
    """
    Detects booth numbers on a map image using OCR and highlights the recommended ones.

    Args:
        image_bytes (BytesIO): The job fair map image in bytes.
        recommended_booth_numbers (list): A list of strings representing the booth numbers to highlight.

    Returns:
        PIL.Image: The image with recommended booths highlighted, or the original image if errors occur.
                   Returns None if the input image cannot be processed.
    """
    if not image_bytes or not recommended_booth_numbers:
        return None

    try:
        pil_image = Image.open(image_bytes).convert("RGB")
        opencv_image = np.array(pil_image)
        # Convert RGB to BGR for OpenCV
        opencv_image = opencv_image[:, :, ::-1].copy()
    except Exception as e:
        print(f"Error loading image for OCR: {e}")
        return None # Return None if image loading fails

    # Preprocessing (optional, but can improve OCR)
    gray_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # --- Experimental: Dilate the image slightly to thicken characters --- 
    kernel = np.ones((2,2),np.uint8) # REVERTED to (2,2) DILATION KERNEL
    dilated_image = cv2.dilate(thresh_image, kernel, iterations = 1)
    # --- End Experimental Dilation ---

    cv2.imwrite("debug_ocr_input_map_dilated.png", dilated_image) # DEBUG: Save the DILATED image
    print("DEBUG: Saved DILATED thresh_image as debug_ocr_input_map_dilated.png")
    # cv2.imwrite("debug_ocr_input_NO_DILATION.png", dilated_image) # DEBUG: Save the NON-DILATED image
    # print("DEBUG: Saved NON-DILATED thresh_image as debug_ocr_input_NO_DILATION.png")
    # Could add more: noise removal, scaling, etc.

    found_booth_boxes = []
    
    try:
        # Use pytesseract to get detailed data including bounding boxes
        tesseract_config = '--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789' # REVERTED to PSM 11
        ocr_data = pytesseract.image_to_data(dilated_image, output_type=pytesseract.Output.DICT, config=tesseract_config)
        
        n_boxes = len(ocr_data['level'])
        print(f"OCR: Found {n_boxes} potential text boxes. Iterating...") 

        raw_detections = []
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            # Log everything Tesseract sees above a very low confidence for debugging
            # print(f"OCR Raw Detect (conf > 0): '{text}' at ({ocr_data['left'][i]},{ocr_data['top'][i]},{ocr_data['width'][i]},{ocr_data['height'][i]}) conf: {conf}") #生产环境下注释掉
            
            # Store reasonably confident raw detections for matching logic
            if conf > 30 and text: # Minimum confidence for considering a piece for matching
                raw_detections.append({
                    "text": text,
                    "box": (ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]),
                    "conf": conf
                })

        # Logic to match recommended_booth_numbers
        for rec_num_str in recommended_booth_numbers:
            rec_num_str = str(rec_num_str) # Ensure it's a string
            found_match_for_this_rec_num = False

            # Attempt 1: Direct match for the recommended number
            for detection in raw_detections:
                if detection["text"] == rec_num_str and detection["conf"] > 50:
                    x, y, w, h = detection["box"]
                    existing_entry = next((fb for fb in found_booth_boxes if fb["text"] == detection["text"] and fb["box"] == (x,y,w,h)), None)
                    if not existing_entry:
                        found_booth_boxes.append({
                            "text": detection["text"],
                            "box": (x, y, w, h) 
                        })
                        print(f"OCR DIRECT MATCH & Kept: '{detection['text']}' at ({x},{y},{w},{h}) conf: {detection['conf']}")
                    found_match_for_this_rec_num = True
                    break 
            
            if found_match_for_this_rec_num:
                continue

            # Attempt 2: Combination logic for two-digit numbers if not directly found
            if len(rec_num_str) == 2 and not found_match_for_this_rec_num:
                digit1_char = rec_num_str[0]
                digit2_char = rec_num_str[1]

                possible_d1s = [d for d in raw_detections if d["text"] == digit1_char and d["conf"] > 40]
                possible_d2s = [d for d in raw_detections if d["text"] == digit2_char and d["conf"] > 40]

                for d1 in possible_d1s:
                    d1_x, d1_y, d1_w, d1_h = d1["box"]
                    d1_center_y = d1_y + d1_h / 2
                    d1_right_edge = d1_x + d1_w

                    for d2 in possible_d2s:
                        if d1 == d2: continue 
                        d2_x, d2_y, d2_w, d2_h = d2["box"]
                        d2_center_y = d2_y + d2_h / 2

                        max_horizontal_gap_abs = d1_w * 0.6 
                        max_vertical_offset_abs = d1_h * 0.5 
                        
                        horizontal_gap = d2_x - d1_right_edge
                        vertical_offset = abs(d1_center_y - d2_center_y)

                        if (d2_x > d1_x and 
                            horizontal_gap >= -(d1_w * 0.3) and 
                            horizontal_gap < max_horizontal_gap_abs and 
                            vertical_offset < max_vertical_offset_abs):
                            
                            combined_x = d1_x
                            combined_y = min(d1_y, d2_y)
                            combined_w = (d2_x + d2_w) - d1_x 
                            combined_h = max(d1_y + d1_h, d2_y + d2_h) - combined_y 

                            print(f"OCR COMBINED MATCH for '{rec_num_str}': Found '{d1['text']}' and '{d2['text']}' nearby. Combined Box: ({combined_x},{combined_y},{combined_w},{combined_h})")
                            found_booth_boxes.append({
                                "text": rec_num_str, 
                                "box": (combined_x, combined_y, combined_w, combined_h)
                            })
                            found_match_for_this_rec_num = True
                            break 
                    if found_match_for_this_rec_num:
                        break 

            # ATTEMPT 3: Heuristic for specific problematic two-digit numbers where the first digit might be "eaten"
            if len(rec_num_str) == 2 and not found_match_for_this_rec_num:
                first_digit_of_rec = rec_num_str[0]
                second_digit_of_rec = rec_num_str[1]

                if first_digit_of_rec == '1':
                    possible_lone_second_digits = [
                        d for d in raw_detections
                        if d["text"] == second_digit_of_rec and d["conf"] > 70 
                    ]
                    # print(f"DEBUG Attempt 3: For rec_num '{rec_num_str}', possible_lone_second_digits: {possible_lone_second_digits}") #生产环境下注释掉

                    for lone_d2_detection in possible_lone_second_digits:
                        d2_x, d2_y, d2_w, d2_h = lone_d2_detection["box"]
                        # print(f"DEBUG Attempt 3: Checking lone '{lone_d2_detection['text']}' (w:{d2_w}, h:{d2_h}) for rec_num '{rec_num_str}'") #生产环境下注释掉

                        if d2_w > (d2_h * 0.8): 
                            print(f"OCR HEURISTIC (Attempt 3) for '{rec_num_str}': Found lone '{lone_d2_detection['text']}' (conf {lone_d2_detection['conf']}) with wide box (w:{d2_w}, h:{d2_h}). Assuming it's {rec_num_str}.")
                            found_booth_boxes.append({
                                "text": rec_num_str,
                                "box": (d2_x, d2_y, d2_w, d2_h) 
                            })
                            found_match_for_this_rec_num = True
                            break 
            
            # End of ATTEMPT 3
        # --- All highlighting logic is now conditional on recommended_booth_numbers ---

    except pytesseract.TesseractNotFoundError:
        print("Tesseract is not installed or not in your PATH.")
        return pil_image # Return original image
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return pil_image # Return original image on other OCR errors

    if not found_booth_boxes:
        print("No recommended booth numbers found on the map via OCR.")
        return pil_image # Return original if nothing found or to highlight

    # Draw highlights on the original PIL image
    draw = ImageDraw.Draw(pil_image, "RGBA") # Use RGBA for semi-transparent highlights

    padding = 10 # INCREASED PADDING

    for item in found_booth_boxes:
        # item["box"] is (x, y, width, height)
        x_coord, y_coord, w_coord, h_coord = item["box"]

        # Convert to (x0, y0, x1, y1) for Pillow, where (x1,y1) is bottom-right
        box_x0 = x_coord
        box_y0 = y_coord
        box_x1 = x_coord + w_coord
        box_y1 = y_coord + h_coord

        # Add padding, ensuring coordinates stay within image bounds
        img_width, img_height = pil_image.size
        padded_x0_for_pillow = max(0, box_x0 - padding)
        padded_y0_for_pillow = max(0, box_y0 - padding)
        padded_x1_for_pillow = min(img_width, box_x1 + padding)
        padded_y1_for_pillow = min(img_height, box_y1 + padding)
        
        # Ensure x1 >= x0 and y1 >= y0 after padding to prevent Pillow error
        # This can happen if width/height is very small and padding is large
        if padded_x1_for_pillow < padded_x0_for_pillow:
            padded_x1_for_pillow = padded_x0_for_pillow 
        if padded_y1_for_pillow < padded_y0_for_pillow:
            padded_y1_for_pillow = padded_y0_for_pillow

        final_padded_box_for_pillow = (padded_x0_for_pillow, padded_y0_for_pillow, padded_x1_for_pillow, padded_y1_for_pillow)

        # Draw a semi-transparent rectangle
        draw.rectangle(final_padded_box_for_pillow, outline="red", fill=(255, 0, 0, 70), width=3)
        
        # Optionally, draw the detected text again (e.g., if preprocessing made it hard to see)
        # draw.text((box[0], box[1] - 10), item["text"], fill="red")

    return pil_image 
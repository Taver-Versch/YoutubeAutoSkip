import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab
import os
import subprocess


def find_tesseract():
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME')),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'tesseract'
    except:
        pass

    return None


tesseract_path = find_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")


def screenshot_region(region):
    try:
        x, y, width, height = region
        bbox = (x, y, x + width, y + height)
        img = ImageGrab.grab(bbox=bbox, all_screens=True)
        img_array = np.array(img)
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Screenshot error: {e}")
        return None


def preprocess_image(img):
    if img is None:
        return []

    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        processed_images = []

        thresh1 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        processed_images.append(thresh1)

        thresh2 = cv2.bitwise_not(thresh1)
        processed_images.append(thresh2)

        _, thresh3 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(thresh3)

        _, thresh4 = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        processed_images.append(thresh4)

        return processed_images
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return []


def find_skip_button(img, search_text="skip"):
    if img is None or not tesseract_path:
        return None

    try:
        processed_images = preprocess_image(img)
        if not processed_images:
            return None

        custom_config = r'--oem 3 --psm 11'
        search_lower = search_text.lower()

        for processed in processed_images:
            try:
                text_data = pytesseract.image_to_string(processed, config=custom_config)

                if search_lower in text_data.lower():
                    data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT,
                                                     config=custom_config)

                    for i, word in enumerate(data["text"]):
                        if word and search_lower in word.lower():
                            x = data["left"][i] + data["width"][i] // 2
                            y = data["top"][i] + data["height"][i] // 2
                            return (x, y)
            except:
                continue

        return None
    except Exception as e:
        print(f"OCR error: {e}")
        return None


def click_button(region, button_coords):
    if button_coords:
        try:
            screen_x = region[0] + button_coords[0]
            screen_y = region[1] + button_coords[1]
            pyautogui.click(screen_x, screen_y)
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    return False

# Set environment variables to disable GUI libraries before importing
import os
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Disable Qt GUI
os.environ['MPLBACKEND'] = 'Agg'  # Use non-interactive backend for matplotlib

try:
    from ultralytics import YOLO
    print("✅ ultralytics imported successfully")
except Exception as e:
    print(f"❌ Failed to import ultralytics: {e}")
    import traceback
    traceback.print_exc()
    YOLO = None

try:
    from PIL import Image
    print("✅ PIL imported successfully")
except Exception as e:
    print(f"❌ Failed to import PIL: {e}")
    Image = None

import io
import json
import os

class YOLOFoodDetector:
    def __init__(self, model_path=None):
        # Use environment variable if set, otherwise default to yolov8m.pt
        if model_path is None:
            model_path = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
        self.model = None

        if YOLO is None:
            raise RuntimeError("❌ CRITICAL: YOLO not installed. Real food detection is REQUIRED.")

        try:
            print(f"🚀 Loading YOLO model: {model_path}")
            self.model = YOLO(model_path)
            print(f"✅ YOLO model loaded successfully")
            print(f"📊 Model classes: {len(self.model.names)} - {list(self.model.names.values())[:10]}...")
        except Exception as e:
            raise RuntimeError(f"❌ CRITICAL: YOLO model loading failed: {e}. Real food detection is REQUIRED.")

    def detect_food(self, image_file):
        # YOLO is required - no fallbacks allowed
        if self.model is None:
            raise RuntimeError("❌ CRITICAL: YOLO model not loaded. Real food detection is REQUIRED.")

        try:
            image = Image.open(image_file).convert('RGB')
            results = self.model.predict(image, conf=0.15)

            detected_items = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)
                    class_name = result.names[class_id]

                    # Map generic YOLO names to food names
                    food_name = self._map_to_food_name(class_name, confidence)

                    detected_items.append({
                        'name': food_name,
                        'confidence': round(confidence, 2),
                        'bbox': box.xyxy[0].tolist()
                    })

            return {
                'success': True,
                'detected_items': detected_items,
                'confidence_score': max([item['confidence'] for item in detected_items], default=0)
            }
        except Exception as e:
            raise RuntimeError(f"❌ CRITICAL: Food detection failed: {e}. Real detection is REQUIRED.")

    def _map_to_food_name(self, generic_name, confidence):
        """Map generic YOLO class names to food names"""
        # Common fruit/food mappings from COCO dataset
        food_mappings = {
            # Bananas - often detected as various yellow objects
            'banana': 'Banana',
            'yellow': 'Banana',
            'stick': 'Banana',
            'sports ball': 'Banana',

            # Apples - often detected as small round fruit-like objects
            'apple': 'Apple',
            'orange': 'Apple',  # Color confusion
            'ball': 'Apple',
            'fruit': 'Apple',

            # Oranges - detected as round orange objects
            'orange': 'Orange',
            'tennis ball': 'Orange',
            'sphere': 'Orange',

            # Common vegetables
            'carrot': 'Carrot',
            'broccoli': 'Broccoli',
            'lettuce': 'Lettuce',
            'tomato': 'Tomato',
            'potato': 'Potato',

            # Common proteins
            'chicken': 'Chicken',
            'meat': 'Meat',
            'fish': 'Fish',
            'sandwich': 'Sandwich',
            'pizza': 'Pizza',
        }

        generic_lower = generic_name.lower()

        # Direct match
        if generic_lower in food_mappings:
            return food_mappings[generic_lower]

        # Partial match
        for key, value in food_mappings.items():
            if key in generic_lower or generic_lower in key:
                return value

        # Fallback: return original if no mapping found
        return generic_name

yolo_detector = YOLOFoodDetector()

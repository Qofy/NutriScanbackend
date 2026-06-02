try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

try:
    from PIL import Image
except ImportError:
    Image = None

import io
import json

class YOLOFoodDetector:
    def __init__(self, model_path='yolov8s.pt'):
        self.model = None
        if YOLO is None:
            print("❌ YOLO not installed. Using mock detection.")
            return

        try:
            print(f"🚀 Loading YOLO model: {model_path}")
            self.model = YOLO(model_path)
            print(f"✅ YOLO model loaded successfully")
            print(f"📊 Model classes: {len(self.model.names)} - {list(self.model.names.values())[:10]}...")
        except Exception as e:
            print(f"❌ YOLO model loading error: {e}. Using mock detection.")
            import traceback
            traceback.print_exc()
            self.model = None

    def detect_food(self, image_file):
        if self.model is None:
            return self._mock_detection(image_file)

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
            print(f"Detection error: {e}")
            return self._mock_detection(image_file)

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

    def _mock_detection(self, image_file):
        # ⚠️ WARNING: Using mock detection because YOLO is not loaded!
        # This means YOLO failed to initialize. Check backend logs for errors.
        print("⚠️  WARNING: Using mock detection - YOLO is not loaded!")
        print("⚠️  This is a fallback. Real food detection is not working.")
        print("⚠️  Check backend logs for YOLO loading errors.")

        mock_foods = [
            {'name': 'Apple', 'confidence': 0.95},
            {'name': 'Carrot', 'confidence': 0.92},
            {'name': 'Salad', 'confidence': 0.88},
            {'name': 'Grilled Chicken', 'confidence': 0.91},
            {'name': 'Rice', 'confidence': 0.89},
        ]

        import random
        selected_foods = random.sample(mock_foods, k=random.randint(1, 3))

        return {
            'success': True,
            'detected_items': selected_foods,
            'confidence_score': sum(f['confidence'] for f in selected_foods) / len(selected_foods),
            'mock': True,
            'warning': 'YOLO model failed to load. Returning random mock data. Check backend logs.'
        }

yolo_detector = YOLOFoodDetector()

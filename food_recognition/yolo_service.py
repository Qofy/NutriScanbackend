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
    def __init__(self, model_path='yolov8n.pt'):
        self.model = None
        if YOLO is None:
            print("YOLO not installed. Using mock detection.")
            return

        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"YOLO model loading error: {e}. Using mock detection.")
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

                    detected_items.append({
                        'name': class_name,
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

    def _mock_detection(self, image_file):
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
            'mock': True
        }

yolo_detector = YOLOFoodDetector()

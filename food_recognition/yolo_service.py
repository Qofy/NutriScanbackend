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
            # Increased confidence threshold from 0.15 to 0.6 for more accurate detection
            # 0.15 was too low and caused many false positives
            # 0.6 requires 60% confidence - much more reliable for food detection
            results = self.model.predict(image, conf=0.6)

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
        # Return empty detection instead of random foods
        # When YOLO is not available, we should NOT guess - user should use manual entry
        # or try to load the actual model
        print("⚠️  YOLO model not loaded - returning empty detection")
        return {
            'success': True,
            'detected_items': [],
            'confidence_score': 0,
            'warning': 'YOLO model not available. Please use manual food entry or ensure YOLO is properly installed.'
        }

yolo_detector = YOLOFoodDetector()

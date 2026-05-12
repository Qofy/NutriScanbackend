import os
import json
import logging
import threading
import datetime
import yaml
from pathlib import Path
from django.conf import settings
from .models import FoodAnalysis

logger = logging.getLogger(__name__)

# Global training status
TRAINING_STATUS = {
    'status': 'idle',  # idle, training, done
    'count': 0,
    'threshold': 20,
    'last_trained': None,
}

RETRAIN_THRESHOLD = 20
TRAINING_DATA_DIR = os.path.join(settings.BASE_DIR, 'training_data')
MODELS_DIR = os.path.join(settings.BASE_DIR, 'models')


def get_training_status():
    """Return current training status."""
    return TRAINING_STATUS.copy()


def count_training_entries():
    """Count total manual entries with images."""
    return FoodAnalysis.objects.filter(is_manual=True, image__isnull=False).count()


def prepare_yolo_dataset(output_dir):
    """
    Prepare YOLO-format dataset from manual entries.
    Creates images/ and labels/ subdirectories with .txt annotation files.
    """
    os.makedirs(output_dir, exist_ok=True)

    images_dir = os.path.join(output_dir, 'images', 'train')
    labels_dir = os.path.join(output_dir, 'labels', 'train')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)

    # Get all manual entries with images
    manual_analyses = FoodAnalysis.objects.filter(is_manual=True, image__isnull=False)

    class_names = set()
    image_count = 0

    for analysis in manual_analyses:
        if not analysis.image:
            continue

        try:
            # Copy image file
            image_path = analysis.image.path
            if not os.path.exists(image_path):
                logger.warning(f"Image file not found: {image_path}")
                continue

            # Get image filename and create label filename
            image_filename = os.path.basename(image_path)
            label_filename = os.path.splitext(image_filename)[0] + '.txt'

            # Copy image to training directory
            import shutil
            dest_image = os.path.join(images_dir, image_filename)
            shutil.copy2(image_path, dest_image)

            # Create YOLO-format label file
            # Each recognized item gets a line: class_id center_x center_y width height
            # For manual entries without bounding boxes, we use full image (0.5 0.5 1.0 1.0)
            label_lines = []
            for idx, item in enumerate(analysis.recognized_items):
                class_names.add(item.get('name', f'food_{idx}').lower())
                # Full-image bounding box (normalized coordinates)
                label_lines.append(f"{idx} 0.5 0.5 1.0 1.0")

            # Write label file
            label_path = os.path.join(labels_dir, label_filename)
            with open(label_path, 'w') as f:
                f.write('\n'.join(label_lines))

            image_count += 1
            logger.info(f"Prepared training sample {image_count}: {image_filename}")

        except Exception as e:
            logger.error(f"Error preparing training sample for analysis {analysis.id}: {e}")
            continue

    # Create data.yaml
    class_names = sorted(list(class_names))
    data_yaml = {
        'path': output_dir,
        'train': 'images/train',
        'val': 'images/train',  # Using train for both for now
        'nc': len(class_names),
        'names': class_names
    }

    yaml_path = os.path.join(output_dir, 'data.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f)

    logger.info(f"Created YOLO dataset with {image_count} images and {len(class_names)} classes")
    return yaml_path, image_count


def run_training_async():
    """
    Check if training threshold is reached and spawn async training thread.
    """
    try:
        count = count_training_entries()

        if TRAINING_STATUS['status'] == 'training':
            logger.info("Training already in progress")
            return

        if count < RETRAIN_THRESHOLD:
            logger.info(f"Not enough training data yet: {count}/{RETRAIN_THRESHOLD}")
            TRAINING_STATUS['count'] = count
            return

        logger.info(f"Threshold reached ({count}/{RETRAIN_THRESHOLD}). Starting async training...")
        TRAINING_STATUS['status'] = 'training'
        TRAINING_STATUS['count'] = count

        # Spawn training in a background thread
        training_thread = threading.Thread(target=_train_yolo_background, daemon=True)
        training_thread.start()

    except Exception as e:
        logger.error(f"Error in run_training_async: {e}")
        TRAINING_STATUS['status'] = 'idle'


def _train_yolo_background():
    """Background training task (runs in separate thread)."""
    try:
        logger.info("🧠 Starting YOLO fine-tuning in background...")

        # Prepare dataset
        yaml_path, image_count = prepare_yolo_dataset(TRAINING_DATA_DIR)

        if image_count < 5:
            logger.warning(f"Not enough images for training: {image_count}")
            TRAINING_STATUS['status'] = 'idle'
            return

        try:
            from ultralytics import YOLO
        except ImportError:
            logger.error("ultralytics not installed")
            TRAINING_STATUS['status'] = 'idle'
            return

        # Load base model
        model_path = 'yolov8n.pt'
        if os.path.exists(os.path.join(MODELS_DIR, 'yolo_retrained.pt')):
            model_path = os.path.join(MODELS_DIR, 'yolo_retrained.pt')

        logger.info(f"Loading model: {model_path}")
        model = YOLO(model_path)

        # Train
        logger.info(f"Starting training on {image_count} images...")
        results = model.train(
            data=yaml_path,
            epochs=10,
            imgsz=640,
            patience=5,
            device=0,  # GPU device, falls back to CPU if not available
            verbose=True
        )

        # Save retrained model
        os.makedirs(MODELS_DIR, exist_ok=True)
        best_model_path = os.path.join(MODELS_DIR, 'yolo_retrained.pt')
        model.save(best_model_path)
        logger.info(f"✓ Saved retrained model to {best_model_path}")

        TRAINING_STATUS['status'] = 'done'
        TRAINING_STATUS['last_trained'] = str(datetime.datetime.now())
        logger.info("✓ YOLO training completed successfully")

    except Exception as e:
        logger.error(f"❌ YOLO training failed: {e}", exc_info=True)
        TRAINING_STATUS['status'] = 'idle'

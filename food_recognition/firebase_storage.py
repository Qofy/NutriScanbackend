import logging
import os
import io
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase not installed. Install with: pip install firebase-admin")

class FirebaseImageStorage:
    """Handle image uploads to Firebase Storage"""

    def __init__(self):
        self.bucket = None
        self._init_firebase()

    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not FIREBASE_AVAILABLE:
                logger.warning("Firebase not available")
                return

            # Check if Firebase app is already initialized
            try:
                app = firebase_admin.get_app()
            except ValueError:
                # Firebase not initialized, initialize it
                if settings.FIREBASE_CONFIG:
                    cred = credentials.Certificate(settings.FIREBASE_CONFIG)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': settings.FIREBASE_CONFIG.get('storage_bucket', 'nutriscan-af269.appspot.com')
                    })
                    logger.info("Firebase Admin SDK initialized")
                else:
                    logger.warning("Firebase config not found in settings")
                    return

            app = firebase_admin.get_app()
            self.bucket = storage.bucket()
            logger.info("Firebase Storage bucket initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            self.bucket = None

    def upload_image(self, image_file, folder='food_analysis'):
        """
        Upload image to Firebase Storage

        Args:
            image_file: File object or bytes
            folder: Storage folder path

        Returns:
            str: Public URL of uploaded image or None if failed
        """
        try:
            if not self.bucket:
                logger.error("Firebase Storage bucket not initialized")
                return None

            # Generate unique filename
            import uuid
            from datetime import datetime

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{folder}/{timestamp}_{unique_id}_{image_file.name}"

            # Upload to Firebase
            blob = self.bucket.blob(filename)

            # Handle both file objects and bytes
            if hasattr(image_file, 'read'):
                blob.upload_from_file(image_file, content_type=image_file.content_type)
            else:
                blob.upload_from_string(image_file, content_type='image/jpeg')

            # Make blob publicly accessible
            blob.make_public()

            # Get public URL
            public_url = blob.public_url
            logger.info(f"✓ Uploaded image to Firebase: {filename}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to upload image to Firebase: {str(e)}")
            return None

    def delete_image(self, image_url):
        """Delete image from Firebase Storage by URL"""
        try:
            if not self.bucket or not image_url:
                return False

            # Extract filename from URL
            # URL format: https://storage.googleapis.com/bucket/path/to/file
            if 'storage.googleapis.com' in image_url:
                parts = image_url.split('/o/')
                if len(parts) > 1:
                    filename = parts[1].split('?')[0]
                    blob = self.bucket.blob(filename)
                    blob.delete()
                    logger.info(f"✓ Deleted image from Firebase: {filename}")
                    return True

            return False
        except Exception as e:
            logger.error(f"Failed to delete image from Firebase: {str(e)}")
            return False


# Initialize singleton instance
firebase_image_storage = FirebaseImageStorage()

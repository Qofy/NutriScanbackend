from django.apps import AppConfig

class MedicalProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medical_processing'

    def ready(self):
        from .nlp_service import _get_ocr_reader
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🚀 Initializing medical processing app...")
        try:
            _get_ocr_reader()
        except Exception as e:
            logger.warning(f"⚠️ Failed to pre-load OCR at startup: {e}")

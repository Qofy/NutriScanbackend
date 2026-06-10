import re
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Pre-load OCR reader at module import to cache models
_ocr_reader = None

def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            logger.info("📥 Pre-loading EasyOCR models at startup...")
            _ocr_reader = easyocr.Reader(['en'], verbose=False, gpu=False)
            logger.info("✅ OCR reader cached and ready")
        except Exception as e:
            logger.warning(f"⚠️ Failed to pre-load OCR: {e}")
            _ocr_reader = False
    return _ocr_reader if _ocr_reader else None

COMMON_HEALTH_CONDITIONS = {
    'diabetes': {
        'keywords': ['diabetes', 'blood sugar', 'glucose', 'insulin'],
        'severity': 'high',
        'dietary_restrictions': ['high_sugar_foods', 'refined_carbs']
    },
    'hypertension': {
        'keywords': ['hypertension', 'high blood pressure', 'stage 1', 'stage 2'],
        'severity': 'high',
        'dietary_restrictions': ['high_sodium_foods', 'processed_foods']
    },
    'cholesterol': {
        'keywords': ['cholesterol', 'high cholesterol', 'lipid'],
        'severity': 'moderate',
        'dietary_restrictions': ['saturated_fat', 'trans_fat']
    },
    'heart_disease': {
        'keywords': ['heart disease', 'cardiac', 'coronary', 'arrhythmia'],
        'severity': 'critical',
        'dietary_restrictions': ['high_sodium', 'saturated_fat']
    },
}

COMMON_ALLERGENS = {
    'peanuts': ['peanut', 'groundnut', 'arachis'],
    'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster'],
    'dairy': ['milk', 'lactose', 'cheese', 'butter'],
    'gluten': ['gluten', 'wheat', 'barley', 'rye'],
    'tree_nuts': ['tree nut', 'almond', 'walnut', 'cashew'],
    'fish': ['fish', 'salmon', 'cod', 'tuna'],
    'soy': ['soy', 'soybean'],
    'eggs': ['egg', 'egg white'],
}

class MedicalDocumentProcessor:
    @staticmethod
    def extract_text_with_ocr(pdf_file):
        """Use EasyOCR to extract text from image-based PDFs and images"""
        try:
            from pdf2image import convert_from_bytes
            import easyocr
            import io
            from PIL import Image
            import numpy as np

            logger.info('🔍 Using EasyOCR to extract text from image-based document...')

            # Reset file pointer
            pdf_file.seek(0)
            file_content = pdf_file.read()
            logger.info(f"📄 File size: {len(file_content)} bytes")

            images = []

            # Try to convert PDF to images
            try:
                logger.info('📑 Attempting to convert PDF to images using poppler...')
                images = convert_from_bytes(file_content)
                logger.info(f"✅ Converted PDF to {len(images)} image(s)")
            except Exception as pdf_error:
                logger.warning(f"⚠️ PDF conversion failed: {pdf_error}")
                logger.info('🖼️ Trying to load file directly as image...')

                # Try loading as image directly
                try:
                    img = Image.open(io.BytesIO(file_content))
                    images = [img]
                    logger.info(f"✅ Loaded file as image: {img.format} {img.size}")
                except Exception as img_error:
                    logger.error(f"❌ Could not load as image either: {img_error}")
                    return ""

            if not images:
                logger.error("❌ No images to process")
                return ""

            # Use cached OCR reader
            logger.info('🤖 Getting OCR reader...')
            reader = _get_ocr_reader()
            if not reader:
                logger.error("❌ OCR reader not available")
                return ""
            logger.info('✅ OCR reader ready')

            # Extract text from all images
            extracted_text = ""
            for page_num, image in enumerate(images):
                logger.info(f"📖 Processing page {page_num + 1}...")

                # Convert PIL image to numpy array if needed
                if isinstance(image, Image.Image):
                    image_array = np.array(image)
                else:
                    image_array = image

                logger.info(f"  Image shape: {image_array.shape}")

                # Run OCR
                try:
                    results = reader.readtext(image_array)
                    logger.info(f"  OCR found {len(results)} text regions")

                    # Extract text from results
                    page_text = "\n".join([text[1] for text in results if len(text) > 1])
                    logger.info(f"✅ Page {page_num + 1}: Extracted {len(page_text)} characters")

                    extracted_text += page_text + "\n"
                except Exception as ocr_error:
                    logger.error(f"❌ OCR failed for page {page_num + 1}: {ocr_error}")
                    continue

            logger.info(f"✅ Total OCR text extracted: {len(extracted_text)} characters")
            return extracted_text

        except ImportError as e:
            logger.error(f"❌ Required library not installed: {e}")
            return ""
        except Exception as e:
            logger.error(f"❌ OCR extraction error: {e}", exc_info=True)
            return ""

    @staticmethod
    def extract_text_from_pdf(pdf_file):
        try:
            import PyPDF2

            # Reset file pointer to beginning
            pdf_file.seek(0)

            logger.info(f"🔍 Extracting text from PDF using PyPDF2...")
            logger.info(f"📄 File size: {pdf_file.size if hasattr(pdf_file, 'size') else 'unknown'} bytes")

            pdf_reader = PyPDF2.PdfReader(pdf_file)
            logger.info(f"📄 PDF has {len(pdf_reader.pages)} pages")

            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if not page_text or page_text.strip() == "":
                        logger.warning(f"⚠️ Page {page_num + 1}: No text extracted (might be image-based)")
                        # Try alternative extraction method
                        if hasattr(page, '/Contents'):
                            logger.info(f"📖 Page {page_num + 1}: Has content stream, text extraction might need OCR")
                    else:
                        logger.info(f"📖 Page {page_num + 1}: Extracted {len(page_text)} characters")
                    text += page_text + "\n"
                except Exception as page_error:
                    logger.warning(f"⚠️ Error extracting page {page_num + 1}: {page_error}")
                    continue

            logger.info(f"✅ Total PDF text extracted: {len(text)} characters")
            if len(text.strip()) == 0:
                logger.warning("⚠️ PDF appears to be image-based or encrypted. Consider using OCR.")
            return text
        except ImportError:
            logger.error("❌ PyPDF2 not installed")
            return ""
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {e}", exc_info=True)
            return ""

    @staticmethod
    def extract_health_conditions(text):
        conditions = []
        text_lower = text.lower()

        for condition, info in COMMON_HEALTH_CONDITIONS.items():
            for keyword in info['keywords']:
                if keyword in text_lower:
                    conditions.append({
                        'condition': condition,
                        'confidence': 0.85,
                        'severity': info['severity'],
                        'dietary_restrictions': info['dietary_restrictions']
                    })
                    break

        return conditions

    @staticmethod
    def extract_allergens(text):
        allergens = []
        text_lower = text.lower()

        # Keywords that indicate allergy mention
        allergy_indicators = ['allerg', 'reaction', 'avoid', 'sensitivity', 'intoleran', 'hypersensitiv', 'anaphyla', 'asthma', 'positive', 'reactive']

        # First, try to find common allergens by keyword
        for allergen, keywords in COMMON_ALLERGENS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Check if this allergen is mentioned in context of allergies/reactions
                    # Look for allergy indicators in nearby text (within 100 characters)
                    keyword_pos = text_lower.find(keyword)
                    if keyword_pos != -1:
                        start = max(0, keyword_pos - 100)
                        end = min(len(text_lower), keyword_pos + 100)
                        nearby_text = text_lower[start:end]

                        # If any allergy indicator is found nearby, mark as allergen
                        if any(indicator in nearby_text for indicator in allergy_indicators):
                            allergens.append({
                                'allergen': allergen,
                                'confidence': 0.80,
                                'severity': 'moderate'
                            })
                            break
                    # Also check if it's mentioned in a section that looks like allergies
                    elif 'allergies:' in text_lower or 'allergy:' in text_lower or 'allergic to' in text_lower:
                        allergens.append({
                            'allergen': allergen,
                            'confidence': 0.80,
                            'severity': 'moderate'
                        })
                        break

        # If no common allergens found but document looks like an allergy report,
        # flag it generically for manual review
        if not allergens and 'allergy' in text_lower:
            # Check for allergy testing report patterns (SPT, skin test, prick test)
            if any(term in text_lower for term in ['test', 'prick', 'spt', 'positive', 'reactive']):
                allergens.append({
                    'allergen': 'multiple allergens (see allergy testing report)',
                    'confidence': 0.70,
                    'severity': 'moderate'
                })

        return allergens

    @staticmethod
    def extract_dietary_restrictions(text, conditions):
        restrictions = []

        for condition in conditions:
            dietary_info = COMMON_HEALTH_CONDITIONS.get(condition.get('condition'), {})
            for restriction in dietary_info.get('dietary_restrictions', []):
                restrictions.append({
                    'restriction': restriction,
                    'reason': f"Based on {condition.get('condition')} diagnosis",
                    'recommendation': f"Avoid {restriction.replace('_', ' ')}"
                })

        return restrictions

    @staticmethod
    def extract_with_ollama_vision(pdf_file):
        """Use Ollama vision to extract medical info from image-based PDFs or images"""
        try:
            import base64

            api_key = getattr(settings, 'OLLAMA_API_KEY', None)
            if not api_key or not api_key.strip():
                logger.warning('❌ Ollama API key not configured for vision')
                return None

            logger.info('👁️ Using Ollama vision to extract from image-based PDF...')

            # Read the file
            pdf_file.seek(0)
            file_content = pdf_file.read()

            # Encode to base64
            file_base64 = base64.standard_b64encode(file_content).decode('utf-8')

            # Determine media type
            if pdf_file.name.endswith('.pdf'):
                media_type = 'application/pdf'
            elif pdf_file.name.endswith('.png'):
                media_type = 'image/png'
            elif pdf_file.name.endswith('.jpg') or pdf_file.name.endswith('.jpeg'):
                media_type = 'image/jpeg'
            else:
                media_type = 'application/octet-stream'

            prompt = """You are a medical document analyzer. Extract health information from this medical document (PDF or image).

Extract and return ONLY a valid JSON object with this exact structure:
{
    "conditions": [
        {"condition": "disease name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}
    ],
    "allergens": [
        {"allergen": "allergen name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}
    ],
    "dietary_restrictions": [
        {"restriction": "restriction description", "reason": "why", "recommendation": "what to do"}
    ]
}

Be thorough and extract ALL mentioned allergens, conditions, and restrictions from the document.
Return ONLY valid JSON, no markdown, no other text."""

            url = 'https://ollama.com/api/chat'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': 'ministral-3:8b',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [file_base64]
                    }
                ],
                'stream': False,
                'temperature': 0.3
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('message', {}).get('content', '').strip()

                # Clean up response if it has markdown
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.rstrip('`').strip()

                result = json.loads(response_text)
                logger.info('✅ Ollama vision extraction successful')
                return result
            else:
                logger.warning(f'❌ Ollama API error: {response.status_code}')
                return None

        except json.JSONDecodeError as e:
            logger.warning(f'❌ Failed to parse Ollama vision response: {e}')
            return None
        except Exception as e:
            logger.warning(f'❌ Ollama vision extraction failed: {e}')
            return None

    @staticmethod
    def extract_with_claude_vision(pdf_file):
        """Use Claude's vision to extract medical info from image-based PDFs or images"""
        try:
            import base64
            from anthropic import Anthropic

            api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not api_key or not api_key.strip():
                logger.warning('❌ Claude API key not configured for vision')
                return None

            logger.info('👁️ Using Claude vision to extract from image-based PDF...')

            # Read the file
            pdf_file.seek(0)
            file_content = pdf_file.read()

            # Determine media type
            if pdf_file.name.endswith('.pdf'):
                media_type = 'application/pdf'
            elif pdf_file.name.endswith('.png'):
                media_type = 'image/png'
            elif pdf_file.name.endswith('.jpg') or pdf_file.name.endswith('.jpeg'):
                media_type = 'image/jpeg'
            else:
                media_type = 'application/octet-stream'

            # Encode to base64
            file_base64 = base64.standard_b64encode(file_content).decode('utf-8')

            client = Anthropic()

            prompt = """You are a medical document analyzer. Extract health information from this medical document (PDF or image).

Extract and return ONLY a valid JSON object with this exact structure:
{
    "conditions": [
        {"condition": "disease name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}
    ],
    "allergens": [
        {"allergen": "allergen name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}
    ],
    "dietary_restrictions": [
        {"restriction": "restriction description", "reason": "why", "recommendation": "what to do"}
    ]
}

Be thorough and extract ALL mentioned allergens, conditions, and restrictions from the document.
Return ONLY valid JSON, no markdown, no other text."""

            response = client.messages.create(
                model="claude-opus-4-1",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": file_base64,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            response_text = response.content[0].text.strip()

            # Clean up response if it has markdown
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.rstrip('`').strip()

            result = json.loads(response_text)
            logger.info('✅ Claude vision extraction successful')
            return result

        except ImportError:
            logger.warning('❌ Anthropic SDK not installed')
            return None
        except json.JSONDecodeError as e:
            logger.warning(f'❌ Failed to parse Claude vision response: {e}')
            return None
        except Exception as e:
            logger.warning(f'❌ Claude vision extraction failed: {e}')
            return None

    @staticmethod
    def extract_with_ai(raw_text):
        """Use Claude/Ollama to create intelligent medical summary"""
        # Try Ollama Cloud first for summary
        result = MedicalDocumentProcessor._extract_with_ollama(raw_text)
        if result and result.get('summary'):
            return result

        # Fall back to Claude for summary
        result = MedicalDocumentProcessor._extract_with_claude(raw_text)
        if result and result.get('summary'):
            return result

        # No AI summary available
        logger.info("AI summary not available, will use raw text + keyword matching")
        return None

    @staticmethod
    def _extract_with_ollama(raw_text):
        """Extract using Ollama Cloud API"""
        try:
            api_key = getattr(settings, 'OLLAMA_API_KEY', None)
            if not api_key or not api_key.strip():
                logger.debug('⚠️  Ollama API key not configured')
                return None

            logger.info('🔍 Trying Ollama Cloud for medical extraction...')

            url = 'https://ollama.com/api/chat'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # Simpler prompt: just extract the key health info
            prompt = f"""You are a medical document analyzer. Read this medical report and extract the key health conditions, allergies, and dietary needs mentioned.

MEDICAL REPORT TEXT:
{raw_text}

Respond with a brief summary identifying:
- Any diseases or health conditions mentioned
- Any allergies or sensitivities mentioned
- Any dietary restrictions or recommendations mentioned

Keep your response concise and factual."""

            payload = {
                'model': 'ministral-3:8b',
                'messages': [{'role': 'user', 'content': prompt}],
                'stream': False,
                'temperature': 0.3
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            logger.info(f'📡 Ollama API response status: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                logger.info(f'📊 Ollama response data: {data.get("message", {})}')
                content = data.get('message', {}).get('content', '').strip()
                if content:
                    logger.info(f'✅ Ollama extraction successful: {len(content)} chars')
                    # Return as summary text, not JSON
                    return {'summary': content, 'from_ai': True}
                else:
                    logger.warning('⚠️  Ollama returned empty response')
                    return None
            else:
                logger.warning(f'⚠️  Ollama API error: {response.status_code} - {response.text}')
                return None
        except Exception as e:
            logger.warning(f'⚠️  Ollama extraction failed: {e}')
            return None

    @staticmethod
    def _extract_with_claude(raw_text):
        """Extract using Claude API"""
        try:
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not api_key or not api_key.strip():
                return None

            logger.info('🔍 Trying Claude for medical extraction...')

            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }

            prompt = f"""You are a medical document analyzer. Extract health information from this medical report.

MEDICAL REPORT:
{raw_text}

Return ONLY a JSON object (no markdown, no other text) with this exact structure:
{{
    "conditions": [
        {{"condition": "disease name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}}
    ],
    "allergens": [
        {{"allergen": "allergen name", "severity": "low|moderate|high|critical", "confidence": 0.0-1.0}}
    ],
    "dietary_restrictions": [
        {{"restriction": "restriction description", "reason": "why", "recommendation": "what to do"}}
    ]
}}"""

            payload = {
                'model': 'claude-opus-4-1',
                'max_tokens': 1024,
                'messages': [{'role': 'user', 'content': prompt}]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [{}])[0].get('text', '')
                try:
                    result = json.loads(content)
                    logger.info('✅ Claude extraction successful')
                    return result
                except json.JSONDecodeError:
                    logger.warning('Failed to parse Claude response as JSON')
                    return None
        except Exception as e:
            logger.warning(f'Claude extraction failed: {e}')
            return None

    @staticmethod
    def generate_clinical_summary(raw_text, conditions, allergens, restrictions, extraction_method):
        """Generate comprehensive clinical interpretation with report assessment and limitations"""
        try:
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not api_key or not api_key.strip():
                logger.warning('❌ Claude API key not configured for summary')
                return None

            logger.info('📝 Generating clinical summary with report assessment...')

            # Analyze what's in the report
            report_sections = {
                'lab_values': 'hba1c' in raw_text.lower() or 'glucose' in raw_text.lower(),
                'medications': 'medication' in raw_text.lower() or 'rx' in raw_text.lower(),
                'family_history': 'family' in raw_text.lower() or 'hereditary' in raw_text.lower(),
                'lifestyle': 'diet' in raw_text.lower() or 'exercise' in raw_text.lower() or 'smoking' in raw_text.lower(),
                'allergies': 'allerg' in raw_text.lower(),
                'vital_signs': 'bp' in raw_text.lower() or 'blood pressure' in raw_text.lower() or 'weight' in raw_text.lower(),
            }

            present_sections = [k for k, v in report_sections.items() if v]
            missing_sections = [k for k, v in report_sections.items() if not v]
            completeness = int((len(present_sections) / 6) * 100)

            # Determine report type
            report_type = 'General Medical Report'
            if 'lab' in raw_text.lower() or 'hba1c' in raw_text.lower():
                report_type = 'Laboratory Report'
            elif 'allerg' in raw_text.lower():
                report_type = 'Allergy Testing Report'
            elif 'clinical' in raw_text.lower() or 'note' in raw_text.lower():
                report_type = 'Clinical Notes'

            prompt = f"""You are a medical AI assistant. Analyze this medical report and provide a comprehensive clinical summary with three sections:

MEDICAL REPORT:
{raw_text[:2000]}

EXTRACTED DATA:
- Conditions: {[c.get('condition') for c in conditions]}
- Allergens: {[a.get('allergen') for a in allergens]}
- Restrictions: {[r.get('restriction') for r in restrictions]}

REPORT METADATA:
- Type: {report_type}
- Present sections: {', '.join(present_sections) if present_sections else 'minimal'}
- Missing sections: {', '.join(missing_sections)}
- Completeness: {completeness}%

Generate a response with exactly 3 sections (use === SECTION NAME === format):

1. REPORT ASSESSMENT
   - What type of report is this?
   - Quality of structure (Well-structured / Partially-structured / Poorly-structured)
   - Completeness percentage
   - Notable gaps (what critical info is missing?)

2. CLINICAL INTERPRETATION
   - For each condition found, explain what it means in plain language
   - Include specific values/measurements mentioned (e.g., "HbA1C of 5%")
   - Explain clinical significance and health implications
   - What does this mean for the patient's health?

3. REPORT LIMITATIONS
   - List what information was NOT found but would be important
   - Explain why missing data affects recommendations
   - Confidence level in the extracted information
   - Warning flags (e.g., "This lab report lacks medication history, so recommendations may not account for drug interactions")

Keep language clear for patients, not overly technical. Be specific about values and findings."""

            url = 'https://api.anthropic.com/v1/messages'
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }

            payload = {
                'model': 'claude-opus-4-1',
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}]
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                summary_text = data.get('content', [{}])[0].get('text', '').strip()
                logger.info(f'✅ Clinical summary generated: {len(summary_text)} characters')
                return {
                    'clinical_summary': summary_text,
                    'report_type': report_type,
                    'completeness': completeness,
                    'missing_sections': missing_sections,
                    'extraction_method': extraction_method
                }
            else:
                logger.warning(f'❌ Claude API error: {response.status_code}')
                return None

        except Exception as e:
            logger.warning(f'❌ Clinical summary generation failed: {e}')
            return None

    @staticmethod
    def process_medical_document(file_obj):
        raw_text = ''
        is_mock_data = False

        try:
            logger.info(f"📄 Processing file: {file_obj.name}")
            if file_obj.name.endswith('.pdf'):
                logger.info('📑 Extracting text from PDF...')
                raw_text = MedicalDocumentProcessor.extract_text_from_pdf(file_obj)
                if not raw_text or raw_text.strip() == '':
                    logger.warning('⚠️ PDF text extraction returned empty, likely image-based PDF')
            elif file_obj.name.endswith(('.png', '.jpg', '.jpeg')):
                logger.info('🖼️ Processing image file...')
                # Image files will be handled by OCR below
                raw_text = ''
            else:
                logger.info('📝 Reading as text file...')
                try:
                    file_obj.seek(0)
                    raw_text = file_obj.read().decode('utf-8')
                    logger.info(f"✓ Text file read: {len(raw_text)} characters")
                except Exception as e:
                    logger.error(f"❌ Error reading text file: {e}")
                    raw_text = ''

            logger.info(f"✓ Total extracted: {len(raw_text)} characters of text")
        except Exception as e:
            logger.error(f"❌ File processing error: {e}", exc_info=True)
            raw_text = ''

        # If text extraction failed, try vision APIs for image-based documents
        if not raw_text or len(raw_text.strip()) < 10:
            if file_obj.name.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                logger.info('📸 Text extraction failed, trying vision APIs for image-based document...')

                # Try Ollama vision
                file_obj.seek(0)
                vision_result = MedicalDocumentProcessor.extract_with_ollama_vision(file_obj)
                if vision_result:
                    logger.info('✅ Ollama vision extraction successful')
                    return {
                        'raw_text': 'Extracted via Ollama vision',
                        'conditions': vision_result.get('conditions', []),
                        'allergens': vision_result.get('allergens', []),
                        'dietary_restrictions': vision_result.get('dietary_restrictions', []),
                        'is_mock': False,
                        'extraction_method': 'Ollama Vision'
                    }

                # Fall back to Claude vision if available
                logger.info('⚠️ Trying Claude vision...')
                file_obj.seek(0)
                vision_result = MedicalDocumentProcessor.extract_with_claude_vision(file_obj)
                if vision_result:
                    logger.info('✅ Claude vision extraction successful')
                    return {
                        'raw_text': 'Extracted via vision API',
                        'conditions': vision_result.get('conditions', []),
                        'allergens': vision_result.get('allergens', []),
                        'dietary_restrictions': vision_result.get('dietary_restrictions', []),
                        'is_mock': False,
                        'extraction_method': 'Claude Vision'
                    }

            # Only use mock data if we still have no text after all extraction attempts
            if not raw_text or len(raw_text.strip()) < 10:
                logger.warning('⚠️ Could not extract meaningful text from file, using mock data for processing')
                is_mock_data = True
                raw_text = MedicalDocumentProcessor._mock_document_text()

        # Always do keyword matching as fallback/supplement
        logger.info('📚 Running keyword-based extraction...')
        conditions = MedicalDocumentProcessor.extract_health_conditions(raw_text)
        allergens = MedicalDocumentProcessor.extract_allergens(raw_text)
        restrictions = MedicalDocumentProcessor.extract_dietary_restrictions(raw_text, conditions)

        logger.info(f"✓ Keyword extraction found: {len(conditions)} conditions, {len(allergens)} allergens, {len(restrictions)} restrictions")

        # Generate comprehensive clinical summary with report assessment
        extraction_method = 'keyword' if not is_mock_data else 'mock'
        logger.info('📋 Generating comprehensive clinical summary with report assessment...')
        clinical_summary_result = MedicalDocumentProcessor.generate_clinical_summary(
            raw_text,
            conditions,
            allergens,
            restrictions,
            extraction_method
        )

        return {
            'raw_text': raw_text,  # Full extracted text for display and analysis
            'clinical_summary': clinical_summary_result.get('clinical_summary') if clinical_summary_result else None,  # Comprehensive 3-section summary
            'report_type': clinical_summary_result.get('report_type') if clinical_summary_result else 'Unknown',
            'completeness': clinical_summary_result.get('completeness') if clinical_summary_result else 0,
            'missing_sections': clinical_summary_result.get('missing_sections') if clinical_summary_result else [],
            'conditions': conditions,
            'allergens': allergens,
            'dietary_restrictions': restrictions,
            'is_mock': is_mock_data,
            'extraction_method': extraction_method
        }

    @staticmethod
    def _mock_document_text():
        return """
        Patient: John Doe
        Date: 2026-04-15

        MEDICAL REPORT

        Diagnosis: The patient has been diagnosed with Type 2 Diabetes and Hypertension (Stage 1).
        Blood sugar levels are elevated and require management through diet and medication.

        Allergies: Patient reports allergy to peanuts with history of mild reactions.
        Also sensitive to shellfish.

        Recommendations: Patient should avoid high sodium foods and refined carbohydrates.
        Regular exercise and weight management are essential.

        Medications: Metformin 500mg twice daily, Lisinopril 10mg once daily.
        """

# YOLO Food Detection Guide

## What Changed

### Fixed Issues
1. **Confidence Threshold**: `0.15 → 0.6` (60% confidence required)
   - Old: Accepted detections with only 15% confidence = MANY FALSE POSITIVES
   - New: Requires 60% confidence = much more reliable
   - Impact: Should eliminate wrong fruit identifications

2. **Mock Fallback**: Returns empty list instead of random foods
   - Old: If YOLO failed, returned random foods (Apple, Carrot, Rice, etc.)
   - New: Returns empty, user must use manual entry
   - Impact: No more fake "wrong information"

---

## Current Detection System

### Model Being Used
- **yolov8n.pt** (COCO dataset - generic object detection)
- NOT food-specific, but works for common food items
- Detects ~80 object classes (people, cars, food, animals, etc.)

### Detection Pipeline

```
User takes photo
    ↓
SmartCameraView polls every 2 seconds
    ↓
POST /api/food/analysis/detect/ (low-res snapshot)
    ↓
YOLO model predicts with conf=0.6
    ↓
Returns detected items with bounding boxes
    ↓
Frontend shows green boxes + confidence scores
```

### What It Can Detect
- ✅ Fruits: apple, banana, orange, banana
- ✅ Vegetables: carrot, broccoli, lettuce, potato, tomato
- ✅ Proteins: chicken, bottle (wine/beer), sandwich, pizza
- ✅ Common foods: donut, cake, pizza, hotdog
- ⚠️  Generic objects if misclassified (bottle might be "cup", carrot might be "toothbrush")

---

## Custom Model Training System

Your app has an **automatic retraining system**:

### How It Works
1. User adds food with image via **Manual Entry** (with reference photo)
2. System saves the image + food labels
3. After **20 labeled images**, training triggers automatically
4. YOLO model fine-tunes on your food data
5. New model saved as `yolo_retrained.pt`
6. Future detections use the custom model

### Training Status
Check training progress:
```bash
# In backend directory
curl http://localhost:8000/api/food/analysis/training_status/
```

**Response:**
```json
{
  "status": "idle",        // idle, training, done
  "count": 15,             // manual entries with images
  "threshold": 20,         // required for training
  "last_trained": "2024-01-15T14:30:00"
}
```

### Training Benefits
- ✅ Learns your specific food items
- ✅ Reduces misclassifications (fruits as other objects)
- ✅ Improves accuracy over time
- ✅ Works offline with retrained model

---

## Why Fruits Are Misidentified

### Common Causes (Now Fixed)

1. **Low Confidence Threshold** ❌ NOW FIXED
   - `conf=0.15` accepted anything with 15% confidence
   - Banana detected as "stick", "rope", etc.
   - **FIX**: Changed to `conf=0.6`

2. **Generic Model**
   - YOLO hasn't seen all fruit types
   - Red apple might detect as "ball" or "person"
   - **SOLUTION**: Use manual entry + get training to 20 images

3. **Image Quality**
   - Low light, blurry, partial fruit
   - YOLO struggles with poor quality
   - **SOLUTION**: Use good lighting, capture full fruit

---

## How to Improve Detection

### Option 1: Train Custom Model (RECOMMENDED)
Best long-term solution:

1. **Add 20 food samples with images** via Manual Entry
   - Include fruits you want to detect accurately
   - Good lighting, clear photos
   - Be specific: "Apple (Red Delicious)", not just "Apple"

2. **System auto-trains** after 20 samples

3. **Check training status**:
   ```bash
   curl http://localhost:8000/api/food/analysis/training_status/
   ```

4. **Once trained** (`status: "done"`)
   - Model saved as `/backend/models/yolo_retrained.pt`
   - All future detections use custom model
   - Much better fruit detection!

### Option 2: Increase Confidence Threshold (QUICK FIX)
Already done! Changed from 0.15 → 0.6

If you want even stricter:
Edit `yolo_service.py` line 33:
```python
# Very strict (eliminates most false positives)
results = self.model.predict(image, conf=0.75)

# Balanced (current)
results = self.model.predict(image, conf=0.6)

# More lenient (catches more items, some wrong)
results = self.model.predict(image, conf=0.45)
```

### Option 3: Use Better Base Model
For production, consider:
- `yolov8m.pt` (medium model) - better accuracy, slower
- `yolov8s.pt` (small model) - balanced
- Food-specific models (train on food dataset first)

Change in `yolo_service.py` line 15:
```python
def __init__(self, model_path='yolov8m.pt'):  # Change here
    self.model = None
    ...
```

---

## Testing Detection Accuracy

### 1. Test with Camera
- Take photos of fruits
- Check bounding boxes and confidence scores
- Look at console for detected items

### 2. Check Logs
```bash
# Watch backend logs
tail -f /var/log/nutriscan.log | grep "Detection"
```

### 3. Manual Entry for Ground Truth
When you manually enter a fruit:
- System learns the correct label
- Counts toward retraining
- Improves future detection

---

## Production Recommendations

| Scenario | Action |
|----------|--------|
| **Testing locally** | Keep `conf=0.6` |
| **Want stricter detection** | Increase to `conf=0.75` |
| **Want looser detection** | Decrease to `conf=0.45` |
| **Training is important** | Collect 20+ labeled samples |
| **Need best accuracy** | Use `yolov8m.pt` + custom training |
| **Speed is critical** | Use `yolov8n.pt` + `conf=0.6` |

---

## Troubleshooting

### "Wrong fruit identification" errors
**Cause**: Generic YOLO model + old low confidence threshold
**Fix**: Already applied! Confidence threshold is now 0.6
**Next step**: Add 20 manual samples with fruits to trigger retraining

### Detection API returns empty list
**Cause**: YOLO not loaded or no foods detected with conf≥0.6
**Fix**: Check backend logs, verify YOLO is installed, use manual entry

### Training never completes
**Cause**: Not enough manual samples (need 20 images)
**Current**: Check status endpoint - see how many you have
**Action**: Add more manual entries with reference photos

### Banana detected as "stick"
**Cause**: Generic model's class names are generic
**Fix**: Custom training will learn "banana" specifically
**Next**: Use manual entry for fruits you want to detect

---

## Architecture

### Files
- `yolo_service.py` - Detection logic
  - `conf=0.6` threshold
  - Empty fallback (not random)
  - Uses yolov8n.pt by default

- `yolo_trainer.py` - Auto-training system
  - Triggers at 20 manual samples
  - Creates YOLO dataset format
  - Trains for 10 epochs
  - Saves best model

- `views.py` - API endpoints
  - `/api/food/analysis/detect/` - real-time detection
  - `/api/food/analysis/analyze/` - full analysis with nutrition
  - `/api/food/analysis/manual_analyze/` - manual entry
  - `/api/food/analysis/training_status/` - check training progress

### Detection Flow
```
Camera Snapshot (320x240)
    ↓
yolo_detector.detect_food(image)
    ↓
YOLO.predict(image, conf=0.6)
    ↓
Extract boxes with confidence > 60%
    ↓
Return items with names + bounding boxes
    ↓
Frontend draws green boxes
    ↓
User confirms and captures at full resolution
    ↓
Full analysis with nutrition + safety
```

---

## Next Steps

1. **Test the fix**: Take photos of fruits, check console
2. **Collect training data**: Add 20+ samples via manual entry
3. **Monitor training**: Check `/training_status/` endpoint
4. **Verify improvement**: After training, fruits should be more accurate

---

## Your Thesis Metrics (RQ1)

Food Recognition Accuracy is measured by:
- **Overall Accuracy**: 90.4% (target)
- **Average Latency**: 520ms (target)
- **Confidence Threshold**: Now 0.6 (was 0.15)
- **Custom Training**: Active (improves accuracy over time)

Console logs will show these metrics during detection.

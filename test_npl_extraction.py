#!/usr/bin/env python
"""Test NLP extraction on all medical reports in backend/md_reports"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, '/Users/kofisafoagyekum/Desktop/NutriScan/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutriscan.settings')
django.setup()

from medical_processing.nlp_service import MedicalDocumentProcessor
import json

# Test files
MD_REPORTS_DIR = Path('/Users/kofisafoagyekum/Desktop/NutriScan/backend/md_reports')
test_files = sorted(MD_REPORTS_DIR.glob('*'))

print("\n" + "="*80)
print("🔬 TESTING NLP EXTRACTION ON ALL 9 MEDICAL REPORTS")
print("="*80)

results = []

for idx, file_path in enumerate(test_files, 1):
    if file_path.is_file():
        print(f"\n[{idx}/9] 📄 Testing: {file_path.name}")
        print("-" * 80)

        try:
            from django.core.files.uploadedfile import SimpleUploadedFile

            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Create a Django UploadedFile object
            uploaded_file = SimpleUploadedFile(
                name=file_path.name,
                content=file_content,
                content_type='application/octet-stream'
            )

            result = MedicalDocumentProcessor.process_medical_document(uploaded_file)

            extraction_method = result.get('extraction_method', 'unknown')
            is_mock = result.get('is_mock', False)
            error = result.get('error', None)

            # Check if extraction failed
            if extraction_method == 'failed' or error:
                print(f"❌ Extraction failed!")
                print(f"   Error: {error}")
                results.append({
                    'file': file_path.name,
                    'success': False,
                    'error': error
                })
                continue

            conditions = result.get('conditions', [])
            allergens = result.get('allergens', [])
            restrictions = result.get('dietary_restrictions', [])
            clinical_summary = result.get('clinical_summary', '')
            report_type = result.get('report_type', 'Unknown')
            completeness = result.get('completeness', 0)

            print(f"✅ Extraction successful!")
            print(f"   Method: {extraction_method}")
            print(f"   Is Mock: {is_mock}")
            print(f"   Report Type: {report_type}")
            print(f"   Completeness: {completeness}%")

            if conditions:
                print(f"\n   🏥 Conditions ({len(conditions)}):")
                for c in conditions:
                    print(f"      • {c.get('condition')} (confidence: {c.get('confidence', 'N/A')}, severity: {c.get('severity', 'N/A')})")

            if allergens:
                print(f"\n   ⚠️  Allergens ({len(allergens)}):")
                for a in allergens:
                    print(f"      • {a.get('allergen')} (confidence: {a.get('confidence', 'N/A')}, severity: {a.get('severity', 'N/A')})")

            if restrictions:
                print(f"\n   🍽️  Restrictions ({len(restrictions)}):")
                for r in restrictions:
                    print(f"      • {r.get('restriction')}")
                    if r.get('reason'):
                        print(f"        Reason: {r.get('reason')}")

            if clinical_summary:
                print(f"\n   📋 Clinical Summary Generated: {len(clinical_summary)} characters")
                # Show first 200 chars
                preview = clinical_summary[:200].replace('\n', ' ')
                print(f"      Preview: {preview}...")

            results.append({
                'file': file_path.name,
                'success': True,
                'extraction_method': extraction_method,
                'is_mock': is_mock,
                'report_type': report_type,
                'completeness': completeness,
                'conditions_count': len(conditions),
                'allergens_count': len(allergens),
                'restrictions_count': len(restrictions),
                'has_clinical_summary': bool(clinical_summary),
                'conditions': conditions,
                'allergens': allergens,
                'restrictions': restrictions,
                'clinical_summary': clinical_summary
            })

        except Exception as e:
            print(f"❌ Extraction failed: {str(e)}")
            results.append({
                'file': file_path.name,
                'success': False,
                'error': str(e)
            })

print("\n" + "="*80)
print("📊 SUMMARY TABLE")
print("="*80)
print(f"\n{'File':<20} {'Status':<12} {'Method':<15} {'Report Type':<20} {'Complete%':<10} {'Conditions':<12} {'Allergens':<10} {'Summary':<10}")
print("-"*120)

for r in results:
    status = "✅ OK" if r['success'] else "❌ FAIL"
    method = r.get('extraction_method', 'N/A')
    report_type = r.get('report_type', 'N/A')[:18]
    completeness = r.get('completeness', 0)
    conditions = r.get('conditions_count', 0)
    allergens = r.get('allergens_count', 0)
    has_summary = "Yes" if r.get('has_clinical_summary') else "No"

    file_name = r['file'][:18]
    print(f"{file_name:<20} {status:<12} {method:<15} {report_type:<20} {completeness:<10} {conditions:<12} {allergens:<10} {has_summary:<10}")

print("\n" + "="*80)
print("📈 STATISTICS")
print("="*80)
successful = sum(1 for r in results if r['success'])
failed = sum(1 for r in results if not r['success'])
total_conditions = sum(r.get('conditions_count', 0) for r in results if r['success'])
total_allergens = sum(r.get('allergens_count', 0) for r in results if r['success'])
avg_completeness = sum(r.get('completeness', 0) for r in results if r['success']) / successful if successful > 0 else 0
reports_with_summary = sum(1 for r in results if r.get('has_clinical_summary'))

print(f"\nTotal Files Tested: {len(results)}")
print(f"Successful: {successful} ✅")
print(f"Failed: {failed} ❌")
print(f"Total Conditions Extracted: {total_conditions}")
print(f"Total Allergens Extracted: {total_allergens}")
print(f"Average Completeness: {avg_completeness:.1f}%")
print(f"Reports with Clinical Summary: {reports_with_summary}/{successful}")

# Save detailed results to JSON
output_file = Path('/Users/kofisafoagyekum/Desktop/NutriScan/backend/npl_extraction_test_results.json')
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n💾 Detailed results saved to: {output_file}")
print("\n" + "="*80)

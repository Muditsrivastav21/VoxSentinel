#!/usr/bin/env python3
"""
Test script to verify the API with the official sample audio.
Run: python test_sample_audio.py
"""

import urllib.request
import base64
import json
import os

# Configuration
API_URL = "https://voxsentinel.onrender.com/api/call-analytics"
API_KEY = "sk_track3_987654321"
SAMPLE_AUDIO_URL = "https://recordings.exotel.com/exotelrecordings/guvi64/5780094ea05a75c867120809da9a199f.mp3"

def main():
    print("=" * 60)
    print("VoxSentinel API Test - Official Sample Audio")
    print("=" * 60)
    
    # Step 1: Download sample audio
    print("\n📥 Downloading sample audio...")
    temp_file = "temp_sample.mp3"
    urllib.request.urlretrieve(SAMPLE_AUDIO_URL, temp_file)
    file_size = os.path.getsize(temp_file)
    print(f"   Downloaded: {file_size:,} bytes")
    
    # Step 2: Convert to base64
    print("\n🔄 Converting to base64...")
    with open(temp_file, 'rb') as f:
        audio_bytes = f.read()
    base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
    print(f"   Base64 length: {len(base64_audio):,} chars")
    
    # Step 3: Call API
    print("\n📡 Calling API (this may take 30-60 seconds)...")
    print(f"   URL: {API_URL}")
    
    # Prepare request
    payload = json.dumps({
        "language": "Tamil",  # Sample is Tamil/Tanglish
        "audioBase64": base64_audio
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    req = urllib.request.Request(API_URL, data=payload, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print("\n✅ SUCCESS!")
            print("=" * 60)
            
            # Display key results
            print(f"\n📋 Status: {result.get('status')}")
            print(f"🌐 Language: {result.get('language')}")
            
            print(f"\n📝 Summary:")
            print(f"   {result.get('summary', 'N/A')[:200]}...")
            
            sop = result.get('sop_validation', {})
            print(f"\n✅ SOP Validation:")
            print(f"   • Greeting: {sop.get('greeting')}")
            print(f"   • Identification: {sop.get('identification')}")
            print(f"   • Problem Statement: {sop.get('problemStatement')}")
            print(f"   • Solution Offering: {sop.get('solutionOffering')}")
            print(f"   • Closing: {sop.get('closing')}")
            print(f"   • Compliance Score: {sop.get('complianceScore')}")
            print(f"   • Adherence Status: {sop.get('adherenceStatus')}")
            
            analytics = result.get('analytics', {})
            print(f"\n📊 Analytics:")
            print(f"   • Payment Preference: {analytics.get('paymentPreference')}")
            print(f"   • Rejection Reason: {analytics.get('rejectionReason')}")
            print(f"   • Sentiment: {analytics.get('sentiment')}")
            
            keywords = result.get('keywords', [])
            print(f"\n🏷️ Keywords: {', '.join(keywords[:10])}")
            
            # Save full response
            with open('sample_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full response saved to: sample_response.json")
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.code}")
        print(f"   {e.read().decode('utf-8')}")
    except urllib.error.URLError as e:
        print(f"\n❌ Connection Error: {e.reason}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()

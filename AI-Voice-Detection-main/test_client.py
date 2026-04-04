"""
Call Center Compliance API - Test Client
=========================================
Test script for Track 3: Call Center Analytics API
"""

import base64
import requests
import sys
import json
import os

# Configuration - Change these for your deployment
API_URL = os.getenv("API_URL", "http://localhost:8000/api/call-analytics")
API_KEY = os.getenv("API_KEY")  # Must be set in environment


def test_call_analytics(audio_file="test.mp3", language="Tamil"):
    """
    Test the Call Center Compliance API
    
    Args:
        audio_file: Path to MP3 audio file
        language: "Tamil" or "Hindi"
    """
    
    print("=" * 60)
    print("🎯 CALL CENTER COMPLIANCE API - TEST CLIENT")
    print("=" * 60)
    
    # 1. Read and encode audio file
    try:
        with open(audio_file, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")
        file_size = os.path.getsize(audio_file) / 1024  # KB
        print(f"✅ Audio file loaded: {audio_file} ({file_size:.1f} KB)")
    except FileNotFoundError:
        print(f"❌ Error: {audio_file} not found")
        print("Usage: python test_client.py <audio_file.mp3> [Tamil|Hindi]")
        return None
    
    # 2. Prepare request
    payload = {
        "language": language,
        "audioFormat": "mp3",
        "audioBase64": audio_base64
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    # 3. Call API
    print(f"\n📡 Endpoint: {API_URL}")
    print(f"🔐 API Key: {API_KEY[:15]}...")
    print(f"🌐 Language: {language}")
    print("\n⏳ Processing audio (this may take 15-30 seconds)...")
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=180  # 3 minutes timeout for longer audio
        )
        
        # Check response status
        if response.status_code == 401:
            print("❌ Authentication failed! Check your API key.")
            return None
        elif response.status_code == 400:
            print(f"❌ Bad request: {response.json().get('message', 'Unknown error')}")
            return None
        
        response.raise_for_status()
        result = response.json()
        
        # 4. Display results
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 60)
        
        print(f"\n📋 STATUS: {result.get('status')}")
        print(f"🌐 LANGUAGE: {result.get('language')}")
        
        # Transcript
        print(f"\n📝 TRANSCRIPT:")
        print("-" * 40)
        transcript = result.get('transcript', 'N/A')
        # Show first 500 chars with ellipsis if longer
        if len(transcript) > 500:
            print(f"{transcript[:500]}...")
            print(f"(Total: {len(transcript)} characters)")
        else:
            print(transcript)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 40)
        print(result.get('summary', 'N/A'))
        
        # SOP Validation
        print(f"\n✅ SOP VALIDATION:")
        print("-" * 40)
        sop = result.get('sop_validation', {})
        print(f"  Greeting:         {'✅' if sop.get('greeting') else '❌'}")
        print(f"  Identification:   {'✅' if sop.get('identification') else '❌'}")
        print(f"  Problem Statement:{'✅' if sop.get('problemStatement') else '❌'}")
        print(f"  Solution Offering:{'✅' if sop.get('solutionOffering') else '❌'}")
        print(f"  Closing:          {'✅' if sop.get('closing') else '❌'}")
        print(f"\n  Compliance Score: {sop.get('complianceScore', 0):.1f}")
        print(f"  Adherence Status: {sop.get('adherenceStatus', 'N/A')}")
        print(f"  Explanation: {sop.get('explanation', 'N/A')}")
        
        # Analytics
        print(f"\n📈 ANALYTICS:")
        print("-" * 40)
        analytics = result.get('analytics', {})
        print(f"  Payment Preference: {analytics.get('paymentPreference', 'N/A')}")
        print(f"  Rejection Reason:   {analytics.get('rejectionReason', 'N/A')}")
        print(f"  Sentiment:          {analytics.get('sentiment', 'N/A')}")
        
        # Keywords
        print(f"\n🔑 KEYWORDS:")
        print("-" * 40)
        keywords = result.get('keywords', [])
        if keywords:
            print(f"  {', '.join(keywords)}")
        else:
            print("  No keywords extracted")
        
        # Save full response to file
        output_file = f"response_{os.path.basename(audio_file)}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full response saved to: {output_file}")
        
        print("\n" + "=" * 60)
        
        return result
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The audio may be too long or the server is busy.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Is the server running?")
        print(f"   URL: {API_URL}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"   Response: {e.response.json()}")
            except:
                print(f"   Response: {e.response.text}")
        return None


def health_check():
    """Check if the API is running"""
    base_url = API_URL.replace("/api/call-analytics", "")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ API Health Check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API not reachable: {e}")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "test.mp3"
    language = sys.argv[2] if len(sys.argv) > 2 else "Tamil"
    
    # Validate language
    if language not in ["Tamil", "Hindi"]:
        print(f"⚠️ Warning: Language '{language}' may not be supported.")
        print("   Supported languages: Tamil, Hindi")
    
    # Run health check first
    print("🔍 Checking API health...")
    if health_check():
        print()
        test_call_analytics(audio_file, language)
    else:
        print("\n💡 Tip: Start the server with:")
        print("   uvicorn app:app --reload --host 0.0.0.0 --port 8000")

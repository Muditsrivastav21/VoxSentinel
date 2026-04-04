"""
VoxSentinel API Live Test Suite
================================
Tests all API endpoints with real requests to verify functionality.

Run with: python test_api_live.py
Backend must be running: uvicorn app:app --reload --port 8000
"""

import requests
import base64
import json
import os
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("API_KEY", "YOUR_API_KEY_HERE")  # Set this before running

# Test audio file (use any .mp3 or .wav file)
TEST_AUDIO_FILE = "test_file_final.mp3"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_header("Test 1: Health Check (GET /)")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_info(f"Message: {data.get('message', 'N/A')}")
            print_info(f"Status: {data.get('status', 'N/A')}")
            print_info(f"Providers: STT={data.get('providers', {}).get('stt', 'N/A')}, AI={data.get('providers', {}).get('ai', 'N/A')}")
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_api_docs():
    """Test 2: API documentation endpoint"""
    print_header("Test 2: API Documentation (GET /docs)")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        
        if response.status_code == 200:
            print_success(f"Swagger UI available at {BASE_URL}/docs")
            return True
        else:
            print_error(f"Docs not available: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_stats_endpoint():
    """Test 3: Statistics endpoint"""
    print_header("Test 3: Statistics (GET /api/stats)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_info(f"Total Calls: {data.get('total_calls', 'N/A')}")
            print_info(f"Average Compliance: {data.get('average_compliance', 'N/A')}")
            print_info(f"Sentiment Distribution: {data.get('sentiment_distribution', {})}")
            print_info(f"Payment Preferences: {data.get('payment_distribution', {})}")
            return True
        else:
            print_warning(f"Status {response.status_code}: {data}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_history_endpoint():
    """Test 4: Call history endpoint"""
    print_header("Test 4: Call History (GET /api/history)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/history?limit=5", timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            calls = data.get('calls', [])
            print_info(f"Total in DB: {data.get('total', 0)}")
            print_info(f"Retrieved: {len(calls)} calls")
            
            if calls:
                print_info("Sample call:")
                call = calls[0]
                print(f"    - ID: {call.get('id', 'N/A')[:8]}...")
                print(f"    - Compliance: {call.get('compliance_score', 'N/A')}")
                print(f"    - Sentiment: {call.get('sentiment', 'N/A')}")
            return True
        else:
            print_warning(f"Status {response.status_code}: {data}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_call_analytics_with_audio():
    """Test 5: Main analysis endpoint with real audio"""
    print_header("Test 5: Call Analytics (POST /api/call-analytics)")
    
    # Check if test audio file exists
    audio_path = Path(TEST_AUDIO_FILE)
    if not audio_path.exists():
        # Try to find any audio file
        audio_files = list(Path(".").glob("*.mp3")) + list(Path(".").glob("*.wav"))
        if audio_files:
            audio_path = audio_files[0]
            print_info(f"Using found audio file: {audio_path}")
        else:
            print_warning("No audio file found. Testing with text-only mode...")
            return test_call_analytics_text_only()
    
    try:
        # Read and encode audio file
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print_info(f"Audio file: {audio_path} ({len(audio_bytes)} bytes)")
        
        # Prepare request
        payload = {
            "audio": audio_base64,
            "language": "English"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        print_info("Sending request (this may take 10-30 seconds)...")
        
        response = requests.post(
            f"{BASE_URL}/api/call-analytics",
            json=payload,
            headers=headers,
            timeout=120  # 2 minute timeout for transcription
        )
        
        data = response.json()
        
        if response.status_code == 200:
            print_success(f"Status: {response.status_code}")
            print_success("Analysis completed successfully!")
            
            # Print results
            print(f"\n{Colors.BOLD}📋 ANALYSIS RESULTS:{Colors.END}")
            print(f"  Analysis ID: {data.get('analysis_id', 'N/A')}")
            print(f"  Language: {data.get('language', 'N/A')}")
            
            # Transcript
            transcript = data.get('transcript', '')
            print(f"\n  📝 Transcript ({len(transcript)} chars):")
            print(f"     {transcript[:200]}{'...' if len(transcript) > 200 else ''}")
            
            # Summary
            print(f"\n  📊 Summary:")
            print(f"     {data.get('summary', 'N/A')}")
            
            # SOP Validation
            print(f"\n  ✅ SOP Validation:")
            sop = data.get('sop_validation', {})
            print(f"     Greeting: {'✓' if sop.get('greeting') else '✗'}")
            print(f"     Identification: {'✓' if sop.get('identification') else '✗'}")
            print(f"     Problem Statement: {'✓' if sop.get('problemStatement') else '✗'}")
            print(f"     Solution Offering: {'✓' if sop.get('solutionOffering') else '✗'}")
            print(f"     Closing: {'✓' if sop.get('closing') else '✗'}")
            print(f"     Compliance Score: {sop.get('complianceScore', 'N/A')}")
            print(f"     Adherence: {sop.get('adherenceStatus', 'N/A')}")
            
            # Analytics
            analytics = data.get('analytics', {})
            print(f"\n  📈 Analytics:")
            print(f"     Sentiment: {analytics.get('sentiment', 'N/A')}")
            print(f"     Payment Preference: {analytics.get('paymentPreference', 'N/A')}")
            print(f"     Rejection Reason: {analytics.get('rejectionReason', 'N/A')}")
            
            # Keywords
            keywords = data.get('keywords', [])
            print(f"\n  🏷️  Keywords: {', '.join(keywords[:10])}")
            
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            print_error(f"Error: {data.get('detail', data)}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out (>120s). Check if Groq API is working.")
        return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_call_analytics_text_only():
    """Test analysis endpoint with text transcript only (no audio)"""
    print_info("Testing text-only analysis...")
    
    # Create a test request without audio
    payload = {
        "audio": "",  # Empty audio
        "language": "English",
        "transcript": """Hello, this is customer service, how may I help you today?
        Hi, I'm calling about my account balance. I'd like to know the payment options available.
        Sure, I can help you with that. Your current balance is $500. We offer EMI options of 3, 6, or 12 months.
        That sounds great. I'd like to go with the 6-month EMI option.
        Perfect! I've set that up for you. Is there anything else I can help you with today?
        No, that's all. Thank you for your help!
        You're welcome. Have a great day!"""
    }
    
    # Note: This endpoint may not support text-only input
    # This is just a fallback test
    print_warning("Text-only mode not fully supported. Use actual audio file for proper testing.")
    return False

def test_provider_info():
    """Test 6: Check configured providers"""
    print_header("Test 6: Provider Configuration Check")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        data = response.json()
        
        providers = data.get('providers', {})
        stt = providers.get('stt', 'unknown')
        ai = providers.get('ai', 'unknown')
        
        print_info(f"Speech-to-Text Provider: {stt.upper()}")
        print_info(f"AI Analysis Provider: {ai.upper()}")
        
        if stt == 'groq' and ai == 'groq':
            print_success("Using Groq (FREE) for both STT and Analysis")
        elif stt == 'assemblyai':
            print_info("Using AssemblyAI for STT (5 hrs/month free)")
        elif stt == 'openai':
            print_warning("Using OpenAI (PAID) - check your quota")
        
        return True
    except Exception as e:
        print_error(f"Check failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          VoxSentinel API Live Test Suite                 ║")
    print("║          Testing all endpoints and features              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    results = {}
    
    # Run tests
    results['Health Check'] = test_health_check()
    results['API Docs'] = test_api_docs()
    results['Provider Config'] = test_provider_info()
    results['Stats Endpoint'] = test_stats_endpoint()
    results['History Endpoint'] = test_history_endpoint()
    results['Call Analytics'] = test_call_analytics_with_audio()
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        if passed_test:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! API is working correctly.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check the errors above.{Colors.END}")
    
    return passed == total

if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check if backend is running
    print_info(f"Testing API at {BASE_URL}")
    print_info("Make sure backend is running: uvicorn app:app --reload --port 8000\n")
    
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except:
        print_error("Cannot connect to backend. Please start it first:")
        print_info("  cd d:\\AI-Voice-Detection-main\\AI-Voice-Detection-main")
        print_info("  uvicorn app:app --reload --port 8000")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

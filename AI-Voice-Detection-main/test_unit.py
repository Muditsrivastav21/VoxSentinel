"""
VoxSentinel Backend Unit Tests

Tests for the core API functions including:
- Health endpoints
- Audio transcription (mocked)
- GPT analysis (mocked)
- API authentication
- Rate limiting

Run with: pytest test_unit.py -v
"""

import pytest
import base64
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the FastAPI app
from app import app, transcribe_audio, analyze_transcript, check_rate_limit, rate_limit_store

# Test client
client = TestClient(app)

# Test API key (must match .env)
TEST_API_KEY = os.getenv("API_KEY", "test_key_for_unit_tests")


# ==========================
# HEALTH ENDPOINT TESTS
# ==========================

class TestHealthEndpoints:
    """Tests for health check endpoints"""
    
    def test_ping(self):
        """Test /ping returns pong"""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json()["status"] == "pong"
    
    def test_health(self):
        """Test /health returns system status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "VoxSentinel API"
        assert "version" in data
        assert "openai_configured" in data
        assert "timestamp" in data
    
    def test_root(self):
        """Test / returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to VoxSentinel API"
        assert "docs" in data


# ==========================
# AUTHENTICATION TESTS
# ==========================

class TestAuthentication:
    """Tests for API key authentication"""
    
    def test_missing_api_key(self):
        """Test request without API key is rejected"""
        response = client.post(
            "/api/call-analytics",
            json={"audio_base64": "dGVzdA==", "language": "en"}
        )
        assert response.status_code == 401
        assert "API key" in response.json()["detail"]
    
    def test_invalid_api_key(self):
        """Test request with invalid API key is rejected"""
        response = client.post(
            "/api/call-analytics",
            json={"audio_base64": "dGVzdA==", "language": "en"},
            headers={"X-API-Key": "invalid_key_12345"}
        )
        assert response.status_code == 401


# ==========================
# INPUT VALIDATION TESTS
# ==========================

class TestInputValidation:
    """Tests for request validation"""
    
    def test_empty_audio_rejected(self):
        """Test empty audio_base64 is rejected"""
        response = client.post(
            "/api/call-analytics",
            json={"audio_base64": "", "language": "en"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 422
    
    def test_invalid_language_rejected(self):
        """Test invalid language code is rejected"""
        response = client.post(
            "/api/call-analytics",
            json={"audio_base64": "dGVzdA==", "language": "invalid123"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 422
    
    def test_valid_languages_accepted(self):
        """Test valid language codes pass validation"""
        from app import CallAnalyticsRequest
        from pydantic import ValidationError
        
        valid_langs = ["en", "hi", "es", "fr", "de", "zh", "ja", "ta"]
        for lang in valid_langs:
            try:
                req = CallAnalyticsRequest(audio_base64="dGVzdA==", language=lang)
                assert req.language == lang
            except ValidationError:
                pytest.fail(f"Language {lang} should be valid")


# ==========================
# RATE LIMITING TESTS
# ==========================

class TestRateLimiting:
    """Tests for rate limiting functionality"""
    
    def setup_method(self):
        """Clear rate limit store before each test"""
        rate_limit_store.clear()
    
    def test_rate_limit_allows_requests(self):
        """Test rate limiter allows requests under limit"""
        client_id = "test_client_1"
        allowed = check_rate_limit(client_id, max_requests=5, window_seconds=60)
        assert allowed is True
    
    def test_rate_limit_tracks_requests(self):
        """Test rate limiter tracks request count"""
        client_id = "test_client_2"
        for i in range(3):
            check_rate_limit(client_id, max_requests=5, window_seconds=60)
        
        assert client_id in rate_limit_store
        assert rate_limit_store[client_id]["count"] == 3
    
    def test_rate_limit_blocks_excess(self):
        """Test rate limiter blocks requests over limit"""
        client_id = "test_client_3"
        # Exhaust the limit
        for i in range(5):
            check_rate_limit(client_id, max_requests=5, window_seconds=60)
        
        # Next request should be blocked
        allowed = check_rate_limit(client_id, max_requests=5, window_seconds=60)
        assert allowed is False


# ==========================
# TRANSCRIPTION TESTS (MOCKED)
# ==========================

class TestTranscription:
    """Tests for audio transcription with mocked OpenAI"""
    
    @patch('app.client')
    def test_transcribe_audio_success(self, mock_openai):
        """Test successful transcription returns text"""
        mock_openai.audio.transcriptions.create.return_value = MagicMock(
            text="Hello, this is a test call about your account."
        )
        
        audio_base64 = base64.b64encode(b"fake audio data").decode()
        result = transcribe_audio(audio_base64, "en")
        
        assert result == "Hello, this is a test call about your account."
        mock_openai.audio.transcriptions.create.assert_called_once()
    
    @patch('app.client')
    def test_transcribe_audio_error_handling(self, mock_openai):
        """Test transcription error is handled gracefully"""
        mock_openai.audio.transcriptions.create.side_effect = Exception("OpenAI API Error")
        
        audio_base64 = base64.b64encode(b"fake audio").decode()
        
        with pytest.raises(Exception) as exc_info:
            transcribe_audio(audio_base64, "en")
        
        assert "OpenAI API Error" in str(exc_info.value)


# ==========================
# ANALYSIS TESTS (MOCKED)
# ==========================

class TestAnalysis:
    """Tests for GPT transcript analysis with mocked OpenAI"""
    
    @patch('app.client')
    def test_analyze_transcript_success(self, mock_openai):
        """Test successful analysis returns proper structure"""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="""{
                "summary": "Customer called about payment issue",
                "sop_validation": {
                    "greeting": true,
                    "identification": true,
                    "problemStatement": true,
                    "solutionOffering": true,
                    "closing": true,
                    "complianceScore": 1.0,
                    "adherenceStatus": "Compliant",
                    "explanation": "All SOP requirements met"
                },
                "analytics": {
                    "paymentPreference": "Credit Card",
                    "rejectionReason": "None",
                    "sentiment": "Positive"
                },
                "keywords": ["payment", "credit card", "account"]
            }"""))
        ]
        mock_openai.chat.completions.create.return_value = mock_response
        
        result = analyze_transcript("Hello, I need help with my payment.", "en")
        
        assert "summary" in result
        assert "sop_validation" in result
        assert "analytics" in result
        assert result["sop_validation"]["greeting"] is True
        assert result["sop_validation"]["complianceScore"] == 1.0
        assert result["analytics"]["sentiment"] == "Positive"
        assert "keywords" in result


# ==========================
# HISTORY ENDPOINTS TESTS
# ==========================

class TestHistoryEndpoints:
    """Tests for call history endpoints"""
    
    def test_history_requires_auth(self):
        """Test /api/history requires authentication"""
        response = client.get("/api/history")
        # Should fail without X-API-Key header
        assert response.status_code in [401, 422]
    
    def test_history_with_auth(self):
        """Test /api/history returns data with valid auth"""
        response = client.get(
            "/api/history",
            headers={"X-API-Key": TEST_API_KEY}
        )
        # Returns 200 with empty data or 503 if no DB
        assert response.status_code in [200, 503]


# ==========================
# STATS ENDPOINTS TESTS
# ==========================

class TestStatsEndpoints:
    """Tests for stats endpoints"""
    
    def test_stats_requires_auth(self):
        """Test /api/stats requires authentication"""
        response = client.get("/api/stats")
        assert response.status_code in [401, 422]
    
    def test_stats_with_auth(self):
        """Test /api/stats returns data with valid auth"""
        response = client.get(
            "/api/stats",
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code in [200, 503]


# ==========================
# INTEGRATION TESTS (MOCKED)
# ==========================

class TestFullAnalysisFlow:
    """Integration tests for full analysis flow"""
    
    def setup_method(self):
        """Clear rate limit store before each test"""
        rate_limit_store.clear()
    
    @patch('app.transcribe_audio')
    @patch('app.analyze_transcript')
    @patch('app.save_analysis_to_db')
    def test_full_analysis_flow(self, mock_save, mock_analyze, mock_transcribe):
        """Test complete analysis flow from audio to response"""
        # Setup mocks
        mock_transcribe.return_value = "Hello, this is a test call about payment."
        mock_analyze.return_value = {
            "summary": "Customer called about payment",
            "sop_validation": {
                "greeting": True,
                "identification": True,
                "problemStatement": True,
                "solutionOffering": True,
                "closing": True,
                "complianceScore": 1.0,
                "adherenceStatus": "Compliant",
                "explanation": "All SOP requirements met"
            },
            "analytics": {
                "paymentPreference": "Credit Card",
                "rejectionReason": "None",
                "sentiment": "Positive"
            },
            "keywords": ["payment", "credit card"]
        }
        mock_save.return_value = "test-uuid-123"
        
        # Make request
        audio_base64 = base64.b64encode(b"fake audio data").decode()
        response = client.post(
            "/api/call-analytics",
            json={"audio_base64": audio_base64, "language": "en"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "transcript" in data
        assert "sop_validation" in data
        assert data["sop_validation"]["complianceScore"] == 1.0
        assert data["sop_validation"]["adherenceStatus"] == "Compliant"


# ==========================
# SWAGGER/OPENAPI TESTS
# ==========================

class TestOpenAPI:
    """Tests for API documentation"""
    
    def test_swagger_ui_available(self):
        """Test Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self):
        """Test ReDoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Test OpenAPI JSON schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/api/call-analytics" in data["paths"]


# ==========================
# RUN TESTS
# ==========================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

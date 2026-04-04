@echo off
echo.
echo ========================================
echo VoxSentinel - Quick API Test
echo ========================================
echo.

REM Test health endpoint
echo Testing Health Endpoint...
curl -s http://127.0.0.1:8000/ | python -c "import sys,json; d=json.load(sys.stdin); print(f'Status: {d.get(\"status\")}'); print(f'Providers: STT={d.get(\"providers\",{}).get(\"stt\")}, AI={d.get(\"providers\",{}).get(\"ai\")}')"
echo.

REM Test stats endpoint
echo Testing Stats Endpoint...
curl -s http://127.0.0.1:8000/api/stats | python -c "import sys,json; d=json.load(sys.stdin); print(f'Total Calls: {d.get(\"total_calls\", 0)}'); print(f'Avg Compliance: {d.get(\"avg_compliance_score\", 0)}')"
echo.

echo ========================================
echo For full API test, run:
echo   python test_api_live.py
echo ========================================

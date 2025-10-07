"""
Full test script for URL Shortener project.
This script will:
1. Create a short URL
2. Visit the redirect endpoint
3. Verify analytics increment
"""

import requests
import time

# Backend base URL (FastAPI)
BACKEND_URL = "http://10.95.193.234:8000"

# Test target URL
TEST_LONG_URL = "https://www.wikipedia.org/"

def test_create_short_url():
    print("🔹 Testing /api/create ...")
    response = requests.post(f"{BACKEND_URL}/api/create", json={"url": TEST_LONG_URL})
    assert response.status_code == 200, f"Create failed: {response.text}"
    data = response.json()
    print("✅ Short URL created:", data)
    assert "short_url" in data
    return data["short_url"]

def test_redirect(short_url):
    print("\n🔹 Testing redirect ...")
    response = requests.get(short_url, allow_redirects=False)
    assert response.status_code in (301, 302, 303, 307, 308), f"Redirect failed: {response.status_code}"
    location = response.headers.get("Location")
    print(f"✅ Redirected with status {response.status_code} to: {location}")
    assert location == TEST_LONG_URL

def test_analytics(short_url):
    print("\n🔹 Testing /api/analytics ...")
    short_id = short_url.strip().split("/")[-1]
    response = requests.get(f"{BACKEND_URL}/api/analytics/{short_id}")
    assert response.status_code == 200, f"Analytics failed: {response.text}"
    data = response.json()
    print("✅ Analytics data:", data)
    assert "clicks" in data
    return data["clicks"]

def main():
    print("\n" + "=" * 100 + "\n")
    print("🚀 Starting URL Shortener tests...\n")

    short_url = test_create_short_url()
    time.sleep(1)  
    print("\n" + "=" * 100 + "\n")

    test_redirect(short_url)
    time.sleep(2)  
    print("\n" + "=" * 100 + "\n")

    clicks_before = test_analytics(short_url)
    print(f"📊 Clicks before: {clicks_before}")

    # Trigger another visit
    requests.get(short_url, allow_redirects=False)
    time.sleep(3)  

    clicks_after = test_analytics(short_url)
    print(f"📊 Clicks after second visit: {clicks_after}")

    assert clicks_after >= clicks_before + 1, "❌ Click count not increasing!"

    print("\n✅ All tests passed successfully!")
    print("\n" + "=" * 100 + "\n")

if __name__ == "__main__":
    main()


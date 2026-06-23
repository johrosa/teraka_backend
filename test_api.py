#!/usr/bin/env python
"""
Test script for Teraka Django API
Tests login, PostgREST proxy, and other endpoints
"""

import requests
import json
import sys
import os
from urllib.parse import urljoin

DJANGO_PORT = os.environ.get('DJANGO_PORT', '8050')
POSTGREST_PORT = os.environ.get('POSTGREST_PORT', '3050')

BASE_URL = f"http://localhost:{DJANGO_PORT}"
POSTGREST_DIRECT = f"http://localhost:{POSTGREST_PORT}"
def test_health():
    """Test basic connectivity to Django"""
    print("\n🔍 Testing Django health...")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   ✓ Django responding: {r.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ Django not accessible: {e}")
        return False

def test_login():
    """Test login endpoint"""
    print("\n🔐 Testing login endpoint...")
    try:
        payload = {
            "username": "postgres",
            "password": "ad,in"
        }
        r = requests.post(f"{BASE_URL}/api/login/", json=payload, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Login successful")
            print(f"      Access token: {data.get('access', '')[:50]}...")
            return data.get('access')
        else:
            print(f"   ⚠️  Login returned {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Login endpoint error: {e}")
        return None

def test_postgrest_direct():
    """Test direct PostgREST access"""
    print("\n📡 Testing direct PostgREST access...")
    try:
        r = requests.get(f"{POSTGREST_DIRECT}/communes?limit=1", timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ PostgREST responding: {len(data)} records")
            return True
        else:
            print(f"   ⚠️  PostgREST returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Direct PostgREST error: {e}")
        return False

def test_postgrest_proxy(access_token):
    """Test PostgREST via Django proxy"""
    print("\n🔗 Testing PostgREST via Django proxy (/api/data/)...")
    try:
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        r = requests.get(f"{BASE_URL}/api/data/communes?limit=1", headers=headers, timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ Proxy working: {len(data)} records")
            return True
        else:
            print(f"   ⚠️  Proxy returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Proxy error: {e}")
        return False

def test_postgrest_info():
    """Test info endpoint"""
    print("\n📋 Testing PostgREST info endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/api/postgrest-info/", timeout=5)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   ✓ PostgREST config:")
            print(f"      Upstream: {data.get('postgrest_upstream')}")
            print(f"      Port: {data.get('postgrest_port')}")
            return True
        else:
            print(f"   ❌ Info endpoint error: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Info endpoint error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 TERAKA DJANGO API TEST")
    print("=" * 60)
    
    results = {
        'health': test_health(),
        'info': test_postgrest_info(),
        'postgrest_direct': test_postgrest_direct(),
    }
    
    access_token = test_login()
    results['login'] = access_token is not None
    
    results['proxy'] = test_postgrest_proxy(access_token) if access_token else False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    for test, result in results.items():
        status = "✓" if result else "❌"
        print(f"{status} {test}")
    
    all_pass = all(results.values())
    print("\n" + ("🎉 All tests passed!" if all_pass else "⚠️  Some tests failed"))
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())

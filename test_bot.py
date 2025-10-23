#!/usr/bin/env python3
"""
NICE-BOT Test Script
Test the bot functionality locally before deployment
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_database():
    """Test database initialization"""
    print("🗄️ Testing database...")
    try:
        from db import init_database, add_user, get_user, get_user_stats
        
        # Initialize database
        init_database()
        print("✅ Database initialized successfully")
        
        # Test user operations
        test_user_id = "123456789"
        add_user(test_user_id, "testuser", "Test User")
        user = get_user(test_user_id)
        
        if user:
            print("✅ User operations working")
        else:
            print("❌ User operations failed")
            return False
        
        # Test stats
        stats = get_user_stats()
        print(f"✅ Stats: {stats['total_users']} users, {stats['total_commands']} commands")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_apis():
    """Test external APIs"""
    print("\n🌐 Testing external APIs...")
    
    try:
        import aiohttp
        import ssl
        
        # Create SSL context that's more permissive for testing
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Test LibreTranslate
            try:
                libretranslate_url = os.getenv("LIBRETRANSLATE_URL", "https://libretranslate.com")
                async with session.get(f"{libretranslate_url}/languages") as response:
                    if response.status == 200:
                        print("✅ LibreTranslate API accessible")
                    else:
                        print("⚠️ LibreTranslate API may have issues")
            except Exception as e:
                print(f"⚠️ LibreTranslate test failed: {e}")
            
            # Test Open-Meteo
            try:
                async with session.get("https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current_weather=true") as response:
                    if response.status == 200:
                        print("✅ Open-Meteo API accessible")
                    else:
                        print("⚠️ Open-Meteo API may have issues")
            except Exception as e:
                print(f"⚠️ Open-Meteo test failed: {e}")
            
            # Test other APIs
            apis_to_test = [
                ("ExchangeRate.host", "https://api.exchangerate.host/latest"),
                ("Quotable", "https://api.quotable.io/random"),
                ("JokeAPI", "https://v2.jokeapi.dev/joke/Programming?type=single"),
                ("Wikipedia", "https://fr.wikipedia.org/api/rest_v1/page/summary/Python")
            ]
            
            for name, url in apis_to_test:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            print(f"✅ {name} API accessible")
                        else:
                            print(f"⚠️ {name} API may have issues")
                except Exception as e:
                    print(f"⚠️ {name} test failed: {e}")
                    
    except Exception as e:
        print(f"❌ API testing failed: {e}")

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing environment variables...")
    
    required_vars = ["BOT_TOKEN"]
    optional_vars = ["TMDB_API_KEY", "MEDIASTACK_API_KEY", "ADMIN_USER_ID"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️ Missing optional variables: {', '.join(missing_optional)}")
        print("   Some features may not work without these.")
    
    return True

def test_imports():
    """Test all required imports"""
    print("\n📦 Testing imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "telegram",
        "aiohttp",
        "qrcode",
        "fpdf",
        "PIL"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

async def test_bot_setup():
    """Test bot setup without starting"""
    print("\n🤖 Testing bot setup...")
    
    try:
        from bot import setup_bot
        
        if not os.getenv("BOT_TOKEN"):
            print("⚠️ BOT_TOKEN not set, skipping bot setup test")
            return True
        
        application = setup_bot()
        print("✅ Bot application created successfully")
        print(f"✅ Bot handlers registered: {len(application.handlers)}")
        
        return True
    except Exception as e:
        print(f"❌ Bot setup failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 NICE-BOT Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Database", test_database),
        ("APIs", test_apis),
        ("Bot Setup", test_bot_setup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bot is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())

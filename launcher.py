#!/usr/bin/env python3
"""
Ollama Chat 统一启动器
支持HTTP和HTTPS模式，自动管理SSL证书
"""

import os
import sys
import argparse
from utils.ssl_manager import SSLCertificateManager


def print_banner():
    """显示启动横幅"""
    print("============================================================")
    print("    🤖 Ollama Chat Server Launcher")
    print("============================================================")
    print()


def start_http_server():
    """启动HTTP服务器"""
    print("🌐 Starting HTTP server...")
    
    # 首先测试导入
    print("🔍 Checking dependencies...")
    try:
        import uvicorn
        from core.config import config
        print(f"  ✅ Config loaded (Model: {config.ollama_model})")
        
        # 测试FAISS功能
        try:
            from utils.faiss_integration import is_rag_available
            if is_rag_available():
                print("  ✅ Document Q&A available")
            else:
                print("  ⚠️  Document Q&A unavailable (missing dependencies)")
        except:
            print("  ⚠️  Document Q&A module not loaded")
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    print("Access URLs:")
    print("   - Chat Interface: http://localhost:8000/chat")
    print("   - Document Q&A: http://localhost:8000/static/rag_chat.html")
    print("   - Gradio Interface: http://localhost:8000/gradio")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Mobile Chat: http://YOUR_IP:8000/chat")
    print("   - Mobile Document Q&A: http://YOUR_IP:8000/static/rag_chat.html")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


def start_https_server():
    """启动HTTPS服务器"""
    print("🔒 Starting HTTPS server...")
    
    # 检查和生成SSL证书
    ssl_manager = SSLCertificateManager()
    
    if not ssl_manager.certificate_exists():
        print("SSL certificate not found. Generating new certificate...")
        if not ssl_manager.generate_certificate():
            print("❌ Failed to generate SSL certificate")
            sys.exit(1)
    elif not ssl_manager.certificate_valid():
        print("SSL certificate is invalid or expiring soon. Regenerating...")
        if not ssl_manager.generate_certificate():
            print("❌ Failed to regenerate SSL certificate")
            sys.exit(1)
    else:
        print("✅ Valid SSL certificate found")
    
    print()
    print("📋 HTTPS Server Configuration:")
    print(f"   - Port: 8443")
    print(f"   - Certificate: {ssl_manager.cert_path}")
    print(f"   - Private Key: {ssl_manager.key_path}")
    print()
    print("🚀 Starting HTTPS server...")
    print("Access URLs:")
    print("   - Secure Chat Interface: https://localhost:8443/chat")
    print("   - Document Q&A: https://localhost:8443/static/rag_chat.html")
    print("   - Gradio Interface: https://localhost:8443/gradio")
    print("   - API Documentation: https://localhost:8443/docs")
    print("   - Mobile Chat: https://YOUR_IP:8443/chat")
    print("   - Mobile Document Q&A: https://YOUR_IP:8443/static/rag_chat.html")
    print()
    print("⚠️  Browser Security Notice:")
    print("   - First visit will show 'Not Secure' warning")
    print("   - Click 'Advanced' → 'Proceed to localhost'")
    print("   - This is normal for self-signed certificates")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        import uvicorn
        uvicorn.run(
            "app:app", 
            host="0.0.0.0", 
            port=8443, 
            ssl_keyfile=ssl_manager.key_path,
            ssl_certfile=ssl_manager.cert_path,
            reload=True
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Ollama Chat Server Launcher')
    parser.add_argument('--https', action='store_true', 
                       help='Start in HTTPS mode (default: HTTP)')
    parser.add_argument('--ssl-only', action='store_true',
                       help='Generate SSL certificate only, don\'t start server')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.ssl_only:
        # 只生成SSL证书
        ssl_manager = SSLCertificateManager()
        success = ssl_manager.generate_certificate(force_regenerate=True)
        sys.exit(0 if success else 1)
    
    try:
        # 检查核心依赖
        from core.config import config
        
        if args.https:
            start_https_server()
        else:
            start_http_server()
            
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        print("Please ensure config.py exists and is properly configured")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
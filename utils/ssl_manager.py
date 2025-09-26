#!/usr/bin/env python3
"""
SSL证书管理器
统一管理SSL证书的生成、验证和更新
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta, timezone


class SSLCertificateManager:
    """SSL证书管理器"""
    
    def __init__(self, cert_dir='ssl'):
        self.cert_dir = cert_dir
        self.cert_path = os.path.join(cert_dir, 'server.crt')
        self.key_path = os.path.join(cert_dir, 'server.key')
    
    def certificate_exists(self):
        """检查证书是否存在"""
        return os.path.exists(self.cert_path) and os.path.exists(self.key_path)
    
    def certificate_valid(self, days_ahead=30):
        """检查证书是否有效（未过期且至少还有指定天数有效期）"""
        if not self.certificate_exists():
            return False
        
        try:
            # 使用cryptography库检查证书有效期
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
            
            with open(self.cert_path, 'rb') as cert_file:
                cert = x509.load_pem_x509_certificate(cert_file.read())
                
            # 检查证书是否在未来days_ahead天内过期
            # 使用UTC时间避免deprecation警告
            try:
                expiry_date = cert.not_valid_after_utc
                warning_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            except AttributeError:
                # 兼容旧版本cryptography
                expiry_date = cert.not_valid_after
                warning_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            return expiry_date > warning_date
            
        except Exception:
            # 如果无法验证证书，假设需要重新生成
            return False
    
    def generate_with_openssl(self):
        """使用OpenSSL生成证书"""
        try:
            # 检查OpenSSL是否可用
            result = subprocess.run(['openssl', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # 创建SSL目录
            os.makedirs(self.cert_dir, exist_ok=True)
            
            print("Using OpenSSL to generate certificate...")
            
            # 生成私钥
            subprocess.run([
                'openssl', 'genrsa', '-out', self.key_path, '2048'
            ], check=True, capture_output=True)
            
            # 生成自签名证书
            subprocess.run([
                'openssl', 'req', '-new', '-x509', '-key', self.key_path,
                '-out', self.cert_path, '-days', '365',
                '-subj', '/C=CN/ST=Beijing/L=Beijing/O=OllamaChat/CN=localhost'
            ], check=True, capture_output=True)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def generate_with_python(self):
        """使用Python cryptography库生成证书"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import ipaddress
            
        except ImportError:
            print("ERROR: cryptography library not installed")
            print("Please install it with: pip install cryptography")
            return False
        
        try:
            print("Using Python cryptography library to generate certificate...")
            
            # 创建SSL目录
            os.makedirs(self.cert_dir, exist_ok=True)
            
            # 生成私钥
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 创建证书主题
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OllamaChat"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            # 创建证书
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1"))
                ]),
                critical=False,
            ).sign(key, hashes.SHA256())
            
            # 保存私钥
            with open(self.key_path, 'wb') as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # 保存证书
            with open(self.cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to generate certificate: {e}")
            return False
    
    def generate_certificate(self, force_regenerate=False):
        """生成SSL证书"""
        if not force_regenerate and self.certificate_valid():
            print("✅ Valid SSL certificate already exists")
            return True
        
        print("============================================================")
        print("    SSL Certificate Generator")
        print("============================================================")
        print()
        
        if not force_regenerate and self.certificate_exists():
            print("⚠️  Certificate exists but will expire soon or is invalid")
        
        print("Generating SSL self-signed certificate...")
        print("Note: Self-signed certificates are for development only")
        print()
        
        # 首先尝试OpenSSL
        if self.generate_with_openssl():
            print("✅ Certificate generated successfully with OpenSSL")
        elif self.generate_with_python():
            print("✅ Certificate generated successfully with Python")
        else:
            print("❌ Failed to generate certificate")
            return False
        
        print()
        print("Certificate files created:")
        print(f"  - Private key: {self.key_path}")
        print(f"  - Certificate: {self.cert_path}")
        print()
        print("IMPORTANT NOTES:")
        print("  - This is a self-signed certificate")
        print("  - Browser will show security warning on first visit")
        print("  - Click 'Advanced' then 'Proceed to localhost' to continue")
        print("  - For production use, obtain CA-signed certificates")
        print()
        
        return True
    
    def get_certificate_info(self):
        """获取证书信息"""
        if not self.certificate_exists():
            return None
        
        try:
            from cryptography import x509
            
            with open(self.cert_path, 'rb') as cert_file:
                cert = x509.load_pem_x509_certificate(cert_file.read())
            
            return {
                'subject': cert.subject.rfc4514_string(),
                'issuer': cert.issuer.rfc4514_string(),
                'not_valid_before': cert.not_valid_before,
                'not_valid_after': cert.not_valid_after,
                'serial_number': cert.serial_number
            }
        except Exception:
            return None


def create_ssl_context(cert_dir='ssl'):
    """创建SSL上下文"""
    import ssl
    
    manager = SSLCertificateManager(cert_dir)
    
    # 确保证书存在且有效
    if not manager.certificate_exists() or not manager.certificate_valid():
        print("🔐 正在生成SSL证书...")
        success = manager.generate_certificate()
        if not success:
            raise Exception("SSL证书生成失败")
    
    # 创建SSL上下文
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(manager.cert_path, manager.key_path)
    
    return ssl_context


def main():
    """命令行接口"""
    manager = SSLCertificateManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        success = manager.generate_certificate(force_regenerate=True)
    else:
        success = manager.generate_certificate()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Test Supabase connection with both direct and pooler URLs
This will verify the IPv6 issue and test the fix
"""

import socket
import sys

def test_dns_resolution(hostname):
    """Test DNS resolution and check for IPv6/IPv4 addresses"""
    print(f"\n{'='*70}")
    print(f"DNS RESOLUTION TEST: {hostname}")
    print(f"{'='*70}")
    
    try:
        # Get all addresses
        addr_info = socket.getaddrinfo(hostname, 6543, socket.AF_UNSPEC, socket.SOCK_STREAM)
        
        ipv4_addresses = []
        ipv6_addresses = []
        
        for family, socktype, proto, canonname, sockaddr in addr_info:
            if family == socket.AF_INET:
                ipv4_addresses.append(sockaddr[0])
            elif family == socket.AF_INET6:
                ipv6_addresses.append(sockaddr[0])
        
        print(f"\nIPv4 addresses: {len(ipv4_addresses)}")
        for addr in ipv4_addresses:
            print(f"  - {addr}")
        
        print(f"\nIPv6 addresses: {len(ipv6_addresses)}")
        for addr in ipv6_addresses:
            print(f"  - {addr}")
        
        if ipv6_addresses and not ipv4_addresses:
            print(f"\n⚠️  WARNING: Only IPv6 addresses found!")
            print(f"   This will fail on Render (no IPv6 support)")
            return False
        elif ipv4_addresses:
            print(f"\n✅ IPv4 addresses available - Compatible with Render")
            return True
        else:
            print(f"\n❌ No addresses resolved")
            return False
            
    except Exception as e:
        print(f"\n❌ DNS resolution failed: {e}")
        return False


def test_connection(host, port, description):
    """Test actual TCP connection"""
    print(f"\n{'='*70}")
    print(f"CONNECTION TEST: {description}")
    print(f"{'='*70}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    
    try:
        # Try to connect with timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print(f"\nAttempting connection...")
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"✅ Connection successful!")
            sock.close()
            return True
        else:
            print(f"❌ Connection failed (error code: {result})")
            sock.close()
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution error: {e}")
        return False
    except socket.timeout:
        print(f"❌ Connection timeout (>10 seconds)")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_postgresql_connection(connection_string, description):
    """Test actual PostgreSQL connection"""
    print(f"\n{'='*70}")
    print(f"POSTGRESQL CONNECTION TEST: {description}")
    print(f"{'='*70}")
    
    try:
        import psycopg2
        
        # Hide password in output
        safe_string = connection_string
        if '@' in safe_string:
            parts = safe_string.split('@')
            user_part = parts[0].split(':')[0]
            safe_string = f"{user_part}:***@{parts[1]}"
        
        print(f"Connection string: {safe_string}")
        print(f"\nAttempting PostgreSQL connection...")
        
        conn = psycopg2.connect(
            connection_string,
            connect_timeout=10
        )
        
        print(f"✅ PostgreSQL connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"\nDatabase version: {version[:80]}...")
        
        cursor.close()
        conn.close()
        
        return True
        
    except ImportError:
        print(f"⚠️  psycopg2 not installed - skipping PostgreSQL test")
        print(f"   Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("SUPABASE CONNECTION DIAGNOSTIC TEST")
    print("="*70)
    print("\nThis test will:")
    print("1. Check DNS resolution (IPv4 vs IPv6)")
    print("2. Test TCP connections")
    print("3. Test PostgreSQL connections (if psycopg2 installed)")
    print("\n" + "="*70)
    
    # Test 1: Direct database URL (should have IPv6)
    direct_host = "db.ryoicrdifiqhqpsnjmdo.supabase.co"
    print(f"\n\n### TEST 1: DIRECT DATABASE URL (Current - WRONG)")
    dns1 = test_dns_resolution(direct_host)
    
    # Test 2: Session pooler URL (should have IPv4 only)
    pooler_host = "aws-0-us-east-1.pooler.supabase.com"
    print(f"\n\n### TEST 2: SESSION POOLER URL (Fix - CORRECT)")
    dns2 = test_dns_resolution(pooler_host)
    
    # Test 3: Try TCP connections (will likely fail without credentials)
    print(f"\n\n### TEST 3: TCP CONNECTION TESTS")
    print(f"\nNote: These may fail due to authentication, but we can test reachability")
    
    conn1 = test_connection(direct_host, 6543, "Direct Database")
    conn2 = test_connection(pooler_host, 6543, "Session Pooler")
    
    # Test 4: PostgreSQL connection (need credentials)
    print(f"\n\n### TEST 4: POSTGRESQL CONNECTION TESTS")
    print(f"\nNote: Requires valid credentials - enter password when prompted")
    print(f"(Press Enter to skip if you don't have the password)")
    
    password = input("\nEnter Supabase database password (or press Enter to skip): ").strip()
    
    if password:
        direct_url = f"postgresql://postgres:{password}@{direct_host}:6543/postgres"
        pooler_url = f"postgresql://postgres.ryoicrdifiqhqpsnjmdo:{password}@{pooler_host}:6543/postgres"
        
        pg1 = test_postgresql_connection(direct_url, "Direct Database URL")
        pg2 = test_postgresql_connection(pooler_url, "Session Pooler URL")
    else:
        print("\nSkipping PostgreSQL connection tests (no password provided)")
        pg1 = None
        pg2 = None
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    print(f"\nDirect Database URL ({direct_host}):")
    print(f"  DNS Resolution: {'✅ PASS' if dns1 else '❌ FAIL (IPv6 only)'}")
    print(f"  TCP Connection: {'✅ PASS' if conn1 else '❌ FAIL' if conn1 is not None else '⚠️  SKIPPED'}")
    print(f"  PostgreSQL:     {'✅ PASS' if pg1 else '❌ FAIL' if pg1 is not None else '⚠️  SKIPPED'}")
    
    print(f"\nSession Pooler URL ({pooler_host}):")
    print(f"  DNS Resolution: {'✅ PASS' if dns2 else '❌ FAIL'}")
    print(f"  TCP Connection: {'✅ PASS' if conn2 else '❌ FAIL' if conn2 is not None else '⚠️  SKIPPED'}")
    print(f"  PostgreSQL:     {'✅ PASS' if pg2 else '❌ FAIL' if pg2 is not None else '⚠️  SKIPPED'}")
    
    print(f"\n{'='*70}")
    print("RECOMMENDATION")
    print(f"{'='*70}")
    
    if dns2 and not dns1:
        print(f"\n✅ CONFIRMED: IPv6 issue exists on direct database URL")
        print(f"✅ SOLUTION: Use Session Pooler URL (IPv4 compatible)")
        print(f"\nUpdate Render environment variable:")
        print(f"  From: postgresql://postgres:[PASSWORD]@{direct_host}:6543/postgres")
        print(f"  To:   postgresql://postgres.ryoicrdifiqhqpsnjmdo:[PASSWORD]@{pooler_host}:6543/postgres")
    elif dns1 and dns2:
        print(f"\n⚠️  Both URLs have IPv4 addresses - may work from your machine")
        print(f"   However, Render may still prefer IPv6 if available")
        print(f"   Recommendation: Use Session Pooler URL to be safe")
    elif not dns2:
        print(f"\n❌ Session Pooler URL also has issues - investigate further")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

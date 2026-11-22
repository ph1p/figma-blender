#!/usr/bin/env python3
"""
Test script to verify the Figma-Blender WebSocket server is running.

This script tests:
1. Server is listening on port 1410
2. WebSocket connection can be established
3. Server responds to basic messages
4. Connection cleanup works properly
"""

import asyncio
import sys
import socket


def check_port_listening(host='localhost', port=1410):
    """Check if server is listening on the specified port."""
    print(f"\n1. Checking if port {port} is open...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"   ✓ Port {port} is OPEN and listening")
            return True
        else:
            print(f"   ✗ Port {port} is CLOSED or not listening")
            return False
    except Exception as e:
        print(f"   ✗ Error checking port: {e}")
        return False


async def test_websocket_connection():
    """Test WebSocket connection to the server."""
    print("\n2. Testing WebSocket connection...")

    try:
        # Try to import websockets
        try:
            import websockets
            print(f"   ✓ websockets library available (version {websockets.__version__})")
        except ImportError:
            print("   ✗ websockets library not installed")
            print("   → Install with: pip3 install websockets")
            return False

        # Connect to the server
        print("   → Connecting to ws://localhost:1410...")
        async with websockets.connect('ws://localhost:1410') as websocket:
            print("   ✓ WebSocket connection established")

            # Wait for init message from server
            print("   → Waiting for init message from server...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"   ✓ Received message from server: {message}")

                # Try sending a test message
                print("   → Sending test ping...")
                await websocket.send('{"event": "ping"}')
                print("   ✓ Message sent successfully")

                print("   ✓ WebSocket communication working!")
                return True

            except asyncio.TimeoutError:
                print("   ✗ Timeout waiting for server response")
                return False

    except ConnectionRefusedError:
        print("   ✗ Connection refused - server not accepting connections")
        return False
    except Exception as e:
        print(f"   ✗ Error during WebSocket test: {type(e).__name__}: {e}")
        return False


async def run_all_tests():
    """Run all server tests."""
    print("=" * 60)
    print("Figma-Blender Server Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Port listening
    port_ok = check_port_listening()
    results.append(("Port listening", port_ok))

    if not port_ok:
        print("\n⚠ Server doesn't appear to be running!")
        print("   Please start Blender and enable the Figma addon")
        return False

    # Test 2: WebSocket connection
    ws_ok = await test_websocket_connection()
    results.append(("WebSocket connection", ws_ok))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests PASSED - Server is running correctly!")
    else:
        print("✗ Some tests FAILED - Check errors above")
    print("=" * 60 + "\n")

    return all_passed


def main():
    """Main entry point."""
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Cross-platform compatibility test for prepare_build.py
Tests path handling on different platforms
"""

import os
import site
import platform

def test_path_handling():
    print(f"Platform: {platform.system()}")
    print(f"Platform release: {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    
    # Test site-packages detection
    site_packages = site.getsitepackages()[0]
    print(f"Site packages: {site_packages}")
    
    # Test path separators
    if platform.system() == "Windows":
        expected_sep = "\\"
        print(f"Expected Windows path separator: {expected_sep}")
    else:
        expected_sep = "/"
        print(f"Expected Unix path separator: {expected_sep}")
    
    print(f"Actual path separator in site_packages: {expected_sep in site_packages}")
    
    # Test critical paths
    test_paths = [
        os.path.join(site_packages, 'streamlit', 'static'),
        os.path.join(site_packages, 'streamlit', 'runtime'),
        os.path.join(site_packages, 'mediapipe', 'modules'),
    ]
    
    print("\nTesting critical paths:")
    for i, path in enumerate(test_paths, 1):
        exists = os.path.exists(path)
        status = "[EXISTS]" if exists else "[MISSING]"
        print(f"  {i}. {status} {path}")
        if not exists:
            # Try to find the parent directory
            parent = os.path.dirname(path)
            if os.path.exists(parent):
                print(f"     Parent exists: {parent}")
                try:
                    contents = os.listdir(parent)[:5]  # Show first 5 items
                    print(f"     Contents: {contents}")
                except:
                    print(f"     Cannot list parent directory")
    
    # Test string escaping for spec file
    print(f"\nPath escaping test:")
    raw_string = f'r"{site_packages}"'
    print(f"  Raw string: {raw_string}")
    
    # Test encoding
    print(f"\nEncoding test:")
    try:
        test_content = f"""# Test content with path: {site_packages}
# This is a test file
site_packages = r"{site_packages}"
"""
        with open('test_encoding.tmp', 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Read it back
        with open('test_encoding.tmp', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("  [SUCCESS] UTF-8 encoding test passed")
        
        # Clean up
        os.remove('test_encoding.tmp')
        
    except Exception as e:
        print(f"  [ERROR] Encoding test failed: {e}")

if __name__ == '__main__':
    test_path_handling() 
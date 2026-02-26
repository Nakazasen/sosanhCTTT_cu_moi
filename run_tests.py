import unittest
import os
import sys

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    # Tìm thư mục tests từ vị trí file run_tests.py
    current_dir = os.path.dirname(__file__)
    tests_dir = os.path.join(current_dir, 'tests')
    
    # Nếu thư mục tests không tồn tại hoặc rỗng, dùng thư mục hiện tại
    if not os.path.exists(tests_dir) or not os.listdir(tests_dir):
        tests_dir = current_dir
        
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        exit(0)
    else:
        exit(1)

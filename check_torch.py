import sys
print(f"Python: {sys.executable}")

try:
    import torch
    print(f"✅ PyTorch установлен, версия: {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch НЕ установлен: {e}")

try:
    import transformers
    print(f"✅ Transformers установлен, версия: {transformers.__version__}")
except ImportError as e:
    print(f"❌ Transformers НЕ установлен: {e}")
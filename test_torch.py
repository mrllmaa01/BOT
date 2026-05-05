import sys
print(f"Python: {sys.executable}")

try:
    import torch
    print(f"✅ PyTorch установлен!")
    print(f"   Версия: {torch.__version__}")
    print(f"   Доступен: {torch.cuda.is_available() and 'GPU' or 'CPU'}")
except Exception as e:
    print(f"❌ PyTorch НЕ установлен: {e}")

try:
    import transformers
    print(f"✅ Transformers установлен!")
except Exception as e:
    print(f"❌ Transformers НЕ установлен: {e}")
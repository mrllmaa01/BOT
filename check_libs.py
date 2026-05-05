import sys
print(f"Python: {sys.executable}")

packages = ['torch', 'transformers', 'sentencepiece']
for package in packages:
    try:
        __import__(package)
        print(f"✅ {package} установлен")
    except ImportError:
        print(f"❌ {package} НЕ установлен")
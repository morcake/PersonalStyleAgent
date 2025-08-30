import sys
import traceback
from app import main

if __name__ == "__main__":
    try:
        print("开始调试应用...")
        main()
    except Exception as e:
        print(f"发生异常: {type(e).__name__}: {e}")
        print("完整的错误堆栈:")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
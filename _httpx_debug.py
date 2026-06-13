import httpx
print("httpx version:", httpx.__version__)

# Check the _normalize_header_value source
import inspect
from httpx._models import _normalize_header_value
print(inspect.getsource(_normalize_header_value))

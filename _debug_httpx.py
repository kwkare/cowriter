import httpx._client
import inspect

src1 = inspect.getsource(httpx._client.AsyncClient._merge_headers)
with open("D:/omptemp/cowriter/_httpx_debug_output.txt", "w", encoding="utf-8") as f:
    f.write("=== _merge_headers ===\n")
    f.write(src1)
    f.write("\n=== build_request ===\n")
    src2 = inspect.getsource(httpx._client.AsyncClient.build_request)
    f.write(src2)
print("Written to file")

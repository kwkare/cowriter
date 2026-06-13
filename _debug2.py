import httpx._models
import inspect

src = inspect.getsource(httpx._models.Headers.update)
with open("D:/omptemp/cowriter/_debug2.txt", "w", encoding="utf-8") as f:
    f.write("=== Headers.update ===\n")
    f.write(src)
    f.write("\n=== Headers.__init__ ===\n")
    src2 = inspect.getsource(httpx._models.Headers.__init__)
    f.write(src2)
print("Done")

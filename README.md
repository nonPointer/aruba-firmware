# Batch download Aruba AP firmware

```bash
# install dependencies
pip install -r requirements.txt
# make download links
./main.py
# download all files
aria2c -c -j32 -s32 -i firmeware.txt
```

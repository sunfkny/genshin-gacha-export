# upload to https://coding.net/products/artifacts
import sys
import requests

if len(sys.argv) != 6:
    print("Usage: {} <token> <password> <file> <coding_file> <version>".format(sys.argv[0]))
    sys.exit(1)
token, password, file, coding_file, version = sys.argv[1:]

url = "https://sunfkny-generic.pkg.coding.net/genshin-gacha-export/releases/{}?version={}".format(coding_file, version)
req = requests.put(url, files={"file": open(file, "rb")}, auth=(token, password))
t = req.text
if "success" not in t:
    print("Upload failed: {}".format(t))
    sys.exit(1)
print(url)

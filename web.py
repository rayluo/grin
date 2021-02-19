# This script is developed based on Brython
from browser import document, bind

from grin import GreenInput, __version__


grin = GreenInput()
grin.load_json("winbxm3126.w2k.grn")

@bind("#code", "keyup")
def code_changed(ev):
    result = grin.input(document["code"].value)
    document["code"].value = result["snippet"]
    document["candidates"].text = "\n".join(
        "{} {}".format((i + 1) % 10, c)  # Although actual selectors could be !@#$...
        for i, c in enumerate(result["candidates"]))
    document["output"].value = document["output"].value + result["result"]


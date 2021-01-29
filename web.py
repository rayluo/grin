# This script is developed based on Brython
from browser import document, bind
import logging

from grin import GreenInput, __version__

logging.basicConfig(level=logging.DEBUG)

logging.info("Initializing GRIN...")
grin = GreenInput()
logging.info("Loading input method...")
grin.load_json("winbxm.w2k.grn")
logging.info("Ready to server")

@bind("#code", "keyup")
def code_changed(ev):
    result = grin.input(document["code"].value)
    document["code"].value = result["snippet"]
    document["candidates"].text = "\n".join(
        "{} {}".format((i + 1) % 10, c)  # Although actual selectors could be !@#$...
        for i, c in enumerate(result["candidates"]))
    document["output"].value = document["output"].value + result["result"]


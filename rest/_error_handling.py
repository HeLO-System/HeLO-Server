import logging
import traceback

# build error json
# add_info, reserved, will be used later ... maybe
def handle_error(text, status=400, add_info=None):
    logging.error(traceback.format_exc())
    if add_info is None:
        return {"error": text}, status
import inspect


def attach_context(message:str)->str:
    caller_frame = inspect.currentframe().f_back
    return f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno} ->{caller_frame.f_code.co_name}(): {message}"

import streamlit as st
try:
    from streamlit.script_run_context import get_script_run_ctx
except ModuleNotFoundError:
    # streamlit < 1.4
    from streamlit.report_thread import (  # type: ignore
        get_report_ctx as get_script_run_ctx,
    )
from threading import current_thread
from contextlib import contextmanager
from io import StringIO
import sys
import logging
import time


@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), get_script_run_ctx().session_id, None):
                buffer.write(b + '')
                output_func(buffer.getvalue() + '')
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    "this will show the prints"
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    "This will show the logging"
    with st_redirect(sys.stderr, dst):
        yield


def demo_function():
    """
    Just a sample function to show how it works.
    :return:
    """
    for i in range(10):
        logging.warning(f'Counting... {i}')
        time.sleep(2)
        print('Time out...')


if __name__ == '__main__':
    with st_stdout("success"), st_stderr("code"):
        demo_function()
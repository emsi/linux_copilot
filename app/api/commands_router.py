import subprocess
from enum import Enum

import pyperclip
from fastapi import APIRouter, Depends
from pydantic import HttpUrl

from app.api.api_key import get_api_key


class Applications(str, Enum):
    """Application that can be invoked with run command"""


class ScreenSaverAction(str, Enum):
    """ScreenSaver actions that can be invoked"""

    ScreenSaverLock = "lock"
    ScreenSaverUnlock = "reset"


commands_router = APIRouter()


@commands_router.get("/screen_saver")
async def screen_saver(action: ScreenSaverAction, _: str = Depends(get_api_key)):
    """Screen saver"""

    process = subprocess.Popen(
        ["xdg-screensaver", action],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"Screen saver {action} failed"}
    else:
        return {"message": f"Screen saver {action} succeeded"}


@commands_router.get("/url_open")
async def url_open(url: HttpUrl, _: str = Depends(get_api_key)):
    """Open URL in default browser"""

    process = subprocess.Popen(
        ["xdg-open", str(url)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"URL {url} open failed"}
    else:
        return {"message": f"URL {url} open succeeded"}


@commands_router.get("/clipboard")
async def clipboard_paste(text: str, _: str = Depends(get_api_key)):
    """Copy text to clipboard"""

    pyperclip.copy(text)
    process = subprocess.Popen(
        ["xclip", "-selection", "clipboard"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = process.communicate(text.encode())
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"Copy to clipboard failed"}
    else:
        return {"message": f"Copy to clipboard succeeded"}
import subprocess
from enum import Enum

import pyperclip
from fastapi import APIRouter, Depends
from pydantic import HttpUrl

from app.api.api_key import get_api_key
from app.configuration import settings


class Applications(str, Enum):
    """Application that can be invoked with run command"""

    KCalc = "kcalc"
    XEyes = "xeyes"


class ScreenSaverAction(str, Enum):
    """ScreenSaver actions that can be invoked"""

    ScreenSaverLock = "lock"
    ScreenSaverUnlock = "reset"


class FileActions(str, Enum):
    """File actions that can be invoked"""

    FileRead = "readFile"
    FileWrite = "writeFile"
    FileList = "listFiles"
    OpenFile = "openFile"


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


@commands_router.get("/run")
async def run(application: Applications, _: str = Depends(get_api_key)):
    """Run application"""

    process = subprocess.Popen(
        [application],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"Application {application} failed"}
    else:
        return {"message": f"Application {application} succeeded"}


def _sanitize_file_name(file_name: str) -> str:
    """Sanitize file name

    Remove any slashes, backslashes and double dots.
    """
    return file_name.replace("/", "").replace("\\", "").replace("..", "")


@commands_router.get("/file/list")
async def list_files(_: str = Depends(get_api_key)):
    """List files"""

    files = settings.FILES_DIR.glob("*")
    return {"files": [file.name for file in files if not file.name.startswith(".")]}


@commands_router.get("/file/read")
async def read_file(file_name: str, _: str = Depends(get_api_key)):
    """Read file"""

    file_path = settings.FILES_DIR / _sanitize_file_name(file_name)
    if not file_path.exists():
        return {"message": f"File '{file_name}' does not exist"}
    else:
        return {"content": file_path.read_text()}


@commands_router.get("/file/write")
async def write_file(file_name: str, content: str, _: str = Depends(get_api_key)):
    """Write file

    Only text files are supported.
    """

    file_path = settings.FILES_DIR / _sanitize_file_name(file_name)
    file_path.write_text(content)
    return {"message": f"File '{file_name}' written"}


@commands_router.get("/file/open")
async def open_file(file_name: str, _: str = Depends(get_api_key)):
    """Open file on your desktop using designed application

    This works by invoking xdg-open on the file.
    """

    process = subprocess.Popen(
        ["xdg-open", str(settings.FILES_DIR / _sanitize_file_name(file_name))],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"File '{file_name}' open failed"}
    else:
        return {"message": f"File '{file_name}' open succeeded"}

import asyncio
import subprocess
from enum import Enum

import pyperclip
from fastapi import APIRouter, Depends, HTTPException
from pydantic import HttpUrl

from app.api.api_key import get_api_key
from app.configuration import settings
from app.linux.util import is_process_running


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

    process = await asyncio.create_subprocess_exec(
        "xdg-screensaver",
        action,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = await process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        raise HTTPException(status_code=400, detail=f"Screen saver {action} failed")
    else:
        return {"message": f"Screen saver {action} succeeded"}


@commands_router.get("/url_open")
async def url_open(url: HttpUrl, _: str = Depends(get_api_key)):
    """Open URL in default browser"""

    process = await asyncio.create_subprocess_exec(
        "xdg-open",
        str(url),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )

    out, err = await process.communicate()
    if process.returncode != 0:
        out_message = out.decode()
        err_message = err.decode()
        print(out_message, err_message)
        raise HTTPException(status_code=400, detail=f"URL {url} open failed: {err_message}")
    else:
        return {"message": f"URL {url} open succeeded"}


@commands_router.get("/clipboard")
async def clipboard_paste(text: str, _: str = Depends(get_api_key)):
    """Copy text to clipboard"""

    pyperclip.copy(text)
    process = await asyncio.create_subprocess_exec(
        "xclip",
        "-selection",
        "clipboard",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = await process.communicate(text.encode())
    if process.returncode != 0:
        print(out.decode(), err.decode())
        raise HTTPException(status_code=400, detail=f"Copy to clipboard failed")
    else:
        return {"message": f"Copy to clipboard succeeded"}


@commands_router.get("/run")
async def run(application: Applications, _: str = Depends(get_api_key)):
    """Run application in the background and check if it's running."""
    await asyncio.create_subprocess_exec(
        application.value,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Give the application some time to start and create a window
    await asyncio.sleep(0.5)  # This is bad but leave it for now

    # Now check if the application is running
    if await is_process_running(application.value):
        return {"message": f"Application {application} started successfully"}
    else:
        # If the application is not running, assume it failed to start
        raise HTTPException(
            status_code=400, detail=f"Application {application} failed to start or is not visible"
        )


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

    process = await asyncio.create_subprocess_exec(
        "xdg-open",
        str(settings.FILES_DIR / _sanitize_file_name(file_name)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    out, err = await process.communicate()
    if process.returncode != 0:
        print(out.decode(), err.decode())
        return {"message": f"File '{file_name}' open failed"}
    else:
        return {"message": f"File '{file_name}' open succeeded"}

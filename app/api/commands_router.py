import subprocess
from enum import Enum

from fastapi import APIRouter, Depends

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

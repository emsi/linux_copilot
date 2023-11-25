import asyncio


async def is_process_running(app_name: str) -> bool:
    """ Attempt to find the application's window using xdotool

    This command needs to be adjusted according to the specifics of how the application window is identified
    """
    find_window_cmd = f"xdotool search --onlyvisible --classname {app_name}"
    process = await asyncio.create_subprocess_shell(
        find_window_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await process.communicate()
    # If `xdotool` returns anything, it means the window was found
    return bool(out.strip())

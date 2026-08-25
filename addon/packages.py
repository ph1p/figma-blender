import subprocess
import sys
import bpy
import json
import os.path
import tempfile
import threading
import site

from importlib import util
from .properties import globalDict


def check_deps_on_startup():
    """Check for dependencies and install missing in background"""
    print("Figma addon: Checking dependencies...")

    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        print(f"Figma addon: Adding user site-packages to path: {user_site}")
        sys.path.append(user_site)

    websockets_find = util.find_spec("websockets")

    if websockets_find is None:
        print("Figma addon: websockets not found, installing in background...")
        globalDict["deps_installed"] = False
        globalDict["deps_checking"] = True
        globalDict["deps_needs_restart"] = False

        thread = threading.Thread(target=install_threaded, daemon=True)
        thread.start()
    else:
        print(f"Figma addon: websockets already installed at {websockets_find.origin}")
        globalDict["deps_installed"] = True
        globalDict["deps_checking"] = False
        globalDict["deps_needs_restart"] = False


def install_threaded():
    """Run installation in background thread"""
    success = install()

    if success:
        print("Figma addon: websockets installation command succeeded")

        try:
            import importlib.util

            user_site = site.getusersitepackages()
            if user_site not in sys.path:
                print(f"Figma addon: Adding user site-packages to path: {user_site}")
                sys.path.append(user_site)

            if 'websockets' in sys.modules:
                print("Figma addon: Removing websockets from module cache")
                del sys.modules['websockets']

            to_remove = [key for key in sys.modules.keys() if key.startswith('websockets.')]
            for key in to_remove:
                del sys.modules[key]

            spec = importlib.util.find_spec("websockets")
            if spec is None:
                print("Figma addon: ERROR - websockets still not found in Python path after installation")
                print(f"Figma addon: Python path: {sys.path}")
                globalDict["deps_installed"] = False
                globalDict["deps_needs_restart"] = True
            else:
                import websockets
                print(f"Figma addon: websockets {websockets.__version__} loaded successfully - ready to use!")
                print(f"Figma addon: Loaded from: {spec.origin}")
                globalDict["deps_installed"] = True
                globalDict["deps_needs_restart"] = False

        except ImportError as e:
            print(f"Figma addon: ERROR - Installation succeeded but import failed: {e}")
            import traceback
            traceback.print_exc()
            print("Figma addon: Please restart Blender")
            globalDict["deps_installed"] = False
            globalDict["deps_needs_restart"] = True
        except Exception as e:
            print(f"Figma addon: ERROR - Unexpected error during import: {e}")
            import traceback
            traceback.print_exc()
            globalDict["deps_installed"] = False
            globalDict["deps_needs_restart"] = True
    else:
        print("Figma addon: Failed to install websockets - check console for errors")
        globalDict["deps_installed"] = False
        globalDict["deps_needs_restart"] = False

    globalDict["deps_checking"] = False

    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except:
        pass


def find_writable_site_packages(py_exec):
    """Return the first writable site-packages dir of Blender's Python, or None.

    site.getsitepackages() is neither single-entry nor ordered the same way on
    every platform - on Windows the first entry is the interpreter root, not
    site-packages - so every candidate is checked instead of taking [0].

    Writability is probed by actually creating a file: os.access() only looks at
    the read-only attribute on Windows and happily reports directories under
    "Program Files" as writable when they are not.
    """
    probe = subprocess.run(
        [py_exec, "-c", "import json, site; print(json.dumps(site.getsitepackages()))"],
        capture_output=True,
        text=True,
        timeout=10
    )

    if probe.returncode != 0:
        print("Figma addon: Could not determine site-packages")
        return None

    try:
        candidates = json.loads(probe.stdout)
    except ValueError:
        print(f"Figma addon: Could not parse site-packages list: {probe.stdout!r}")
        return None

    for candidate in candidates:
        if os.path.basename(candidate) != "site-packages":
            continue

        try:
            with tempfile.NamedTemporaryFile(dir=candidate):
                pass
        except OSError as e:
            print(f"Figma addon: {candidate} is not writable ({e.__class__.__name__})")
            continue

        return candidate

    return None


def install():
    """Install websockets package. Returns True on success."""
    py_exec = str(sys.executable)
    print(f"Figma addon: Using Python: {py_exec}")

    try:
        result = subprocess.run(
            [py_exec, "-m", "ensurepip"],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(f"Figma addon: ensurepip result: {result.returncode}")

        result = subprocess.run(
            [py_exec, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(f"Figma addon: pip upgrade result: {result.returncode}")

        target_dir = find_writable_site_packages(py_exec)

        if target_dir:
            print(f"Figma addon: Target installation directory: {target_dir}")
            pip_args = ["--target", target_dir, "--upgrade", "websockets"]
        else:
            # Blender's site-packages lives inside the installation directory,
            # which is read-only for a normal system-wide install - the default
            # on Windows and for most Linux packages. The per-user site
            # directory needs no elevation, and check_deps_on_startup() already
            # puts it on sys.path.
            print("Figma addon: site-packages is not writable, installing into the user site")
            pip_args = ["--user", "--upgrade", "websockets"]

        result = subprocess.run(
            [py_exec, "-m", "pip", "install"] + pip_args,
            capture_output=True,
            text=True,
            timeout=120
        )

        print(f"Figma addon: websockets install result: {result.returncode}")

        if result.returncode == 0:
            print("Figma addon: websockets installation output:")
            print(result.stdout)
            return True
        else:
            print("Figma addon: websockets installation failed:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("Figma addon: Installation timed out")
        return False
    except Exception as e:
        print(f"Figma addon: Installation error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

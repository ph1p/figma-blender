import subprocess
import sys
import bpy
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

        site_packages_result = subprocess.run(
            [py_exec, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if site_packages_result.returncode == 0:
            target_dir = site_packages_result.stdout.strip()
            print(f"Figma addon: Target installation directory: {target_dir}")

            result = subprocess.run(
                [py_exec, "-m", "pip", "install", "--target", target_dir, "--upgrade", "websockets"],
                capture_output=True,
                text=True,
                timeout=120
            )
        else:
            print("Figma addon: Could not determine site-packages, installing without --target")
            result = subprocess.run(
                [py_exec, "-m", "pip", "install", "websockets"],
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

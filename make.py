import os
import shutil
import pathlib
import platform
import argparse

if platform.system() != "Windows":
    raise OSError("This script is only for Windows")

if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.abspath(__file__))
    if pathlib.Path(ROOT).resolve() != pathlib.Path(os.path.abspath(".")).resolve():
        raise RuntimeError("Please run this script in the repository's root directory")

    parser = argparse.ArgumentParser("thtool(TouHouTool) build script")
    parser.add_argument("--debug", action="store_true", help="Build in debug mode")
    args = parser.parse_args()

    for root, dirs, _ in os.walk(ROOT):
        for dir in dirs:
            if dir == "build" or dir == "dist" or dir.endswith(".egg-info"):
                shutil.rmtree(os.path.join(root, dir))
        break

    for root, _, files in os.walk(os.path.join(ROOT, "thtool")):
        for file in files:
            if file.endswith(".pyd"):
                os.remove(os.path.join(root, file))
        break

    if not os.path.exists(os.path.join(ROOT, "cpp/pybind11")) and \
        not os.path.isdir(os.path.join(ROOT, "cpp/pybind11")):
        os.system("git clone https://github.com/pybind/pybind11.git cpp/pybind11 --depth=1")

    os.system("python -m pip install -U pip")
    os.system(f"python -m pip install -r requirements.txt")

    os.system(f"python -m build --wheel --sdist")

    for root, dirs, files in os.walk(os.path.join(ROOT, "build")):
        for dir in dirs:
            if dir.startswith("lib."):
                for root2, _, files2 in os.walk(os.path.join(root, dir, "thtool")):
                    for file in files2:
                        if file.endswith(".pyd"):
                            shutil.copy(os.path.join(root2, file), os.path.join(ROOT, "thtool"))
                            print(f"Coping {file} -> thtool")
                    break
        break
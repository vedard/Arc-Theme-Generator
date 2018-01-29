#! /bin/python3

import re
import pathlib
import subprocess
import argparse
import multiprocessing.pool


class ArcThemeVariant:
    def get(name):
        if name.lower() == "default":
            return ArcThemeVariant.DEFAULT
        elif name.lower() == "black":
            return ArcThemeVariant.BLACK
        elif name.lower() == "grey":
            return ArcThemeVariant.GREY

    DEFAULT = {
    }

    BLACK = {
        "#252a35": "#121212",  # Gnome Panel Background
        "#2f343f": "#1d1d1d",  # Dark Header BG
        "#e7e8eb": "#e8e8e8",  # Light Header BG
        "#383c4a": "#252525",  # Dark Background
        "#d3dae3": "#c0c0c0",  # Dark Foreground
        "#f5f6f7": "#f5f5f5",  # Light Background
        "#3b3e45": "#3b3b3b",  # Light Foreground
        "#404552": "#2f2f2f",  # Dark Base Background (ListBox)
        "#353945": "#222222",  # Dark SideBar Background (Nautilus)
        "#bac3cf": "#c4c4c4",  # Dark SideBar Foreground (Nautilus)
        "#323644": "#202020",  # Dark Gnome Shell Modal background
        "#5c616c": "#616161",  # Light Gnome Shell Foreground
        "#5b627b": "#505050",  # Dark Switch Background
        "#353a47": "#232323",  # Dark Switch Circle
        "#cfd6e6": "#dbdbdb",  # Light Switch Background
    }

    GREY = {
        "#252a35": "#2d2d2d",  # Gnome Panel Background
        "#2f343f": "#383838",  # Dark Header BG
        "#e7e8eb": "#e8e8e8",  # Light Header BG
        "#383c4a": "#404040",  # Dark Background
        "#d3dae3": "#dbdbdb",  # Dark Foreground
        "#f5f6f7": "#f5f5f5",  # Light Background
        "#3b3e45": "#636363",  # Light Foreground
        "#404552": "#4a4a4a",  # Dark Base Background (ListBox)
        "#353945": "#3d3d3d",  # Dark SideBar Background (Nautilus)
        "#bac3cf": "#c4c4c4",  # Dark SideBar Foreground (Nautilus)
        "#323644": "#3b3b3b",  # Dark Gnome Shell Modal background
        "#5c616c": "#636363",  # Light Gnome Shell Foreground
        "#5b627b": "#6b6b6b",  # Dark Switch Background
        "#353a47": "#3E3E3E",  # Dark Switch Circle
        "#cfd6e6": "#dbdbdb",  # Light Switch Background
    }


class ArcThemeGenerator:
    def __init__(self, cwd):
        self.cwd = pathlib.Path(cwd)

    def replace_color(self, color, subtheme):
        print("Replacing colors...")
        replacement = ArcThemeVariant.get(subtheme)
        replacement["#5294e2"] = color
        regex = re.compile('|'.join(map(re.escape, replacement)),
                           re.RegexFlag.IGNORECASE)
        for path in self.cwd.rglob("**/*"):
            if re.match('(.*\.scss|.*\.svg|.*\.rc|.*\.xml|.*gtkrc.*)', str(path)):
                with(open(path, 'r+')) as file:
                    content = file.read()
                    content = regex.sub(
                        lambda m: replacement[m.group(0).lower()],
                        content)
                    file.seek(0)
                    file.write(content)

    def remove_bold_font(self):
        print("Removing bold font...")
        for path in self.cwd.rglob("**/*"):
            if re.match('(.*\.scss)', str(path)):
                with(open(path, 'r+')) as file:
                    content = file.read()
                    content = re.sub("font-weight: bold",
                                     "font-weight: normal",
                                     content)
                    file.seek(0)
                    file.write(content)

    def render_assets(self, threads):
        print("Rendering assets...")
        pool = multiprocessing.pool.ThreadPool(threads)
        for path in self.cwd.rglob("./**/render-assets.sh"):
            if not path.parent.is_symlink():
                assets_folder = [path.parent / "assets",
                                 path.parent / "assets-dark"]

                for folder in assets_folder:
                    if folder.exists():
                        [x.unlink() for x in (folder).glob("*")]

                pool.apply_async(self.__render_assets, args=(path, ))
        pool.close()
        pool.join()

    def __render_assets(self, path):
        print("  Rendering: " + path.parent.name)
        subprocess.check_output(str(path), cwd=path.parent)
        print("  Finished: " + path.parent.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a custom Arc-Theme')
    parser.add_argument('directory', action='store',
                        help='Path to Arc Theme Git repository')
    parser.add_argument('--color', '-c', action='store', default="#5294e2",
                        help='Main color')
    parser.add_argument('--variant', action='store', default="default",
                        choices=["default", "black", "grey"],
                        help='Preconfigured background and header colors')
    parser.add_argument('--without-bold', action='store_true',
                        help='Replace all bold font with normal font')
    parser.add_argument('--no-assets', action='store_true',
                        help='Do not render assets (Faster)')
    parser.add_argument('--threads', '-t', action='store', default=2, type=int,
                        help='Number of threads to render assets')
    parser.add_argument('--version', '-v', action='version',
                        version='Arc-Theme-Generator 0.0')
    args = parser.parse_args()

    at = ArcThemeGenerator(args.directory)
    at.replace_color(args.color, args.variant)

    if args.without_bold:
        at.remove_bold_font()

    if not args.no_assets:
        at.render_assets(args.threads)

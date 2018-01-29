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
        "#262932": "#101010",  # Dark WM bordard
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
        "#2d323d": "#171717",  # Dark Checkbox Background
        "#5b627b": "#505050",  # Dark Switch Background
        "#353a47": "#232323",  # Dark Switch Circle
        "#cfd6e6": "#dbdbdb",  # Light Switch Background
        "#444a58": "#2F2F2F",  # Gtk2 Dark Button Background
        "#505666": "#3B3B3B",  # Gtk2 Dark Button-Hover Background
        "#3e4351": "#282828",  # Gtk2 Dark Button-insensitive Background
        "#2e3340": "#181818",  # Gtk2 Dark Button-active Background
        "#4b5162": "#3C3C3C",  # Gtk2 Dark Tooltips Background
        "#3e4350": "#2C2C2C",  # Gtk2 Dark Insensitive Background
        "#262934": "#0E0E0E",  # Gtk2 Dark checkbox-unchecked border
        "#2b303b": "#151515",  # Gtk2 Dark checkbox-unchecked Background
        "#3e434f": "#282828",  # Gtk2 Dark scrollbar Background
        "#2d303b": "#151515",  # Gtk2 Dark trough Background
        "#767b87": "#606060",  # Gtk2 Dark slider Background
        "#303440": "#191919",  # Gtk2 Dark border insensitive
        "#2b2e39": "#131313",  # Gtk2 Dark border
        "#313541": "#1a1a1a",  # Gtk2 Dark inline toolbar
    }

    GREY = {
        "#252a35": "#2d2d2d",  # Gnome Panel Background
        "#262932": "#2b2b2b",  # Dark WM bordard
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
        "#2d323d": "#323232",  # Dark Checkbox Background
        "#353a47": "#3E3E3E",  # Dark Switch Circle
        "#cfd6e6": "#dbdbdb",  # Light Switch Background
        "#444a58": "#4a4a4a",  # Gtk2 Dark Button  Background
        "#505666": "#565656",  # Gtk2 Dark Button-Hover Background
        "#3e4351": "#434343",  # Gtk2 Dark Button-insensitive Background
        "#2e3340": "#333333",  # Gtk2 Dark Button-active Background
        "#4b5162": "#575757",  # Gtk2 Dark Tooltips Background
        "#3e4350": "#474747",  # Gtk2 Dark Insensitive Background
        "#262934": "#292929",  # Gtk2 Dark checkbox-unchecked border
        "#2b303b": "#303030",  # Gtk2 Dark checkbox-unchecked Background
        "#3e434f": "#434343",  # Gtk2 Dark scrollbar Background
        "#2d303b": "#303030",  # Gtk2 Dark trough Background
        "#767b87": "#7b7b7b",  # Gtk2 Dark slider Background
        "#303440": "#343434",  # Gtk2 Dark border insensitive
        "#2b2e39": "#2e2e2e",  # Gtk2 Dark border
        "#313541": "#353535",  # Gtk2 Dark inline toolbar
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

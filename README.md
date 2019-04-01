# Arc Theme Generator
This script let you replace colors in the arc-theme by updating every `.scss`, `.svg`, `.xml`, `.rc` and `gtkrc` files

## Usage
1. Clone the arc-theme repository
2. Run arc-theme-generator
3. Then you can follow the installation procedure in the arc-theme README.

```sh
# Only change the main color to red
python arc-theme-generator.py -c "#cc575d" /path/to/arc-theme-repo

# Change the main color to green (Screenshots below)
# Change all background/header to black
# Remove all bold font 
python arc-theme-generator.py -c "#3D8E91" --variant "black" --without-bold /path/to/arc-theme-repo
```

If you want to generate a new theme you need to reset all modification in the arc-theme repository with a `git reset --hard`.

## Screenshot
### Arc
![](screenshot/light.png)
### Arc-Darker
![](screenshot/darker.png)
### Arc-Dark
![](screenshot/dark.png)

## Optional arguments
|Option|Description|
|-|-|
|`--color`| Change the main color|
|`--variant` | Change the color of the header and the background. There is currently 2 variant (black and grey) |
|`--without-bold`| Remove the `font-weight: bold` in the css

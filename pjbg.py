#!/usr/bin/env python3

## Paul E. Johnson <pauljohn@ku.edu>
## 20150102

## A script to randomly reassign compiz background images for viewports.
## Recall compiz after 0.9.2 uses "viewports" to simulate workspaces.

## Will choose an image file randomly from within dir hierarchy. 

## Can replace one viewport's wallpaper.  The w argument will be
## interpreted in one of 3 ways 
## 
## 1. If w < 1, (either 0 or a negative number), this means remove all
## existing wallpapers and replace with one randomly chosen image.
##
## 2. If 1 <= w <= N (where there are N wallpaper images already
## defined), then the image on viewport w will be replaced. All of the
## other images will remain the same.
##
## 3. If N < w, we interpret this as a request to expand the
## wallpaper array by one.


## I thought it was a little interesting to make types 1 and 3
## work together with compiz. To change the number of wallpapers,
## it is required to correctly change these variables in the
## wallpaper plugin as well:
## "bg-fill-type"
## "bg-image-pos"
## "bg-color1", 
## "bg-color2", s

## I had previously been doing this by dbus-send, but compiz's
## interaction with dbus has become less and less stable, so this version
## uses "gsettings".

## About the schema argument:
## Because I do not use Unity as my desktop environment, I have to point
## SCHEMA at the location where compiz stores wallpapers. If you get
## compiz working with XFCE4, for example, make sure you use the Gsettings
## backend and DO allow Compiz to interact with the desktop environment in
## advanced settings. 

## If you are using Unity, you probably need to change the path, removing
## "Default" with "unity".  You can do from command line or by editing script.

## If you want to know how to get Compiz going without the Unity Desktop, 
## this is not a bad set of advice 
## http://www.webupd8.org/2012/11/how-to-set-up-compiz-in-xubuntu-1210-or.html
## If you have Unity installed, it is necessary to remove it, or else
## launching compiz with the Gsettings back end gets Ubuntu all confused and
## Unity keeps starting at same time. If you have trouble with that, I can help


import argparse
import subprocess
import sys
import os
import random

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir",  help = "directory path", 
                    default = "/usr/local/share/Backgrounds")
parser.add_argument("-w", "--workspace", 
                    help = "workspace number, 0, 1-n, or > n", default = "-1", 
                    type = int)
parser.add_argument("-schema", help = "gsettings shema", 
                    metavar = "SCHEMA", default = "org.compiz.wallpaper:/org/compiz/profiles/Default/plugins/wallpaper/")
parser.add_argument("-key", help = "gsettings key", metavar = "KEY", default = "bg-image")
args = parser.parse_args()

array = eval(subprocess.check_output(["gsettings", "get", args.schema, args.key]))

## print(array)
arraylen = len(array)

filename = random.choice([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(args.dir)) for f in fn])
print("The newly found filename is:")
print(filename)

## print("Array length was")
## print(arraylen)

## python arrays index 0, ... , N-1, so downshift workspace number
ws = args.workspace - 1

## If ws 0 or smaller, we are going to reset whole collection back to
## just one image. if ws > N of images, then add a new image.
if ws < 0:
    array=[str(filename)]
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
    subprocess.call(["gsettings", "set", args.schema, "bg-fill-type", str("[0]")])
    subprocess.call(["gsettings", "set", args.schema, "bg-image-pos", str("[0]")])
    subprocess.call(["gsettings", "set", args.schema, "bg-color1", str("['#000000ff']")])
    subprocess.call(["gsettings", "set", args.schema, "bg-color2", str("['#000000ff']")])
elif ws < arraylen:
    array[ws]=str(filename)
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
else:
    array.append(str(filename))
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
    arraylen = len(array)
    subprocess.call(["gsettings", "set", args.schema, "bg-fill-type", str([0]*arraylen)])
    subprocess.call(["gsettings", "set", args.schema, "bg-image-pos", str([0]*arraylen)])
    subprocess.call(["gsettings", "set", args.schema, "bg-color1", str(['#000000ff']*arraylen)])
    subprocess.call(["gsettings", "set", args.schema, "bg-color2", str(['#000000ff']*arraylen)])



subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])

print("HELLO, corrected image array is:")               
print('\n '.join(array))

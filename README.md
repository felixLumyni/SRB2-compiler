# SRB2-Compiler
A python program to automate the proccess of making [SRB2](https://www.srb2.org/) mods fit for git.

[Download with DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/felixLumyni/SRB2-compiler/blob/main/_SRB2Compiler.py)

[Download compatibility version with DownGit](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/felixLumyni/SRB2-compiler/blob/main/_SRB2CompilerUgly.py)

## Why is this helpful?
- While compressed files - such as ZIP/WAD/PK3 - can be uploaded with git, you can't keep track of development (like which files were added, removed or modified in each commit/version)
- Having your mod outside of a compressed file also allows mods to be edited more easily with apps other than [SLADE](https://github.com/sirjuddington/SLADE)
- The **compiler** tool can automate the process of saving your mod to a PK3 every time you want to test the mod
- The **decompiler** tool can automate the process of exporting your PK3 mod to a folder so it can be versioned with git
- Your settings are saved automatically based on the file name. You can also expand the window vertically in the **Compiler** menu to save and load custom presets

## How to use this to build and test your mod
- Open the .py file with [Python](https://www.python.org/)
- Compiler settings page: Specify which folder will be converted into a pk3
- (OPTIONAL) Compiler settings page: Specify the preferred filename for the pk3
- (OPTIONAL) Compiler settings page: Specify where the pk3 will be moved to afterwards (By default, it goes to wherever the compiler is)
- (OPTIONAL) Compiler settings page: Specify a .bat to automatically launch SRB2 with your mod after compiling (Example: ``srb2win.exe -debug -opengl -warp 1 -file MyCoolMod.pk3 +weather 1``)
- Compiler page: Compile and/or test the mod

## How to use this to export your PK3 mod
- Open the .py file with [Python](https://www.python.org/)
- Decompiler settings page: Specify where your [7-Zip](https://www.7-zip.org/) is installed
- Decompiler settings page: Specify which PK3 will be cloned to a folder
- Decompiler page: Decompile your mod, and sort files to remove duplicate files so it can be ran in SRB2 after compiling (WORK IN PROGRESS)

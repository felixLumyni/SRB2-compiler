'''
# SRB2Compiler (Compatibility Mode) v1.1002 by Lumyni
# Requires https://www.python.org/ and https://www.7-zip.org/
# Messes w/ files, only edit this if you know what you're doing!
'''

import os, shutil, importlib, sys, subprocess, tkinter, platform
from tkinter import messagebox, filedialog
from os.path import splitext
from collections import Counter
from importlib import util, machinery
from tkinter import ttk
from tkinter import *

def import_path(path):
    module_name = os.path.basename(path).replace('-', '_')
    spec = util.spec_from_loader(module_name, machinery.SourceFileLoader(module_name, path))
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module

def clean(sevenzip, result, destination):
    toclean = {
        "previous zip ("+result+".zip)" : os.path.join(sevenzip, result+".zip"),
        "previous pk3 ("+result+".pk3)" : os.path.join(sevenzip, result+".pk3"),
        "previous pk3 ("+result+".pk3) from destination" : os.path.join(destination, result+".pk3")
    }
    for step in toclean:
        path = toclean[step]
        if os.path.exists(path):
            os.unlink(path) ; print(f"Removed {step}.")
        else:
            pass #print(f"Couldn't find {step}, all clear.")

def ziptopk3(location, result, destination, usesevenziptocompile, sevenzip):
    os.chdir(sevenzip)
    print("----- 7ZIP -----")
    os.system('7z a '+result+'.zip '+location+"\\* -x!.git")
    print("----- END OF 7ZIP -----")
    print("Location compiled to .zip")

    os.rename(os.path.join(os.getcwd(), result+'.zip'), result+'.pk3')
    print("Changed from .zip to .pk3")

    shutil.move(os.path.join(os.getcwd(), result+".pk3"), destination)
    print(f"Moved the result pk3 to {destination}")

def unzip(sevenzip, pk3toextract, autosort=0):
    sevenzip = validate_path(sevenzip, "sevenzip's path")
    if not sevenzip: return
    pk3toextract = validate_path(pk3toextract, "pk3 to extract's path")
    if not pk3toextract: return

    os.chdir(sevenzip)
    #this is the mess ever
    ext = os.path.splitext(pk3toextract)
    if ext[1].lower() == ".pk3":
        os.rename(pk3toextract,ext[0]+".pk3")
        pk3toextract = pk3toextract.replace(pk3toextract,ext[0]+".pk3")
    basename = os.path.basename(pk3toextract).replace('.pk3','')
    basename = basename.replace('"','')
    newfolder = os.path.join(sevenzip,basename)
    if pk3toextract == "" or basename == "": #paranoia
        messagebox.showerror("Got empty basename, do you have your 'PK3 to extract' field set up correctly? BE CAREFUL, something *terrible* could have happened.")
        return
    try: shutil.rmtree(newfolder); print("Deleted old temp folder in 7zip")
    except: pass
    os.mkdir(newfolder)
    print("Created folder where files will be extracted to")

    print("----- 7ZIP -----")
    os.system('7z x -o"'+newfolder+'" "'+pk3toextract+'" -aou') #Rename duplicate files from the archive
    print("----- END OF 7ZIP -----")
    print("Extracted files from pk3")

    moveto = pk3toextract.replace('.pk3','')
    moveto = moveto.replace('"','')
    try: shutil.rmtree(moveto); print("Deleted old export/folder")
    except: pass
    basedir = pk3toextract.replace(''+basename+'.pk3','')
    basedir = basedir.replace('"','')
    shutil.move(newfolder, basedir)
    print("Moved the folder to the same location as the pk3")
    if autosort: sortbynumber(pk3toextract)

def sortbynumber(pk3toextract): #TODO: SOMEHOW MOVE S_SKIN TO THE ABSOLUTE TOP
    search_dir = pk3toextract.replace('.pk3','')
    search_dir = search_dir.replace('"','')
    print(f"Organizing lumps in {search_dir}...")
    count = 0
    index = 2
    folder1 = None

    for subdir, dirs, files in os.walk(search_dir):
        for file in files:
            ext = os.path.splitext(str(file))[1]
            basename = os.path.basename(file).replace(ext,'')
            filepath = os.path.join(str(subdir),str(file))
            filepath = check_conflicts(filepath, basename, subdir, ext)
            if subdir and basename[len(basename)-index] == "_": #THIS MEANS IT ONLY GOES UP TO "_9"
                print('* Found duplicate file: ' + filepath)

                #paranoia
                try:
                    os.rename(filepath, filepath.replace(ext,''))
                    filepath = os.path.join(str(subdir),basename)
                except:
                    newdir = os.path.join(subdir, 0)
                    try: os.mkdir(newdir)
                    except: pass
                    shutil.move(filepath, newdir)
                    newpath = os.path.join(filepath, newdir)
                    os.rename(newpath, newpath.replace(ext,''))
                    filepath = os.path.join(newpath,newpath.replace(ext,''))

                num = basename.split('_')[1-index]
                newdir = os.path.join(subdir, num)
                if num=='1' and not folder1: folder1 = newdir

                try: os.mkdir(newdir)
                except: pass
                shutil.move(filepath, newdir)

                newfile = os.path.join(filepath, os.path.join(newdir,basename))
                os.rename(newfile, newfile[0 : -index : ]+ext)

                count += 1
    print(f"Modified a total of {count} files (Excluding conflicts)")
    print("NOTE: All duplicate files were moved and renamed to a subdirectory based on the last digit from their filename (for example, 'hi_1' would move to '1/hi').")
    if folder1:
        os.rename(folder1,folder1[0 : -1 : ]+'Super')
        print("NOTE: Renamed folder '1' to 'Super'")
        try:
            os.rename(folder1[0 : -1 : ]+'0',folder1[0 : -1 : ]+'CONFLICTS')
            messagebox.showwarning(title="Warning", message="There were files with extension conflicts!!! \nThere should be a 'CONFLICTS' folder in their place, wherever they were.")
        except: pass

def check_conflicts(filepath, basename, subdir, ext):
    myDir = os.listdir(subdir)
    l = [splitext(filename)[0] for filename in myDir]
    a = dict(Counter(l))

    for k,v in a.items():
        if v > 1 and k == basename:
            print(f"+ FOUND EXTENSION CONFLICT: {k}")
            try:
                os.rename(filepath, filepath.replace(ext,''))
                filepath = os.path.join(str(subdir),str(basename))
            except:
                newdir = os.path.join(subdir, '0')
                try: os.mkdir(newdir)
                except: pass
                shutil.move(filepath, newdir)
                newpath = os.path.join(filepath, newdir)
                os.rename(newpath, newpath.replace(ext,''))
                filepath = os.path.join(newpath,newpath.replace(ext,''))
    return filepath

def test(testbat):
    print("The compiled file should be ready for tests! Trying to run the test file...")
    testbat = validate_path(testbat, "the test bat's path")
    if not testbat: return

    try:
        os.chdir(os.path.dirname(os.path.realpath(testbat)))
        subprocess.call([os.path.join(os.getcwd(), testbat)])
    except Exception as e:
        print(f'ERROR: Failed to run the test file. Reason: {e}')
        messagebox.showerror(title='Error', message="Couldn't execute the test file.\nCheck the console for details.")

class UI:
    def __init__(self, root, warn):
        def layoutMode(lol, lmao, rofl, mode=None):
            if mode: self.box1.set(mode)
            goToHell()

            OFFSET = 10
            SPACING = 29
            L = 5
            R = 155
            self.box1.place(x=R, y=SPACING)

            if self.box1.get() == self.box1.cget('values')[1]: #compiler settings
                self.t1.configure(state=tkinter.NORMAL)
                self.t2.configure(state=tkinter.NORMAL)
                self.t3.configure(state=tkinter.NORMAL)
                self.t4.configure(state=tkinter.NORMAL)
                self.t6.configure(state=tkinter.NORMAL)
                self.t7.configure(state=tkinter.NORMAL)
                self.inf1.place(x=SPACING, y=00)
                self.inf2.place(x=R/1.5, y=(OFFSET/2)+SPACING*4)
                self.b1.place(x=L, y=SPACING)
                self.lbl2.place(x=L, y=(OFFSET/2)+SPACING*3)
                self.lbl3.place(x=L, y=(OFFSET/2)+SPACING*2)
                self.lbl1.place(x=L, y=(OFFSET/2)+SPACING*5)
                self.lbl7.place(x=L, y=(OFFSET/2)+SPACING*6)
                self.lbl4.place(x=L, y=(OFFSET/2)+SPACING*7)
                self.t2.place(x=R, y=(OFFSET/2)+SPACING*3)
                self.t3.place(x=R, y=(OFFSET/2)+SPACING*2)
                self.t1.place(x=R, y=(OFFSET/2)+SPACING*5)
                self.t7.place(x=R, y=(OFFSET/2)+SPACING*6)
                self.t4.place(x=R, y=(OFFSET/2)+SPACING*7)
                self.cfg1.place(x=L, y=OFFSET+SPACING*8)
                self.cfg3.place(x=L, y=OFFSET+SPACING*9)
                '''offscreen'''
                self.cfg2.place(x=L, y=OFFSET+SPACING*10.5)
                self.cfg2b.place(x=L, y=OFFSET+SPACING*11.5)
                self.lbl6.place(x=L, y=OFFSET+SPACING*12.5)
                self.t6.place(x=R, y=OFFSET+SPACING*12.5)
            elif self.box1.get() == self.box1.cget('values')[2]: #decompiler
                self.b3.place(x=L, y=SPACING)
                self.inf3.place(x=SPACING, y=00)
                if not self.cfg4var.get(): self.b4.place(x=L, y=SPACING*2)
            elif self.box1.get() == self.box1.cget('values')[3]: #decompiler settings
                self.inf1.place(x=SPACING, y=00)
                self.t2.configure(state=tkinter.NORMAL)
                self.t5.configure(state=tkinter.NORMAL)
                self.inf1.place(x=SPACING)
                self.b1.place(x=L, y=SPACING)
                self.lbl2.place(x=L, y=(OFFSET/2)+SPACING*2)
                self.lbl5.place(x=L, y=(OFFSET/2)+SPACING*3)
                self.t2.place(x=R, y=(OFFSET/2)+SPACING*2)
                self.t5.place(x=R, y=(OFFSET/2)+SPACING*3)
                self.cfg4.place(x=L, y=OFFSET+SPACING*4)
            elif self.box1.get() == self.box1.cget('values')[0]: #compiler
                self.b2.place(x=L, y=SPACING)
                bt = 2
                if self.cfg2bvar.get(): self.b5.place(x=L, y=SPACING*bt); bt += 1
                if not self.cfg3var.get(): self.b6.place(x=L, y=SPACING*bt)
                '''offscreen'''
                self.preset.place(x=L, y=SPACING*10.1)
                self.b7.place(x=L,y=SPACING*11)
                self.b8.place(x=R,y=SPACING*11)
            else:
                messagebox.showerror(title="Error", message="wtf")
        
        def goToHell(): #i hate this
            #teleport labels, entries, buttons and checkbuttons to hell
            #i wish i could just make them invisible, oh well
            for i in enumerate(self.frame_1.winfo_children()):
                for type in ['label', 'entry', 'button', 'checkbutton']:
                    if type in str(i[1]):
                        self.frame_1.winfo_children()[i[0]].place(y=-666)
                        if 'entry' in str(i[1]): #also disable entries, because TAB...
                            self.frame_1.winfo_children()[i[0]].configure(state=tkinter.DISABLED)

        def resetEntries():
            try: self.t1.insert(0,settings.result)
            except: pass
            try: self.t2.insert(0,settings.sevenzip)
            except: pass
            try: self.t3.insert(0,settings.location)
            except: pass
            try: self.t4.insert(0,settings.testbat)
            except: pass
            try: self.t5.insert(0,settings.pk3toextract)
            except: pass
            try: self.t6.insert(0,settings.logs)
            except: pass
            try: self.t7.insert(0,settings.destination)
            except: pass
            try: self.cfg1.select() if settings.autosave else self.cfg1.deselect()
            except: self.cfg1.select()
            try: self.cfg2.select() if settings.autormlog else self.cfg2.deselect()
            except: pass
            try: self.cfg2b.select() if settings.autoclear else self.cfg2b.deselect()
            except: pass
            try: self.cfg3.select() if settings.autotest else self.cfg3.deselect()
            except: self.cfg3.select()
            try: self.cfg4.select() if settings.autosort else self.cfg4.deselect()
            except: self.cfg4.select()

        def getEVERYTHING(): #IMPORTANT: this gets the values based in the order of creation of the entries; mind the run() function
            values = []
            trace = [] #so we don't get values from the same checkbutton twice. because they are stoopid
            for i in enumerate(self.frame_1.winfo_children()):
                for type in ['entry', 'checkbutton']:
                    if 'checkbutton' in str(i[1]):
                        bruh = False
                        for repeat in trace:
                            if repeat == str(i[1]): bruh = True
                        if bruh: continue
                        trace.append(str(i[1]))
                        varname = str(self.frame_1.winfo_children()[i[0]].cget("variable"))
                        values.append(int(self.frame_1.winfo_children()[i[0]].getvar(varname)))
                        continue
                    if type in str(i[1]):
                        values.append(self.frame_1.winfo_children()[i[0]].get())
            return values

        def savepreset():
            path = filedialog.asksaveasfilename(defaultextension=".lumy")
            if not path == '':
                run(path, *list(getEVERYTHING()))
                global preset
                preset = path
                self.preset.configure(text = f'Current preset: {os.path.basename(preset)}')

        def loadpreset():
            path = filedialog.askopenfilename()
            if not path == '':
                print("Attempting to change settings file...\n")
                root.destroy()
                for after_id in root.tk.eval('after info').split():
                    root.after_cancel(after_id)
                main(path)

        def smartPath(entry, dir=False):
            if dir:
                try: path = filedialog.askdirectory(initialdir=entry.get())
                except: path = filedialog.askdirectory()
            else:
                path = filedialog.askopenfilename()
                
            if not path == '':
                entry.delete(0,tkinter.END)
                entry.insert(0,path)

        def smartDirPath(entry): smartPath(entry, True)

        self.frame_1=tkinter.Frame(master=root)
        self.frame_1.pack(pady=10, padx=10, expand=True, fill="both")
        self.box1var = StringVar()
        self.box1var.trace('w',layoutMode)
        self.box1=ttk.Combobox(self.frame_1, textvar=self.box1var, values=["Compiler", "Compiler settings", "Decompiler", "Decompiler settings"])
        self.inf1=tkinter.Label(self.frame_1, text='Make sure the paths do not require admin!', fg='#555')
        self.inf2=tkinter.Label(self.frame_1, text='\u2193 OPTIONAL \u2193',  fg='#555')
        self.lbl1=tkinter.Label(self.frame_1, text='Mod name (without .pk3)')
        self.lbl2=tkinter.Button(self.frame_1, text='Path to 7Zip', command= lambda: smartDirPath(self.t2))
        self.lbl3=tkinter.Button(self.frame_1, text='Path to compile (Mod)', command= lambda: smartDirPath(self.t3))
        self.lbl4=tkinter.Button(self.frame_1, text='Path to test file (.bat)', command= lambda: smartPath(self.t4))
        self.lbl5=tkinter.Button(self.frame_1, text='Path to PK3 to extract', command= lambda: smartPath(self.t5))
        self.lbl6=tkinter.Button(self.frame_1, text='Path to logs', command= lambda: smartDirPath(self.t6))
        self.lbl7=tkinter.Button(self.frame_1, text='Path: Mod destination', command= lambda: smartDirPath(self.t7))
        self.t3=tkinter.Entry(self.frame_1) #location
        self.t2=tkinter.Entry(self.frame_1) #sevenzip
        self.t1=tkinter.Entry(self.frame_1) #result
        self.t7=tkinter.Entry(self.frame_1) #destination
        self.t4=tkinter.Entry(self.frame_1) #testbat
        self.t5=tkinter.Entry(self.frame_1) #pk3toextract
        self.t6=tkinter.Entry(self.frame_1) #logs
        self.b1=tkinter.Button(self.frame_1, text='Save settings', command= lambda: run(True, *list(getEVERYTHING())))
        self.b2=tkinter.Button(self.frame_1, text='Compile', command= lambda: run(False, *list(getEVERYTHING())))
        self.b3=tkinter.Button(self.frame_1, text='Decompile', command= lambda: unzip(self.t2.get(),self.t5.get(),self.cfg4.get()))
        self.b4=tkinter.Button(self.frame_1, text='Sort files', command= lambda: sortbynumber(self.t5.get()))
        self.b5=tkinter.Button(self.frame_1, text='Clean ALL logs', command= lambda: clean_logs(self.t6.get(), "ALL"))
        self.b6=tkinter.Button(self.frame_1, text='Test', command= lambda: test(self.t4.get()))
        self.inf3=tkinter.Label(self.frame_1, text='NOTE: This does not fully work with SKINS yet', fg='#FF0000')
        self.cfg1var=BooleanVar()
        self.cfg2var=BooleanVar()
        self.cfg2bvar=BooleanVar()
        self.cfg3var=BooleanVar()
        self.cfg4var=BooleanVar()
        self.cfg5var=BooleanVar()
        self.cfg1=tkinter.Checkbutton(master=self.frame_1, text="Automatically save after compiling", variable=self.cfg1var)
        self.cfg2=tkinter.Checkbutton(master=self.frame_1, text="Automatically delete last log after compiling", variable=self.cfg2var)
        self.cfg2b=tkinter.Checkbutton(master=self.frame_1, text="Automatically CLEAR ALL logs after compiling", variable=self.cfg2bvar)
        self.cfg3=tkinter.Checkbutton(master=self.frame_1, text="Automatically run test file after compiling", variable=self.cfg3var)
        self.cfg4=tkinter.Checkbutton(master=self.frame_1, text="Automatically sort files after decompiling", variable=self.cfg4var)
        self.preset=tkinter.Label(self.frame_1, text=f'Current preset: {os.path.basename(preset)}')
        self.b7=tkinter.Button(self.frame_1, text='Save preset', command= lambda: savepreset())
        self.b8=tkinter.Button(self.frame_1, text='Load preset', command= lambda: loadpreset())

        #restore entries based on user's settings and load the first accessible page
        resetEntries()
        layoutMode(0,0,0, mode=self.box1.cget('values')[0])

        if warn:
            if warn['type'] == 1:
                MSG1 = "The settings file was found but could not be loaded."
                MSG2 = "To avoid conflicts, the file in question was renamed to "+warn['newfilename']+"."
                MSG3 = "Check the console for details."
                self.w1 = messagebox.showwarning(title='Warning', message=f"{MSG1}\n{MSG2}\n{MSG3}")
                warn = False
                root.focus_force()

def main(settingsfile=None):
    os.chdir(os.path.dirname(os.path.realpath(__file__))) #paranoia
    global preset
    if settingsfile == None: 
        settingsfile = os.path.basename(__file__).replace(".py","_settings.txt")
        preset = "(Default)"
    else:
        preset = settingsfile

    #Try to load settings file, if there is one, and is valid
    global settings
    warn = {}
    if os.path.exists(settingsfile):
        try:
            settings = import_path(settingsfile)
            print("Found settings file.\n")
        except Exception as e:
            print(f"Couldn't load settings file. Reason: {e}")
            try:
                os.rename(settingsfile, settingsfile.replace(".txt","_INVALID.txt"))
                print("Added '_INVALID' to the end of filename.")
            except:
                os.unlink(settingsfile.replace(".txt","_INVALID.txt"))
                print("Deleted previous '_INVALID' file.")
                os.rename(settingsfile, settingsfile.replace(".txt","_INVALID.txt"))
                print("Added '_INVALID' to the end of filename.")
            warn['type'] = 1 #Settings file could not be loaded.
            warn['newfilename'] = os.path.basename(settingsfile).replace('.txt','_INVALID.txt')
    else: print("Settings file not found, running anyway.\n")

    #Create the app's window
    root = tkinter.Tk()
    GUI = UI(root, warn)
    root.title("SRB2Compiler")
    root.geometry('320x320')
    root.mainloop()

def run(onlysave=False, location='', sevenzip='', result='', destination='', testbat='', pk3toextract='', logs='',
        autosave=None, autormlog=None, autoclear=None, autotest=None, autosort=None):
    variables = vars()
    if not(onlysave):
        location = validate_path(location, "the location of the mod")
        sevenzip = validate_path(sevenzip, "sevenzip's path")
        if not(location and sevenzip): return
        try:
            if result == '': result = os.path.splitext(os.path.basename(location))[0]
            if destination == '': destination = os.path.dirname(os.path.realpath(__file__))
            else: destination = validate_path(destination, "the destination of the mod")
            if not destination: return
            clean(sevenzip, result, destination)
            ziptopk3(location, result, destination, sevenzip)
        except Exception as e:
            print(f"ERROR: {e}")
            messagebox.showerror(title="Error", message=e)
            return
        if autotest or autotest==None: test(testbat)
        if autoclear: clean_logs(logs, "ALL")
        elif autormlog: clean_logs(logs)

    if onlysave or autosave: settings_save(variables, onlysave)

def settings_save(variables, settingsfile=False):
    if type(settingsfile) is bool:
        settingsfile = preset
        if preset == "(Default)":
            settingsfile = __file__.replace(".py","_settings.txt")
    #TODO: don't delete vars that won't be replaced?
    #don't save these
    try: del variables['variables']
    except: pass
    try: del variables['onlysave']
    except: pass
    if variables['autoclear'] == 0:
        try: del variables['autoclear']
        except: pass
    #iteration time... is this even readable?
    try:
        settings = f""
        for v in list(variables.items()):
            settings += f"{v[0]} = {repr(v[1])}\n" #variable_name = variable, then go to the next line
        with open(settingsfile, "w") as outfile:
            outfile.write(settings)
            print(f"Saved settings to {os.path.basename(settingsfile)}")
    except Exception as e:
        print(f"Couldn't save settings file. Reason: {e}")
        messagebox.showwarning(title='Warning', message="Something went wrong when trying to save the settings file.\nCheck the console for details.")

def clean_logs(folder, all=False):
    folder = validate_path(folder, "the log's path")
    if not folder: return

    print("\nCleaning logs folder...")
    count = 0
    if all:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Unlinked: {filename}")
                    count += 1
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        print(f"Finished cleaning, {count} files total.")
    else:
        files = os.listdir(folder)
        paths = [os.path.join(folder, basename) for basename in files]
        newest = max(paths, key=os.path.getctime)
        try:
            os.unlink(newest)
            print(f"Unlinked lastest log: {newest}")
        except Exception as e: 
            print('Failed to delete %s. Reason: %s' % (newest, e))

def validate_path(path, name="an unknown path"):
    try: path = path.replace('"','')
    except: pass
    try: path = path.replace("'","")
    except: pass
    try:
        if platform.system() == "Windows":
            path = path.replace("/","\\")
    except: pass
    if path == "":
        err = f"{name} is empty."
        print(f"ERROR: {err}")
        messagebox.showerror(title="Error", message=err);
        return False
    if not os.path.exists(path):
        err = f"Couldn't parse {name}.\nCheck the console for details."
        print(f"ERROR: Couldn't parse {path}.")
        messagebox.showerror(title="Error", message=err);
        return False
    return path

if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
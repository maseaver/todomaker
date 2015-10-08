import sys
import json
from tkinter import filedialog

def getFiles(failedargs):
    newfiles = []
    
    if failedargs:
        if failedargs == -1:
            answer = input("""\
You didn't specify any files as input, would you like to continue? y/n
>""")
            if answer in ["n", ""]:
                raise SystemExit
        else:
            answer = input("""\
One or more of the command line arguments couldn't be opened, would you like to
specify additional input files? y/n
>""")
            if answer in ["n", ""]:
                return newfiles, -1
    
    prompt = """\
Please select the filename of one of the files you want to input to this
script, or hit enter with the filename box empty to finish."""
    
    filename = "foo"
    while filename:
        print(prompt)
        
        filename = filedialog.askopenfilename()
        
        if filename:
            try:
                with open(filename) as f:
                    pass
            except OSError as e:
                error = """\
Input failed for filename "%s".""" % file
                print(error % file)
                print(e)
            else:
                newfiles.append(filename)
    
    return newfiles, -1

def getFormats(files):
    neededKeys = ["prefix", "catchall", "keywords", "sep"]
    default = {"prefix" : "##",
               "catchall" : "!!",
               "keywords" : ["game", "program", "task", "notes"],
               "sep" : ","}
    answer = "foo"
    formatList = []
    for file in files:
        if answer not in "dD":
            answer = input("""\
Would you like to select a JSON file to serve as the format specifier for:
    {0}
or would you like to use the default format?
    prefix: "{1[prefix]}"
    catchall: "{1[catchall]}"
    keywords: "{1[keywords]!s}"
    (keyword) sep(arator) : "{1[sep]}"

Your options are:
    Y: Yes, select a format specifier
    N: No, but continue asking, I might for a later file
    S: Enter from scratch
    D: No, use the default format for all files
If you successfully load or enter a format, you'll have the option of setting
it as the default for the remaining files. If your load attempt is
unsuccessful, you can either try again, do it from scratch, or quit the script.
> """.format(file, default))
            if answer not in ["y", "Y", "n", "N", "d", "D", "s", "S"]:
                answer = "n"
                print("Didn't get that, so I'll assume \"no.\"")
                formatList.append(default)
            elif answer in "yY":
                while True:
                    formatFilename = filedialog.askopenfilename()
                    
                    try:
                        with open(formatFilename) as f:
                            temp = json.load(f)
                    except OSError as e:
                        error = """\
Input failed for filename "%s".""" % formatFilename
                        print(error)
                        print(e)
                        temp = {}
                        
                        if keepTrying(file) == "s":
                            for key in neededKeys:
                                temp[key] = scratch(key)
                            
                            if keepFormat(temp):
                                default = temp
                                
                            formatList.append(temp)
                            
                        elif keepTrying:
                            continue
                        else:
                            formatList.append(default)
                    except ValueError as e:
                        error = """\
"%s" doesn't appear to be properly formatted for JSON deserialization.\
""" % formatFilename
                        print(error)
                        print(e)
                        temp = {}
                        
                        if keepTrying(file) == "s":
                            for key in neededKeys:
                                temp[key] = scratch(key)
                            if keepFormat(temp):
                                default = temp
                            formatList.append(temp)
                        elif keepTrying:
                            continue
                        else:
                            formatList.append(default)
                    else:
                        missing = []
                        incorrectKeywords = False
                        
                        for key in neededKeys:
                            if key in temp:
                                if key == "keywords":
                                    if type(temp[key]) != type([]):
                                        incorrectKeywords = True
                            else:
                                missing.append(key)
                        
                        if missing:
                            for item in missing:
                                print("Key %s is not in the object loaded."
                                      % item)
                                
                                temp[item] = scratch(item)
                                
                        if incorrectKeywords:
                            print("Keywords not a list/JSON array.")
                            
                            temp["keywords"] = scratch("keywords")
                        
                        if keepFormat(temp):
                            default = temp
                            
                        formatList.append(temp)
            elif answer in "sS":
                temp = {}
                
                for key in neededKeys:
                    temp[key] = scratch(key)
                
                if keepFormat(temp):
                    default = temp
                
                formatList.append(temp)
                
            else:
                formatList.append(default)
                
        else:
            formatList.append(default)
        
        return formatList
                
def keepTrying(file):
    prompt = """\
Try to find another format file for %s? y/n (use default)/s (make from scratch)
/q (quit script)
> """ % file 
    answer = input(prompt)
    if answer in "yY":
        return True
    elif answer in "qQ":
        raise SystemExit
    elif answer in "sS":
        return "s"
    elif answer in "nN":
        return False
    else:
        print("Didn't get that, so I'll assume \"no.\"")
        return False

def scratch(key):
    if key == keywords:
        value = []
        keyword = "foo"
        
        while keyword:
            keyword = input("""\
Enter a keyword, or the empty string if you're done. {} keyword(s) entered.
> """.format(len(value)))
            if keyword:
                value.append(keyword)
            elif not value:
                keyword = input("""\
It's fine to leave "keywords" empty, that actually won't do anything
particularly untoward, but I just want to check that that's what you want. If
not, enter something now.
> """)
                if keyword:
                    value.append(keyword)
    else:
        value = input("""\
Enter a value for {}.
> """.format(key))
        if value:
            return value
        else:
            value = input("""\
I just want to make sure, you want to leave {} blank? If not, enter something.
> """.format(key))
            return value

def keepFormat(form):
    print(form)
    answer = input("""\
Do you want to keep the format you just made or loaded as the default? y/n
> """)
    
    if answer in "yY":
        return True
    elif answer in "nN":
        return False
    else:
        print("Didn't get that, so I'll assume \"no.\"")
        return False

def getTodos(file, form):
    newkeyed = {"chunks" : []}
    newkeyed.update(dict.fromkeys(form["keywords"], []))
    
    with open(file) as f:
        catchall = False
        chunk = []
        chunky = {"chunks"}
        linenum = 0
        
        for line in f:
            linenum = linenum + 1
            comment, catchall, keys = lineLogic(line, form, catchall)
            print(keys)
            chunky.update(keys)
            
            if comment:
                if chunk:
                    chunk.append(comment)
                else:
                    chunk.extend(["\t{}, line {}:\n".format(file, linenum),
                                 comment])
            elif chunk:
                print(chunky)
                for key in chunky:
                    newkeyed[key].append(chunk)
                    chunk, chunky = [], {"chunks"}
    
    return newkeyed

def lineLogic(line, form, catchall):
    comment = ""
    keys = set()
    newcatchall = False
    
    p, c, kws, s = (form["prefix"], form["catchall"],
                    form["keywords"], form["sep"])
        
    if p in line:
        comment = line[line.index(p):]
        parsed = comment[len(p):]
        
        if parsed.startswith(c):
            newcatchall = True
        else:
            for kw in kws:
                if parsed.startswith(kw + s):
                    keys.add(kw)
                    parsed = parsed[len(kw + s):]
                    continue
                elif parsed.startswith(kw + c):
                    keys.add(kw)
                    newcatchall = True
                    break
                elif parsed.startswith(kw):
                    keys.add(kw)
                    break
    
    if catchall:
        comment = line
    
    if newcatchall:
        catchall = not catchall
    
    return comment, catchall, keys

def writeFile(key, chunks, overwrite):
    failure = True
    filename = "{}.todo".format(key)
    while failure:
        try:
            with open(filename) as f:
                pass
        except OSError as e:
            try:
                with open(filename, "w") as f:
                    for chunk in chunks:
                        for line in chunk:
                            f.write(line)
                        f.write("\n")
            except OSError as f:
                print("""\
The file {} exists and the file system doesn't want me to touch it. Please
enter a different one.""".format(filename))
                filename = filedialog.asksaveasfilename()
                continue
            else:
                failure = False
        else:
            if overwrite:
                with open(filename, "w") as f:
                    for chunk in chunks:
                        for line in chunk:
                            f.write(line)
                        f.write("\n")
                failure = False
            else:   
                answer = input("""\
Yo, {} exists. Do you want to overwrite it? y/n
> """.format(filename))
                if answer in "yY":
                    print("""\
Okay, your funeral I guess.""")
                    with open(filename, "w") as f:
                        for chunk in chunks:
                            for line in chunk:
                                f.write(line)
                            f.write("\n")
                    failure = False
                elif answer in "nN":
                    print("""\
Okay, enter a new one.""")
                    filename = filedialog.asksaveasfilename()
                    continue
                else:
                    print("""\
Didn't get that, so I'm assuming "no." (Aren't you glad this is my default
behavior for garbled input?)""")
                    filename = filedialog.asksaveasfilename()
                    continue

if __name__ == "__main__":
    files = []
    failedargs = 0
    arguments = sys.argv[1:]
    overwrite = False
    
    if "-o" in arguments:
        arguments.pop(arguments.index("-o"))
        overwrite = True
    
    if len(arguments) > 0:
        for file in arguments:
            try:
                with open(file) as f:
                    pass
            except OSError as e:
                error = """\
Input failed for argument "%s".""" % file
                print(error % file)
                print(e)
                failedargs = 1
            else:
                files.append(file)
    while (not files or failedargs) and not (not files and failedargs):
        newfiles, failedargs = getFiles(failedargs)
        files.extend(newfiles)
    
    formats = getFormats(files)
    
    keyed = {"chunks" : []}
    
    for form in formats:
        keyed.update(dict.fromkeys(form["keywords"], []))
        
    for filename, form in zip(files, formats):
        newkeyed = getTodos(filename, form)
                
        for key in newkeyed.keys():
            keyed[key].extend(newkeyed[key])
    
    if not overwrite:
        print("""\
Gonna try to write all these chunks to files, now. There are some default
filenames that I'll try to use first, but don't worry, I won't overwrite
anything without your express permission. (For reference, the default filenames
are "chunks.todo" and "<keyword>.todo" for every keyword you put in, if any.\
""")
    
    for key, chunks in keyed.items():
        writeFile(key, chunks, overwrite)
    

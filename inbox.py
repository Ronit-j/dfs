from Tkinter import *
from tkFileDialog  import asksaveasfilename, SaveAs
from tkMessageBox  import showinfo, showerror, askyesno
from textEditor import TextEditorComponentMinimal
from email.parser import Parser
import re
import socket
import ssl
import rfc822, StringIO, string, sys
import datetime
import client_GUI
import copy

CRLF = "\r\n"
host = "imap.gmail.com"
port = 993
user = "pranav2000joglekar@gmail.com"
pas = "Pranav2000"
global fileI, fileII, sockI, sockII
ssl_context = ssl._create_stdlib_context(certfile = None, keyfile = None)
pend_tag = {"a"}
msgList       = []                       # list of retrieved emails text
listBox       = None                     # main window's scrolled msg list


#GUI CODE STARTS HERE

def onViewFormatMail():
    # view selected message
    msgnum = selectedMsg()
    if not (1 <= msgnum <= len(msgList)):
        showerror('PyMail', 'No message selected')
    else:
        parser = Parser()

        email = parser.parsestr(msgList[msgnum-1])

        body = ""
        if email.is_multipart():
            for part in email.walk():
                if part.is_multipart():
                    for subpart in part.get_payload():
                        if subpart.is_multipart():
                            for subsubpart in subpart.get_payload():
                                body = body + str(subsubpart.get_payload(decode=True)) + '\n'
                        else:
                            body = body + str(subpart.get_payload(decode=True)) + '\n'
                else:
                    body = body + str(part.get_payload(decode=True)) + '\n'
        else:
            body = body + str(email.get_payload(decode=True)) + '\n'

        body = str(body).decode('unicode-escape')
        file_name = "file" + str(msgnum)
        ttext = copy.deepcopy(client_GUI.client_read(file_name))
        print("--ttext below")
        print(ttext)
        editmail('Write',
                file_name,
                "email.get('To')",
                "email.get('Subject')",
                ttext,
                "email.get('Date')"
            )




def fillIndex(msgList):
    # fill all of main listbox
    listBox.delete(0, END)
    count = 1
    for msg in msgList:
        # print msg
        # hdrs = rfc822.Message(StringIO.StringIO(msg))
        # print hdrs
        num = '%02d' % count
        # for key in ('Subject', 'From', 'Date'):
            # if hdrs.has_key(key): msginfo = msginfo + ' | ' + hdrs[key][:30]
        listBox.insert(END, str(count) + '\t|\t' + msg)
        count = count+1
    listBox.see(END)         # show most recent mail=last line


def selectedMsg():
    # get msg selected in main listbox
    # print listBox.curselection()
    if listBox.curselection() == ():
        return 0                                     # empty tuple:no selection
    else:                                            # else zero-based index
        return eval(listBox.curselection()[0]) + 1   # in a 1-item tuple of str


def waitForThreadExit(win):
    import time
    global threadExitVar
    delay = 0.0
    while not threadExitVar:
        win.update()
        time.sleep(delay)
    threadExitVar = 0


def busyInfoBoxWait(message):


    popup = Toplevel()
    popup.title('PyMail Wait')
    popup.protocol('WM_DELETE_WINDOW', lambda:0)
    label = Label(popup, text=message+'...')
    label.config(height=10, width=40, cursor='watch')
    label.pack()
    popup.focus_set()
    popup.grab_set()
    waitForThreadExit(popup)
    print 'thread exit caught'
    popup.destroy()


def onViewRawMail():
    # view selected message - raw mail text with header lines
    msgnum = selectedMsg()
    print(len(msgList))
    if not (1 <= msgnum <= len(msgList)):
        showerror('PyMail', 'No message selected')
    else:
        text = client_GUI.client_read("file"+str(msgnum))                # put in ScrolledText
        from ScrolledText import ScrolledText
        window  = Toplevel()
        window.title('PyMail raw message viewer #' + str(msgnum))
        browser = ScrolledText(window)
        browser.insert('0.0', text)
        browser.pack(expand=YES, fill=BOTH)



def onLoadMail():

    # mails = useless()

    # for i in mails:
    #     mail = i
    #     new_mail = [x.rstrip() for x in mail]
    #     emailText = '\n'.join(new_mail)
    #     msgList.append(emailText)

    # msgListd = [ "file1" , "file2" ]

    global msgList

    msgList = copy.deepcopy(client_GUI.client_list())

    # print(msgListd)

    print(msgList)

    fillIndex(msgList)


def decorate(rootWin):
    # window manager stuff for main window
    rootWin.title('Mail Client')
    # rootWin.protocol('WM_DELETE_WINDOW', onQuitMail)

def makemainwindow(parent=None):
    # make the main window - by default shows inbox
    global rootWin, listBox, allModeVar
    if parent:
        rootWin = Frame(parent)             # attach to a parent
        rootWin.pack(expand=YES, fill=BOTH)
    else:
        rootWin = Tk()                      # assume I'm standalone
        decorate(rootWin)

    # add main buttons at bottom
    frame1 = Frame(rootWin)
    frame1.pack(side=BOTTOM, fill=X)
    allModeVar = IntVar()
    Checkbutton(frame1, text="All", variable=allModeVar).pack(side=RIGHT)
    actions = [ ('Load',  onLoadMail),  ('View',  onViewFormatMail),
                ('Save',  onSaveMail),  ('Del',   onDeleteMail),
                ('Write', onWriteMail), ('Reply', onReplyMail),
                ('Fwd',   onFwdMail),   ('Quit',  onQuitMail) ]
    for (title, callback) in actions:
        Button(frame1, text=title, command=callback).pack(side=LEFT, fill=X)

    # add main listbox and scrollbar
    frame2  = Frame(rootWin)
    vscroll = Scrollbar(frame2)
    fontsz  = (sys.platform[:3] == 'win' and 8) or 10
    listBox = Listbox(frame2, bg='white', font=('courier', fontsz))

    # crosslink listbox and scrollbar
    vscroll.config(command=listBox.yview, relief=SUNKEN)
    listBox.config(yscrollcommand=vscroll.set, relief=SUNKEN, selectmode=SINGLE)
    listBox.bind('<Double-1>', lambda event: onViewRawMail())
    frame2.pack(side=TOP, expand=YES, fill=BOTH)
    vscroll.pack(side=RIGHT, fill=BOTH)
    listBox.pack(side=LEFT, expand=YES, fill=BOTH)
    return rootWin
def onWriteReplyFwdSend(w,e,h,file_name):
    print(e.getAllText())
    print(file_name)
    client_GUI.client_write(e.getAllText(),file_name)

    # print(w,e,h)
    # print(w.keys())
    # for kk in h:
    #     for i in kk.keys():
    #         print(kk[i])
def editmail(mode, From, To='', Subj='', origtext='', Date=''):
    # create a new mail edit/view window
    win = Toplevel()
    win.title('PyMail - '+ mode)
    win.iconname('PyMail')
    viewOnly = (mode[:4] == 'View')

    # header entry fields
    frm =  Frame(win); frm.pack( side=TOP,   fill=X)
    lfrm = Frame(frm); lfrm.pack(side=LEFT,  expand=NO,  fill=BOTH)
    mfrm = Frame(frm); mfrm.pack(side=LEFT,  expand=NO,  fill=NONE)
    rfrm = Frame(frm); rfrm.pack(side=RIGHT, expand=YES, fill=BOTH)
    hdrs = []
    for (label, start) in [('From:', From),
                           ('To:',   To),           # order matters on send
                           ('Date:',   Date),
                           ('Subj:', Subj)]:
        lab = Label(mfrm, text=label, justify=LEFT)
        ent = Entry(rfrm)
        lab.pack(side=TOP, expand=YES, fill=X)
        ent.pack(side=TOP, expand=YES, fill=X)
        ent.insert('0', start)
        hdrs.append(ent)

    # send, cancel buttons (need new editor)
    editor = TextEditorComponentMinimal(win)
    sendit = (lambda w=win, e=editor, h=hdrs: onWriteReplyFwdSend(w, e, h, From))


    for (label, callback) in [('Cancel', win.destroy), ('Send', sendit)]:
        if not (viewOnly and label == 'Send'):
            b = Button(lfrm, text=label, command=callback)
            b.config(bg='beige', relief=RIDGE, bd=2)
            b.pack(side=TOP, expand=YES, fill=BOTH)
    # body text editor: pack last=clip first
    editor.pack(side=BOTTOM)
    # print(origtext)                        # may be multiple editors
    editor.setAllText(origtext)

    if viewOnly:
        editor.freeze()


def onWriteMail():
    # compose new email
    now = str(datetime.datetime.now())

    editmail('Write', From="shivani@mind-spark.org", Date=now)


def container():
    #Inbox, sentbox, compose menu bar
     #title = Menu(root)
    rootWin = Tk()
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = dummyfunction)
    submenu.add_command(label = "Sentbox", command = sentboxwindow)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)


    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    tag = Button(rootWin, text='Inbox')
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    decorate(rootWin)
    return rootWin

def sentboxwindow(parent=None):
    # make the main window - by default shows inbox
    global rootWin, listBox, allModeVar
    #rootWin.protocol('WM_DELETE_WINDOW', lambda:0)
    if parent:
        rootWin = Frame(parent)             # attach to a parent
        rootWin.pack(expand=YES, fill=BOTH)
    else:
        rootWin = Tk()                      # assume I'm standalone
        decorate(rootWin)

    rootWin = Tk()
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = makemainwindow)
    submenu.add_command(label = "Sentbox", command = dummyfunction)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)


    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    tag = Button(rootWin, text='SentBox')
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    #decorate(rootWin)


    # add main buttons at bottom
    frame1 = Frame(rootWin)
    frame1.pack(side=BOTTOM, fill=X)
    allModeVar = IntVar()
    Checkbutton(frame1, text="All", variable=allModeVar).pack(side=RIGHT)
    actions = [ ('Load',  onLoadMail),  ('View',  onViewFormatMail),
                ('Save',  onSaveMail),  ('Del',   onDeleteMail),
                ('Write', onWriteMail), ('Reply', onReplyMail),
                ('Fwd',   onFwdMail),   ('Quit',  onQuitMail) ]
    for (title, callback) in actions:
        Button(frame1, text=title, command=callback).pack(side=LEFT, fill=X)

    # add main listbox and scrollbar
    frame2  = Frame(rootWin)
    vscroll = Scrollbar(frame2)
    fontsz  = (sys.platform[:3] == 'win' and 8) or 10
    listBox = Listbox(frame2, bg='white', font=('courier', fontsz))

    # crosslink listbox and scrollbar
    vscroll.config(command=listBox.yview, relief=SUNKEN)
    listBox.config(yscrollcommand=vscroll.set, relief=SUNKEN, selectmode=SINGLE)
    listBox.bind('<Double-1>', lambda event: onViewRawMail())
    frame2.pack(side=TOP, expand=YES, fill=BOTH)

    vscroll.pack(side=RIGHT, fill=BOTH)
    listBox.pack(side=LEFT, expand=YES, fill=BOTH)
    #rootWin = makemainwindow(container_sentbox())
    #return rootWin
    decorate(rootWin)
    return rootWin

def container_sentbox():
    #Inbox, sentbox, compose menu bar
     #title = Menu(root)
    rootWin = Tk()
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = makemainwindow)
    submenu.add_command(label = "Sentbox", command = dummyfunction)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)


    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    tag = Button(rootWin, text='SentBox')
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    #decorate(rootWin)
    return rootWin

def dummyfunction():
    print("You are already here!")


def selectedMsg():
    # get msg selected in main listbox
    # print listBox.curselection()
    if listBox.curselection() == ():
        return 0                                     # empty tuple:no selection
    else:                                            # else zero-based index
        return listBox.curselection()[0] + 1   # in a 1-item tuple of str

global fileI, fileII, sockI, sockII
ssl_context = ssl._create_stdlib_context(certfile = None, keyfile = None)
pend_tag = {"a"}
def message():
    global fileI, fileII, sockI, sockII
    resp = ''
    while True:
        lineI = fileI.readline()
        #print lineI
        resp = resp + lineI
        tag = lineI.split(" ")[0]
        if tag in pend_tag:
            break
    return resp

def get_mail():
    global fileI, fileII, sockI, sockII
    mail = []
    lineI = fileI.readline()
    while True:
        lineI = fileI.readline()
        mail.append(lineI)
        tag = lineI.split(" ")[0]
        if tag in pend_tag:
            break
    return mail


def useless():
    global fileI, fileII, sockI, sockII
    sockI = socket.create_connection((host, port))
    sockII = ssl_context.wrap_socket(sockI, server_hostname = host)
    #fileI = sockI.makefile('rb')
    fileI = sockII.makefile('rb')
    #CAPABILITY TEST
    cmd = '%s%s' % ("a CAPABILITY", CRLF)
    cmd = cmd.encode('ascii')
    sockII.sendall(cmd)
    message()

    #LOGIN
    cmd = '%s %s %s %s%s' % ("a","LOGIN",user,pas, CRLF)
    cmd = cmd.encode('ascii')
    sockII.sendall(cmd)
    message()
    #SELECT INBOX

    cmd = '%s %s %s%s' % ("a","SELECT","INBOX", CRLF)
    cmd = cmd.encode('ascii')
    sockII.sendall(cmd)
    #print lineI
    out = message()
    msg_no = int(out.split("\n")[3].split(" ")[1])
    uid = int(out.split("\n")[5].split("]")[0].split(" ")[3])

    #GET Email
    #message with id - 13126 used for test case.
    #a FETCH 13127 BODY[]
    mails = []
    for i in range(msg_no - 20, msg_no):
        cmd = '%s %s %s %s%s' % ("a", "FETCH", str(i), "BODY[]", CRLF)
        cmd = cmd.encode('ascii')
        sockII.sendall(cmd)
        #message()
        mail1 = get_mail()
        mails.append(mail1)
    return mails

#mail_fetched = useless()


# use objects that retain prior directory for the next
# select, instead of simple asksaveasfilename() dialog

saveOneDialog = saveAllDialog = None


def onSaveMail():
    pass
def onDeleteMail():
    pass
def onReplyMail ():
    editmail('Write', From="shivani@mind-spark.org", To="pranavjoglekar@mind-spark.org")
def onFwdMail():
    pass
def onQuitMail():
    pass
def mail_extractor():
    pass

if __name__ == '__main__':
    # run stand-alone or attach
    rootWin = makemainwindow(container())    # or makemainwindow()
    rootWin.mainloop()

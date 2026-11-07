import os
import csv
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

FILE="studata.csv"

BG="#EDF2F9"
HEADER="#C5D5EC"
ACCENT="#2F5C9E"
ACCENT_DARK="#1B3A6B"
TEXT="#1F2D45"
SELECT="#B7CCEC"
STRIPE="#F2F6FC"
RED="#D6455D"
WARN="#D98E04"
FONT="Segoe UI"
SORTS=("Name (A-Z)","Name (Z-A)","Average (High to Low)","Average (Low to High)")

class Node:
    def __init__(self,nm,q1,q2,q3):
        self.nm=nm
        self.q1=q1
        self.q2=q2
        self.q3=q3
        self.next=None

    def ave(self):
        return (self.q1+self.q2+self.q3)/3


class StudentList:
    def __init__(self):
        self.head=None

    def locate(self,nm):
        cur=self.head
        while cur is not None:
            if cur.nm==nm:
                return cur
            cur=cur.next
        return None

    def append(self,node):
        if self.head is None:
            self.head=node
        else:
            cur=self.head
            while cur.next is not None:
                cur=cur.next
            cur.next=node

    def add(self,node):
        if self.locate(node.nm) is not None:
            return False
        self.append(node)
        return True

    def delete(self,nm):
        if self.head is None:
            return False
        if self.head.nm==nm:
            self.head=self.head.next
            return True
        prev=self.head
        while prev.next is not None and prev.next.nm!=nm:
            prev=prev.next
        if prev.next is None:
            return False
        prev.next=prev.next.next
        return True

    def update(self,nm,q1,q2,q3):
        r=self.locate(nm)
        if r is None:
            return False
        r.q1=q1
        r.q2=q2
        r.q3=q3
        return True

    def before(self,a,b,by,reverse):
        if by=="name":
            x=a.nm.lower()
            y=b.nm.lower()
        else:
            x=a.ave()
            y=b.ave()
        if reverse:
            return x>y
        return x<y

    def sort(self,by,reverse=False):
        new_head=None
        cur=self.head
        while cur is not None:
            nxt=cur.next
            cur.next=None
            if new_head is None or self.before(cur,new_head,by,reverse):
                cur.next=new_head
                new_head=cur
            else:
                p=new_head
                while p.next is not None and not self.before(cur,p.next,by,reverse):
                    p=p.next
                cur.next=p.next
                p.next=cur
            cur=nxt
        self.head=new_head

    def save(self,path=FILE):
        with open(path,"w",newline="") as f:
            w=csv.writer(f)
            w.writerow(["Name","Quiz1","Quiz2","Quiz3"])
            cur=self.head
            while cur is not None:
                w.writerow([cur.nm,cur.q1,cur.q2,cur.q3])
                cur=cur.next

    def load(self,path=FILE):
        if not os.path.exists(path):
            return False
        with open(path,newline="") as f:
            rd=csv.reader(f)
            next(rd,None)
            for p in rd:
                if len(p)==4:
                    try:
                        self.add(Node(p[0],int(p[1]),int(p[2]),int(p[3])))
                    except ValueError:
                        pass
        return True


class StudentApp:
    def __init__(self):
        self.st=StudentList()
        loaded=self.st.load()

        self.win=tk.Tk()
        self.win.title("Student Record System")
        self.win.geometry("960x620")
        self.win.minsize(860,580)
        self.win.configure(bg=BG)

        self.nm=tk.StringVar()
        self.q1=tk.StringVar()
        self.q2=tk.StringVar()
        self.q3=tk.StringVar()
        self.msg=tk.StringVar(value="Ready.")
        self.summary=tk.StringVar()
        self.sort_var=tk.StringVar(value=SORTS[0])

        self.style()
        self.build()
        self.refresh()
        self.win.protocol("WM_DELETE_WINDOW",self.exit)

        self.loaded=loaded
        self.win.after(300,self.start_msg)

    def start_msg(self):
        if self.loaded:
            self.popup("info","File","File is loaded.")
        else:
            self.popup("info","File","No file found. A new file will be created.")

    def popup(self,kind,title,message,yesno=False):
        colors={"info":ACCENT,"warning":WARN,"error":RED,"question":ACCENT}
        symbols={"info":"i","warning":"!","error":"x","question":"?"}
        color=colors[kind]
        self.result=False

        dlg=tk.Toplevel(self.win)
        dlg.title(title)
        dlg.configure(bg=BG)
        dlg.resizable(False,False)
        dlg.transient(self.win)

        head=tk.Frame(dlg,bg=color)
        head.pack(fill=tk.X)
        tk.Label(head,text=title,bg=color,fg="white",font=(FONT,12,"bold"),padx=16,pady=10).pack(anchor=tk.W)

        body=ttk.Frame(dlg)
        body.pack(fill=tk.BOTH,expand=True,padx=18,pady=16)
        icon=tk.Canvas(body,width=44,height=44,bg=BG,highlightthickness=0)
        icon.create_oval(2,2,42,42,fill=color,outline="")
        icon.create_text(22,22,text=symbols[kind],fill="white",font=(FONT,18,"bold"))
        icon.pack(side=tk.LEFT,padx=(0,14))
        ttk.Label(body,text=message,wraplength=300,justify=tk.LEFT).pack(side=tk.LEFT)

        row=ttk.Frame(dlg)
        row.pack(fill=tk.X,padx=18,pady=(0,16))
        if yesno:
            ttk.Button(row,text="Yes",command=lambda:self.close(dlg,True)).pack(side=tk.RIGHT,padx=(8,0))
            ttk.Button(row,text="No",command=lambda:self.close(dlg,False),style="Exit.TButton").pack(side=tk.RIGHT)
        else:
            ttk.Button(row,text="OK",command=lambda:self.close(dlg,True)).pack(side=tk.RIGHT)

        dlg.protocol("WM_DELETE_WINDOW",lambda:self.close(dlg,False))
        dlg.bind("<Return>",lambda e:self.close(dlg,True))
        dlg.bind("<Escape>",lambda e:self.close(dlg,False))
        dlg.update_idletasks()
        x=self.win.winfo_x()+(self.win.winfo_width()-dlg.winfo_width())//2
        y=self.win.winfo_y()+(self.win.winfo_height()-dlg.winfo_height())//2
        dlg.geometry(f"+{x}+{y}")
        dlg.wait_visibility()
        dlg.grab_set()
        dlg.focus_set()
        self.win.wait_window(dlg)
        return self.result

    def close(self,dlg,value):
        self.result=value
        dlg.destroy()

    def style(self):
        s=ttk.Style(self.win)
        s.theme_use("clam")
        s.configure(".",background=BG,foreground=TEXT,font=(FONT,10))
        s.configure("TFrame",background=BG)
        s.configure("TPanedwindow",background=BG)
        s.configure("TLabel",background=BG,foreground=TEXT)
        s.configure("Title.TLabel",background=ACCENT_DARK,foreground="white",font=(FONT,17,"bold"),padding=(16,12))
        s.configure("Status.TLabel",background=HEADER,foreground=TEXT,padding=(10,5))
        s.configure("TLabelframe",background=BG,bordercolor=ACCENT,lightcolor=ACCENT,darkcolor=ACCENT)
        s.configure("TLabelframe.Label",background=BG,foreground=ACCENT_DARK,font=(FONT,10,"bold"))
        s.configure("TEntry",fieldbackground="white",bordercolor=ACCENT,lightcolor=ACCENT,darkcolor=ACCENT,padding=5)
        s.configure("TButton",background=ACCENT,foreground="white",font=(FONT,10,"bold"),padding=8,borderwidth=0,focusthickness=0)
        s.map("TButton",background=[("pressed",ACCENT_DARK),("active",ACCENT_DARK)])
        s.configure("Exit.TButton",background="#6B7F99")
        s.map("Exit.TButton",background=[("pressed",RED),("active",RED)])
        s.configure("TNotebook",background=BG,borderwidth=0)
        s.configure("TNotebook.Tab",background=HEADER,foreground=TEXT,font=(FONT,10,"bold"),padding=(18,7))
        s.map("TNotebook.Tab",background=[("selected",ACCENT)],foreground=[("selected","white")])
        s.configure("Treeview",background="white",fieldbackground="white",foreground=TEXT,rowheight=30,borderwidth=0,font=(FONT,10))
        s.map("Treeview",background=[("selected",SELECT)],foreground=[("selected",TEXT)])
        s.configure("Treeview.Heading",background=ACCENT,foreground="white",font=(FONT,10,"bold"),padding=7,relief="flat")
        s.map("Treeview.Heading",background=[("active",ACCENT_DARK)])
        s.configure("Vertical.TScrollbar",background=ACCENT,troughcolor=BG,bordercolor=BG,arrowcolor="white")
        s.configure("TCombobox",fieldbackground="white",background=ACCENT,foreground=TEXT,bordercolor=ACCENT,arrowcolor="white",padding=5)
        s.map("TCombobox",fieldbackground=[("readonly","white")],foreground=[("readonly",TEXT)],selectbackground=[("readonly","white")],selectforeground=[("readonly",TEXT)])
        self.win.option_add("*TCombobox*Listbox.selectBackground",ACCENT)
        self.win.option_add("*TCombobox*Listbox.font",(FONT,10))

    def build(self):
        ttk.Label(self.win,text="Student Record System",style="Title.TLabel").pack(fill=tk.X)

        main=ttk.Frame(self.win)
        main.pack(fill=tk.BOTH,expand=True,padx=12,pady=12)

        pane=ttk.PanedWindow(main,orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH,expand=True)

        left=ttk.Frame(pane)
        right=ttk.LabelFrame(pane,text="Student Records")
        pane.add(left,weight=1)
        pane.add(right,weight=4)

        self.build_form(left)
        self.build_menu(left)
        self.build_notebook(right)

        ttk.Label(self.win,textvariable=self.msg,style="Status.TLabel",anchor=tk.W).pack(fill=tk.X)

    def build_form(self,parent):
        form=ttk.LabelFrame(parent,text="Student Details")
        form.pack(fill=tk.X,padx=(0,10),pady=(0,10))
        form.columnconfigure(1,weight=1)

        ttk.Label(form,text="Name:").grid(row=0,column=0,sticky=tk.W,padx=10,pady=6)
        ttk.Entry(form,textvariable=self.nm,width=20).grid(row=0,column=1,sticky=tk.E+tk.W,padx=10,pady=6)
        ttk.Label(form,text="Quiz 1:").grid(row=1,column=0,sticky=tk.W,padx=10,pady=6)
        ttk.Entry(form,textvariable=self.q1,width=20).grid(row=1,column=1,sticky=tk.E+tk.W,padx=10,pady=6)
        ttk.Label(form,text="Quiz 2:").grid(row=2,column=0,sticky=tk.W,padx=10,pady=6)
        ttk.Entry(form,textvariable=self.q2,width=20).grid(row=2,column=1,sticky=tk.E+tk.W,padx=10,pady=6)
        ttk.Label(form,text="Quiz 3:").grid(row=3,column=0,sticky=tk.W,padx=10,pady=6)
        ttk.Entry(form,textvariable=self.q3,width=20).grid(row=3,column=1,sticky=tk.E+tk.W,padx=10,pady=6)

    def build_menu(self,parent):
        menu=ttk.LabelFrame(parent,text="Menu")
        menu.pack(fill=tk.X,padx=(0,10))

        ttk.Button(menu,text="Add Record",command=self.add).pack(fill=tk.X,padx=10,pady=(10,3))
        ttk.Button(menu,text="Update Record",command=self.update).pack(fill=tk.X,padx=10,pady=3)
        ttk.Button(menu,text="Delete Record",command=self.delete).pack(fill=tk.X,padx=10,pady=3)
        ttk.Button(menu,text="Clear Fields",command=self.clear).pack(fill=tk.X,padx=10,pady=3)
        ttk.Button(menu,text="Import CSV...",command=self.import_csv).pack(fill=tk.X,padx=10,pady=3)
        ttk.Button(menu,text="Export CSV...",command=self.export_csv).pack(fill=tk.X,padx=10,pady=3)
        ttk.Button(menu,text="Exit",command=self.exit,style="Exit.TButton").pack(fill=tk.X,padx=10,pady=(3,10))

    def build_notebook(self,parent):
        bar=ttk.Frame(parent)
        bar.pack(fill=tk.X,padx=8,pady=(8,0))
        ttk.Label(bar,text="Sort by:").pack(side=tk.LEFT)
        combo=ttk.Combobox(bar,textvariable=self.sort_var,values=SORTS,state="readonly",width=22)
        combo.pack(side=tk.LEFT,padx=8)
        ttk.Button(bar,text="Sort",command=self.sort).pack(side=tk.LEFT)

        nb=ttk.Notebook(parent)
        nb.pack(fill=tk.BOTH,expand=True,padx=8,pady=8)

        tab_all=ttk.Frame(nb)
        tab_pass=ttk.Frame(nb)
        tab_fail=ttk.Frame(nb)
        tab_summary=ttk.Frame(nb)
        nb.add(tab_all,text="All Records")
        nb.add(tab_pass,text="Passed")
        nb.add(tab_fail,text="Failed")
        nb.add(tab_summary,text="Summary")

        self.tree=self.make_tree(tab_all)
        self.tree_pass=self.make_tree(tab_pass)
        self.tree_fail=self.make_tree(tab_fail)

        box=ttk.LabelFrame(tab_summary,text="Class Statistics")
        box.pack(fill=tk.X,padx=12,pady=12)
        ttk.Label(box,textvariable=self.summary,justify=tk.LEFT).pack(anchor=tk.W,padx=12,pady=12)

    def make_tree(self,parent):
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(0,weight=1)

        cols=("no","name","q1","q2","q3","ave","rem")
        tree=ttk.Treeview(parent,columns=cols,show="headings",selectmode="browse")
        for c,h in zip(cols,("No.","NAME","Q1","Q2","Q3","AVE","REMARKS")):
            tree.heading(c,text=h)
            tree.column(c,width=70,anchor=tk.CENTER)
        tree.column("name",width=190,anchor=tk.W)
        tree.tag_configure("odd",background="white")
        tree.tag_configure("even",background=STRIPE)
        tree.tag_configure("fail",foreground=RED)
        tree.bind("<<TreeviewSelect>>",self.pick)

        sb=ttk.Scrollbar(parent,orient=tk.VERTICAL,command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)
        sb.grid(row=0,column=1,sticky=tk.N+tk.S)
        return tree

    def fill(self,tree,want):
        tree.delete(*tree.get_children())
        cur=self.st.head
        i=1
        while cur is not None:
            a=cur.ave()
            rem="Passed" if a>=75 else "Failed"
            if want is None or want==rem:
                stripe="odd" if i%2==1 else "even"
                tags=(stripe,"fail") if rem=="Failed" else (stripe,)
                tree.insert("","end",tags=tags,
                            values=(i,cur.nm,cur.q1,cur.q2,cur.q3,f"{a:.2f}",rem))
                i+=1
            cur=cur.next

    def refresh(self):
        self.fill(self.tree,None)
        self.fill(self.tree_pass,"Passed")
        self.fill(self.tree_fail,"Failed")
        self.update_summary()

    def update_summary(self):
        total=0
        passed=0
        ave_sum=0
        high=0
        low=100
        cur=self.st.head
        while cur is not None:
            a=cur.ave()
            total+=1
            ave_sum+=a
            if a>=75:
                passed+=1
            high=max(high,a)
            low=min(low,a)
            cur=cur.next
        if total==0:
            low=0
        class_ave=ave_sum/total if total>0 else 0
        self.summary.set(f"Total Students: {total}\n"
                         f"Passed: {passed}\n"
                         f"Failed: {total-passed}\n"
                         f"Class Average: {class_ave:.2f}\n"
                         f"Highest Average: {high:.2f}\n"
                         f"Lowest Average: {low:.2f}")

    def clear_fields_only(self):
        self.nm.set("")
        self.q1.set("")
        self.q2.set("")
        self.q3.set("")

    def clear(self):
        self.clear_fields_only()
        for t in (self.tree,self.tree_pass,self.tree_fail):
            t.selection_remove(t.selection())
        self.msg.set("Fields cleared.")

    def pick(self,event=None):
        tree=event.widget if event is not None else self.tree
        sel=tree.selection()
        if not sel:
            return
        v=tree.item(sel[0],"values")
        self.nm.set(v[1])
        self.q1.set(v[2])
        self.q2.set(v[3])
        self.q3.set(v[4])

    def read_fields(self):
        nm=self.nm.get().strip()
        if nm=="":
            self.popup("warning","Missing Name","Please enter a name.")
            return None
        try:
            q1=int(self.q1.get())
            q2=int(self.q2.get())
            q3=int(self.q3.get())
        except ValueError:
            self.popup("error","Invalid Input","Quiz scores must be whole numbers.")
            return None
        for x in (q1,q2,q3):
            if x<0 or x>100:
                self.popup("error","Invalid Input","Quiz scores must be from 0 to 100.")
                return None
        return nm,q1,q2,q3

    def add(self):
        d=self.read_fields()
        if d is None:
            return
        node=Node(*d)
        if self.st.add(node):
            self.refresh()
            self.msg.set(f"Record added. Average: {node.ave():.2f}")
            self.clear_fields_only()
        else:
            self.popup("warning","Duplicate","Duplicate Record!")
            self.msg.set("Duplicate Record!")

    def update(self):
        d=self.read_fields()
        if d is None:
            return
        if self.st.update(*d):
            self.refresh()
            self.msg.set(f"Record updated for {d[0]}.")
        else:
            self.popup("warning","Not Found","Record not found.")
            self.msg.set("Record not found.")

    def delete(self):
        nm=self.nm.get().strip()
        if nm=="":
            self.popup("warning","Missing Name","Select a record or enter a name to delete.")
            return
        if not self.popup("question","Confirm Delete",f"Delete the record of {nm}?",True):
            return
        if self.st.delete(nm):
            self.refresh()
            self.clear_fields_only()
            self.msg.set("Record deleted.")
        else:
            self.popup("warning","Not Found","Record not found.")
            self.msg.set("Record not found.")

    def sort(self):
        choice=self.sort_var.get()
        if choice=="Name (A-Z)":
            self.st.sort("name",False)
        elif choice=="Name (Z-A)":
            self.st.sort("name",True)
        elif choice=="Average (High to Low)":
            self.st.sort("ave",True)
        else:
            self.st.sort("ave",False)
        self.refresh()
        self.msg.set(f"Sorted by {choice}.")

    def import_csv(self):
        path=filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if path:
            self.st.load(path)
            self.refresh()
            self.msg.set("Records imported.")

    def export_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",
                                          filetypes=[("CSV files","*.csv")])
        if path:
            self.st.save(path)
            self.msg.set("Records exported.")

    def exit(self):
        self.st.save()
        self.popup("info","Goodbye","File is saved, Thank you!\nGoodbye :>")
        self.win.destroy()


if __name__=="__main__":
    app=StudentApp()
    app.win.mainloop()

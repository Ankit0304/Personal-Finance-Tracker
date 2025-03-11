import datetime as dt
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# database of projecct

connection = sqlite3.connect("Finance.db")
cursor = connection.cursor()

connection.execute(
    'CREATE TABLE IF NOT EXISTS Finance (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,Date DATETIME, Category TEXT, Description TEXT, Amount FLOAT, ModeOfPayment TEXT)'
)

connection.commit()

# functions of projects

def list_all_expenses():
    global connection, table
    table.delete(*table.get_children())
    all_data = connection.execute('SELECT * FROM Finance')
    data = all_data.fetchall()
    
    for values in data:
        table.insert('', END, values=values)
        
def view_expense_details():
    global table
    global date, category, desc, amnt,MoP
    
    if not table.selection():
        mb.showerror('No Expense Selected', 'Please select an expense to view its details')
        
    current_selected_expense = table.item(table.focus())
    values = current_selected_expense['values']
    
    expenditure_date = dt.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))
    date.set_date(expenditure_date) ; category.set(values[2]) ; desc.set(values[3]) ; amnt.set(values[4]) ; MoP.set(values[5])
    
def clear_fields():
    global desc, category,amnt,MoP,date,table
    today_date = dt.datetime.now().date()
    
    desc.set('') ; category.set('') ; amnt.set(0.0) ; MoP.set('Cash') ; date.set_date(today_date)
    table.selection_remove(*table.selection())
    
def remove_expense():
    if not table.selection():
        mb.showerror('No Record Selected!', 'Please select a record to delete!')
        return
    current_selected_expense = table.item(table.focus())
    values_selected = current_selected_expense['values']
    
    surety = mb.askyesno('Are you Sure?', f'Are you sure that you want to delete the record of {values_selected[2]}')
    
    if surety:
        connection.execute('DELETE FROM Finance WHERE ID=%d' % values_selected[0])
        connection.commit()
        list_all_expenses()
        mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully!')
        
def remove_all_expenses():
    surety = mb.askyesno('Are you sure?', 'Are sure that you want to delete all the expense item from the database?', icon='warning')
    
    if surety:
        table.delete(*table.get_children())
        
        connection.execute('DELETE FROM Finance')
        connection.commit()
        
        clear_fields()
        list_all_expenses()
        mb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
    
    else:
        mb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')
        
def add_another_expense():
    global date, category, desc, amnt, MoP
    global connection
    
    if not date.get() or not category.get() or not desc.get() or not amnt.get() or not MoP.get():
        mb.showerror('Fields Empty!', 'Please fill all the missinng fileds before pressing the add button!')
    else:
        connection.execute('INSERT INTO finance(Date, Category, Description, Amount, ModeOfPayment) VALUES(?,?,?,?,?)',(dt.datetime.strptime(date.get(), "%m/%d/%y").strftime("%Y-%m-%d"),category.get(),desc.get(),amnt.get(),MoP.get())) 
        
        connection.commit()
        
        clear_fields()
        list_all_expenses()
        mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')

def edit_expense():
    global table
    
    def edit_existing_expense():
        global date, category, desc, amnt, MoP
        global connection, table
        
        current_selected_expense = table.item(table.focus())
        contents = current_selected_expense['values']
        
        connection.execute('UPDATE Finance SET Date = ?, Category = ?, Description = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?', (dt.datetime.strptime(date.get(), "%m/%d/%y").strftime("%Y-%m-%d"), category.get(), desc.get(), amnt.get(), MoP.get(), contents[0]))
        connection.commit()
        
        clear_fields()
        list_all_expenses()
        mb.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
        
        edit_btn.destroy()
        return
    if not table.selection():
        mb.showerror('No expense selected!', 'You have not selected any expense in the table for us to edit ; please do that !')
        return
    
    view_expense_details()
    
    edit_btn = Button(data_entry_frame, text='Edit expense', font=btn_font, width=30, bg= hlb_btn_bg, command=edit_existing_expense)
    edit_btn.place(x=10, y=395)


def selected_expenses_to_words():
    global table
    
    if not table.selection():
        mb.showerror('No expense selected!', 'Please select an expense from the table for us to read')
        return
    
    current_selection_expense = table.item(table.focus())
    values = current_selection_expense['values']
    
    message = f'Your expense can be read like : \n"You paid {values[4]} to {values[2]} for {values[3]} on {values[1]} via {values[5]}"'
    mb.showinfo('Here\'s how to read your expense', message)
    

def expense_to_words_before_adding():
    global date, category, desc, amnt, MoP
    
    if not date or not desc or not category or not amnt or not MoP:
        mb.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')
    
    message = f'Your expense can be read like this : \n "You Paid {amnt.get()} to {category.get()} for {desc.get()} on {date.get_date()} via {MoP.get()}"'
    
    add_question = mb.askyesno('Read your record like: ', f'{message}\n\nShould I add it to the database?')
    
    if add_question:
        add_another_expense()
    else:
        mb.showinfo('Ok', 'Please take your time to add this record')

def generate_transaction_pdf():
    all_data = connection.execute('SELECT * FROM Finance')
    data = all_data.fetchall()

    if not data:
        mb.showinfo("No Transactions", "There are no transactions to print.")
        return

    file_name = "Transactions.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(200, 750, "Personal Finance Tracker - Transactions Report")
    c.drawString(50, 730, "--------------------------------------------------------")

    y_position = 710
    for record in data:
        transaction_text = f"ID: {record[0]}, Date: {record[1]}, Category: {record[2]}, Description: {record[3]}, Amount: {record[4]}, Mode: {record[5]}"
        c.drawString(50, y_position, transaction_text)
        y_position -= 20
        if y_position < 50:  # Create a new page if needed
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750

    c.save()
    mb.showinfo("PDF Generated", f"Transactions saved as {file_name}")


# GUI Bckground code

DataEntry_Frame_bg = 'sky blue'
button_frame_bg = 'light green'
hlb_btn_bg = 'Red'

lbl_font = ('Georgia', 13 )
entry_font = 'Times 13 bold'
btn_font = ('Gill Sans MT', 13)

root = Tk()
root.title('Personal Finance Tracker')
root.geometry('1200x700')
root.resizable(0, 0)

Label(root, text='Personal Finance Tracker', font=('Noto Sans CJK TC',16, 'bold'), bg=hlb_btn_bg).pack(side=TOP, fill=X)

desc = StringVar()
amnt = DoubleVar()
category = StringVar()
MoP = StringVar(value='Cash')

data_entry_frame = Frame(root, bg=DataEntry_Frame_bg)
data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

button_frame = Frame(root, bg=button_frame_bg)
button_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

tree_frame = Frame(root)
tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

Label (data_entry_frame, text='Date (M/DD/YY) :', font=lbl_font, bg=DataEntry_Frame_bg).place(x=10, y=50)
date = DateEntry(data_entry_frame, date=dt.datetime.now().date(), font=entry_font)
date.place(x=160, y=50)

Label(data_entry_frame, text='Category\t :', font=lbl_font, bg=DataEntry_Frame_bg).place(x=10, y=230)
Entry(data_entry_frame, font=entry_font, width=31, text=category).place(x=10, y=260)

Label(data_entry_frame, text='Description :', font=lbl_font, bg=DataEntry_Frame_bg).place(x=10, y=100)
Entry(data_entry_frame, font=entry_font, width=31, text=desc).place(x=10, y=130)

Label(data_entry_frame, text='Amount\t :', font=lbl_font, bg=DataEntry_Frame_bg).place(x=10, y=180)
Entry(data_entry_frame, font=entry_font, width=14, text=amnt).place(x=160, y=180)

Label(data_entry_frame, text='Mode of Payment :', font=lbl_font, bg=DataEntry_Frame_bg).place(x=10, y=310)
mop1 = OptionMenu(data_entry_frame, MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'PhonePe', 'Google Pay', 'Paytm', 'UPI'])
mop1.place(x=160, y=305) ; mop1.configure(width=10, font=entry_font)

Button(data_entry_frame, text='Add Expenses', command=add_another_expense, font=btn_font, width=30, bg=hlb_btn_bg).place(x=10, y=395)
Button(data_entry_frame, text='Convert to words before adding',command=expense_to_words_before_adding, font=btn_font, width=30, bg=hlb_btn_bg).place(x=10, y=450)
Button(data_entry_frame, text='Print Transactions (PDF)', font=btn_font, width=30, bg=hlb_btn_bg, command=generate_transaction_pdf).place(x=10, y=505)


Button(button_frame, text='Delete Expense', font=btn_font, width=25, bg=hlb_btn_bg, command=remove_expense).place(x=30, y=5)

Button(button_frame, text='Clear Fields in DataEntry Frame', font=btn_font, width=25, bg=hlb_btn_bg, command=clear_fields).place(x=335, y=5)

Button(button_frame, text='Delete All Expenses', font=btn_font, width=25, bg=hlb_btn_bg,command=remove_all_expenses).place(x=640, y=5)

Button(button_frame, text='View Selected Expense\'s Details', font=btn_font, width=25, bg=hlb_btn_bg, command=view_expense_details).place(x=30, y=65)

Button(button_frame, text='Edit Selected Expense', command=edit_expense, font=btn_font, width=25,bg=hlb_btn_bg).place(x=335, y=65)

Button(button_frame, text='Convert Expenses to a Sentence', font=btn_font, width=25, bg=hlb_btn_bg, command=selected_expenses_to_words).place(x=640, y=65)




table = ttk.Treeview(tree_frame, selectmode=BROWSE, columns=('ID', 'Date', 'Category', 'Description', 'Amount', 'Mode of Payment'))

X_Scroller = Scrollbar(tree_frame, orient=HORIZONTAL, command=table.xview)
Y_Scroller = Scrollbar(tree_frame, orient=VERTICAL, command=table.yview)
X_Scroller.pack(side=BOTTOM, fill=X)
Y_Scroller.pack(side=RIGHT, fill=Y)

table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

table.heading('ID', text='S No.', anchor=CENTER)
table.heading('Date', text='Date', anchor=CENTER)
table.heading('Category', text='Category', anchor=CENTER)
table.heading('Description', text='Description', anchor=CENTER)
table.heading('Amount', text='Amount', anchor=CENTER)
table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

table.column('#0', width=0, stretch=NO)
table.column('#1',width=50, stretch=NO)
table.column('#2', width=95, stretch=NO)
table.column('#3', width=150, stretch=NO)
table.column('#4', width=325, stretch=NO)
table.column('#5', width=135, stretch=NO)
table.column('#6', width=125, stretch=NO)

table.place(relx=0, y=0, relheight=1, relwidth=1)

list_all_expenses()


root.update()
root.mainloop()


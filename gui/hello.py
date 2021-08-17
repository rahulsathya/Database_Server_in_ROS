import tkinter as tk
import pygubu



app=tk.Tk()
#app.geometry('400x200')

warden_list = ['tb3_0','tb3_1']

#Robot Entry Fields
tk.Label(app, text= 'Robot Fields', font = ('Helvetica', 10,'bold')).grid(row=0)
tk.Label(app, text= 'Explorer Robot List').grid(row=1,pady=4)
tk.Label(app, text = 'Warden Robot List').grid(row=2,pady=4)
tk.Label(app ,text = 'Guide Robot List').grid(row =4,pady=4)


exp_entry = tk.Entry(app).grid(row=1, column=1)
ward_entry = tk.Entry(app)
ward_entry.insert(10, warden_list)
ward_entry.grid(row=2,column=1)
guide_entry = tk.Entry(app).grid(row=4,column=1)



#Quit Button
tk.Button(app, text='Quit', command=app.quit).grid(sticky=tk.S,pady=4)

tk.mainloop()


'''
class HelloWorldApp:
    
	def __init__(self, master):
		self.master = master

		#1: Create a builder
		self.builder = builder = pygubu.Builder()

		#2: Load an ui file
		builder.add_from_file('hello.ui')

		#3: Create the mainwindow
		self.mainwindow = builder.get_object('mainwindow', master)

		#connect callbacks
		builder.connect_callbacks(self)
        
	def on_quit_button_click(self):
		self.master.quit()


if __name__ == '__main__':
	root=tk.Tk()
	app = HelloWorldApp(root)
	root.mainloop()
'''

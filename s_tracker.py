# import libs
import os
import re
import datetime
import pandas as pd
from tkinter import *
from tkinter import messagebox, filedialog
import tkinter as tk

# global vars
WORKSPACE = './workspace'
ICONFILE = './resources/icon.ico'
TITLE = 'S. Tracker'

def load_progress(user_input, filename: str):
	'''
		if filename csv exists load it as df
		else create empty df
	'''
	filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), \
		WORKSPACE, f'{filename}.csv')
	if os.path.exists(filepath):
		df = get_progress(user_input, pd.read_csv(filepath))
	else:
		df = pd.DataFrame(columns=['date', 'hours', 'notes', 'todo', 'literature'])
	return df

def review_todo(todo):
	'''
		parse & update incomplete ToDo list
	'''
	task_completed, todo_completed, updated_tasks =  ' (done)', 'Completed', []
	if type(todo) is str and not todo.startswith(todo_completed):
		tasks = todo.split('\n')
		for task in tasks:
			if not task.endswith(task_completed):
				user_input = messagebox.askyesno('Question', 
									'Are you done with task "{}"?'.format(task[3:]))
				if user_input==1:
					task += task_completed
			updated_tasks.append(task)
		if all(task_completed in updated_task for updated_task in updated_tasks):
		    updated_tasks.insert(0, todo_completed)
		return '\n'.join(updated_tasks)
	return todo

def get_progress(user_input, df):
	'''
		display progress in hours
	'''
	ttl_hours_excl = df.hours.sum()
	ttl_hours_incl = ttl_hours_excl + user_input['hours']
	messagebox.showinfo('Information', 
						'You have worked in total {} hours so far.\n'.format(ttl_hours_excl) + \
						'Updating to {} hours '.format(ttl_hours_incl) + \
		   				'(incl. the inserted {} hours).'.format(user_input['hours']))
	if user_input['review_todo']==1:
		df.todo = df.todo.apply(lambda x: review_todo(x))
	return df

def update_progress(user_input, df):
	'''
		update old data
	'''
	df_new = pd.DataFrame({'date': user_input['date'], 
					'hours': user_input['hours'],
					'notes': user_input['notes'],
					'todo': user_input['todo'],
					'literature': user_input['literature']
				}, index=[0])
	return df.append(df_new)

def save_progress(df, filename: str):
	'''
		save df as csv
	'''
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORKSPACE)
	if not os.path.exists(path):
		os.mkdir(path)
	filepath = os.path.join(path, f'{filename}.csv')
	df.to_csv(filepath, index=False)

def main():

	def disableChildren(parent):
		'''
			disable widgets in parent frame
		'''
		for child in parent.winfo_children():
			wtype = child.winfo_class()
			if wtype not in ('Frame','Label', 'Entry'):
				child.configure(state='disable')
			else:
				disableChildren(child)

	def enableChildren(parent):
		'''
			enable widgets in parent frame
		'''
		for child in parent.winfo_children():
			wtype = child.winfo_class()
			if wtype not in ('Frame','Label', 'Entry'):
				child.configure(state='normal')
			else:
				enableChildren(child)

	def create_project(main_frame):
		'''
			open new window for new project naming
		'''

		def name_project(main_frame, curr_window, project_entry):
			'''
				validate & update current project name
				close current window
				enable main window
			'''
			project_name_parsed = project_entry.get().strip()
			if re.search(r'^[A-z_]+$', project_name_parsed) is None:
				messagebox.showerror('Error', 'Incorrect Project name!\n' + \
					'valid chars: "A"-"Z", "a"-"z", "_"')
				curr_window.lift()
				return
			project_name.set(project_name_parsed)
			curr_window.destroy()
			enableChildren(main_frame)

		def cancel_naming_project(main_frame, curr_window):
			curr_window.destroy()
			enableChildren(main_frame)

		disableChildren(main_frame)
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORKSPACE)
		if not os.path.exists(path):
			os.mkdir(path)
		new_project_window = Toplevel(root) 
		new_project_window.title('Create New Project')
		topframe_tmp = Frame(new_project_window)
		topframe_tmp.pack(padx=10, side=TOP)
		new_project_frame = Label(topframe_tmp, text ='New Project Name:')
		new_project_frame.pack(padx=10, pady = 10, side='left')
		project_name_tmp = StringVar()
		project_entry = Entry(topframe_tmp, width=16, textvariable=project_name_tmp)
		project_entry.pack(padx=10, pady = 10, side='right')
		bottomframe_tmp = Frame(new_project_window)
		bottomframe_tmp.pack(side=BOTTOM)
		buttonframe_new = Frame(bottomframe_tmp)
		buttonframe_new.grid(pady=(10, 20), columnspan=2, sticky=NSEW)
		ok_btn = Button(buttonframe_new,
					width=6,
		            text ='OK',
		            command = lambda: name_project(main_frame, new_project_window, project_name_tmp)) 
		ok_btn.grid(row=0, column=0, padx=10)
		cancel_btn = Button(buttonframe_new,
					width=6,
		            text ='Cancel',
		            command = lambda: cancel_naming_project(main_frame, new_project_window)) 
		cancel_btn.grid(row=0, column=1, padx=10)

	def open_project():
		'''
			get csv filename in workspace as string
		'''
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORKSPACE)
		if not os.path.exists(path):
			os.mkdir(path)
		root.filename = filedialog.askopenfilename(initialdir=path, \
							title='Select Project', filetypes=(('csv files', '*.csv'),))
		project_name.set(os.path.split(root.filename)[-1].split('.')[0])

	def edit_project(frame):
		project_name_parsed = project_name.get()
		# validate project name
		if re.search(r'^[A-z_]+$', project_name_parsed) is None:
			messagebox.showerror('Error', 'Incorrect Project name!')
			return
		frame.destroy()
		root.title('{} - {}'.format(TITLE, project_name_parsed))
		main_frame = Frame(root)
		main_frame.grid(padx=12, pady=(30, 20))
		gui_data = {'todo': {'row': 0, 'entries': [], 'btn_frame': None},
				 	'literature': {'row': 0, 'entries': [], 'btn_frame': None}
		}

		def add_entry(frame, section):
			entry = Entry(frame, width=30)
			entry.grid(row=gui_data[section]['row'] , column=1, pady=8, sticky=W)
			gui_data[section]['btn_frame'].grid(row=gui_data[section]['row']+1, column=1, \
											 columnspan=2, pady=(0, 22), sticky=EW)
			gui_data[section]['entries'].append(entry)
			gui_data[section]['row'] += 1

		def clear_entries(frame, section):
			for entry in gui_data[section]['entries']:
				entry.destroy()
			gui_data[section]['row'] = 0
			gui_data[section]['entries'] = []
			add_entry(frame, section)

		def to_main_menu(frame):
			frame.destroy()
			main_menu()

		def process_input(project):
			hours = hours_entry.get().strip()
			if not hours:
				messagebox.showerror('Error', '"Hours" value cannot be null!')
				return
			else:				
				try:
					hours = int(hours)
					if not 0 <= hours <= 14:
						messagebox.showerror('Error', '"Hours" value can only take\n values between 0 and 14!')
						return
				except:
					messagebox.showerror('Error', '"Hours" value is not a valid number!')
					return
			note = note_entry.get().strip()
			todo_list = '\n'.join([f'{i+1}) {todo}' for i, todo in enumerate( \
								  [todo_entry.get() for todo_entry \
					 			  in gui_data['todo']['entries'] if todo_entry.get().strip()])])
			literature_list = '\n'.join([f'{i+1}) {todo}' for i, todo in enumerate( \
										[literature_entry.get() for literature_entry \
							   			in gui_data['literature']['entries']  if literature_entry.get().strip()])])
			review_todo = review_choice.get()
			user_input = {
					'date': datetime.datetime.today().strftime('%d-%m-%Y'),
					'hours': hours,
					'notes': note,
					'todo': todo_list,
					'literature': literature_list,
					'review_todo' : review_todo
			}
			df = load_progress(user_input, project)
			df = update_progress(user_input, df)
			save_progress(df, project)
			root.quit()

		# Date section
		date_frame = Frame(main_frame)
		date_frame.grid(row=0, columnspan=2, sticky=NSEW)
		date_frame.columnconfigure(0, minsize=100, weight=0)
		date_frame.columnconfigure(1, weight=1)
		date_label = Label(date_frame, text='Date:')
		date_label.grid(row=0, column=0, padx=(0,12), sticky=W)
		date_entry = Entry(date_frame, width=30, \
			textvariable=StringVar(date_frame, datetime.datetime.today().strftime('%a %d, %B, %Y')), state='disabled')
		date_entry.grid(row=0, column=1, pady=8, sticky=W)

		# Hours section
		hours_frame = Frame(main_frame)
		hours_frame.grid(row=1, columnspan=2, sticky=NSEW)
		hours_frame.columnconfigure(0, minsize=100, weight=0)
		hours_frame.columnconfigure(1, weight=1)
		hours_label = Label(hours_frame, text='Hours:')
		hours_label.grid(row=0, column=0, padx=(0,12), sticky=W)
		hours_entry = Entry(hours_frame, width=4)
		hours_entry.grid(row=0, column=1, pady=8, sticky=W)

		# Note section
		note_frame = Frame(main_frame)
		note_frame.grid(row=2, columnspan=2, sticky=NSEW)
		note_frame.columnconfigure(0, minsize=100, weight=0)
		note_frame.columnconfigure(1, weight=1)
		note_label = Label(note_frame, text='Notes:')
		note_label.grid(row=0, column=0, padx=(0,12), sticky=W)
		note_entry = Entry(note_frame, width=30)
		note_entry.grid(row=0, column=1, pady=8, sticky=W)

		# ToDo section
		todo_frame = Frame(main_frame)
		todo_frame.grid(row=3, columnspan=2, sticky=EW)
		todo_frame.columnconfigure(0, minsize=100, weight=0)
		todo_frame.columnconfigure(1, weight=1)
		todo_label = Label(todo_frame, text='ToDo:')
		todo_label.grid(row=0, column=0, padx=(0,12), sticky=W)
		todo_btn_frame = Frame(todo_frame)
		gui_data[list(gui_data.keys())[0]]['btn_frame'] = todo_btn_frame
		todo_btn_frame.grid(row=1, column=1, columnspan=2, pady=(0, 22), sticky=EW)
		todo_btn_frame.columnconfigure(0, minsize=100, weight=1)
		todo_btn_frame.columnconfigure(1, minsize=100, weight=1)
		todo_add_btn = Button(todo_btn_frame, text='Add', padx=12, pady=0, \
							  command=lambda: add_entry(todo_frame, list(gui_data.keys())[0]))
		todo_add_btn.grid(row=0, column=0)
		todo_clear_btn = Button(todo_btn_frame, text='Clear', padx=12, pady=0, \
								command=lambda: clear_entries(todo_frame, list(gui_data.keys())[0]))
		todo_clear_btn.grid(row=0, column=1)
		add_entry(todo_frame, list(gui_data.keys())[0])

		# Literature section
		literature_frame = Frame(main_frame)
		literature_frame.grid(row=4, columnspan=2, sticky=EW)
		literature_frame.columnconfigure(0, minsize=100, weight=0)
		literature_frame.columnconfigure(1, weight=1)
		literature_label = Label(literature_frame, text='Literature:')
		literature_label.grid(row=0, column=0, padx=(0,12), sticky=W)
		literature_btn_frame = Frame(literature_frame)
		gui_data[list(gui_data.keys())[1]]['btn_frame'] = literature_btn_frame
		literature_btn_frame.grid(row=1, column=1, pady=(0, 22), columnspan=2, sticky=EW)
		literature_btn_frame.columnconfigure(0, minsize=100, weight=1)
		literature_btn_frame.columnconfigure(1, minsize=100, weight=1)
		literature_add_btn = Button(literature_btn_frame, text='Add', padx=12, pady=0,
							  command=lambda: add_entry(literature_frame, list(gui_data.keys())[1]))
		literature_add_btn.grid(row=0, column=0)
		literature_clear_btn = Button(literature_btn_frame, text='Clear', padx=12, pady=0,
							  command=lambda: clear_entries(literature_frame, list(gui_data.keys())[1]))
		literature_clear_btn.grid(row=0, column=1)
		add_entry(literature_frame, list(gui_data.keys())[1])

		# Review_choice section
		review_choice_frame = Frame(main_frame)
		review_choice_frame.grid(row=5, columnspan=2, sticky=EW)
		review_choice_frame.columnconfigure(0, minsize=100, weight=0)
		review_choice_frame.columnconfigure(1, weight=1)
		review_choice = IntVar()
		review_checkbox = Checkbutton(review_choice_frame, text='Review ToDo List', variable=review_choice)
		review_checkbox.grid(row=0, column=1, pady=10, sticky=EW)

		# Button section
		button_frame = Frame(main_frame)
		button_frame.grid(row=6, columnspan=2, pady=10, sticky=EW)
		button_frame.columnconfigure(0, weight=1)
		button_frame.columnconfigure(1, weight=1)
		save_btn = Button(button_frame, 
			text='Save', 
			padx=18, 
			pady=6, 
			command=lambda: process_input(project_name_parsed))
		save_btn.grid(row=0, column=0)
		back_btn = Button(button_frame, 
			text='Back', 
			command=lambda: to_main_menu(main_frame), 
			padx=18, 
			pady=6)
		back_btn.grid(row=0, column=1)

		# Info section
		info_frame = Frame(main_frame)
		info_frame.grid(row=7, columnspan=1, pady=(20, 0), sticky=EW)
		info_frame.columnconfigure(0, weight=1)
		info_label = Label(info_frame, 
			text='* You can move around using Tab, Shift+Tab and Space.',
			anchor=CENTER, 
			font=('Arial', 7))
		info_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=EW)

	def main_menu():
		root.title(TITLE)
		main_frame = Frame(root, width=480)
		main_frame.grid(padx=12, pady=(30, 20))

		# Project placeholder
		topframe = Frame(main_frame)
		topframe.pack(padx=10, side=TOP)
		project_label = Label(topframe, text='Project:')
		project_label.pack(padx=10, pady = 10, side='left') 
		project_entry = Entry(topframe, width=20, textvariable=project_name, state='disabled')
		project_entry.pack(padx=10, pady = 10, side='right') 

		# Button Section
		bottomframe = Frame(main_frame, width=480)
		bottomframe.pack( side = BOTTOM , fill=X)
		buttonframe = Frame(bottomframe, width=480)
		buttonframe.grid(padx=12, pady=(30, 10))
		create_project_btn = Button(buttonframe,
					width=16,
		            text ='New Project',  
		            command = lambda: create_project(main_frame)) 
		create_project_btn.grid(row=0, column=0, padx=10)
		open_project_btn = Button(buttonframe,
					width=16,
		            text ='Open Project',
		            command = open_project)
		open_project_btn.grid(row=0, column=1, padx=10)
		ok_project_btn = Button(buttonframe,
					width=6,
		            text ='OK', 
		            command = lambda: edit_project(main_frame))
		ok_project_btn.grid(row=1, pady=20, columnspan=2)

	root = Tk()
	if os.path.exists(ICONFILE):
		root.iconphoto(False, tk.PhotoImage(file=ICONFILE))
	root.resizable(False, False)
	project_name = StringVar()
	main_menu()
	root.mainloop()

if __name__ == '__main__':
	main()
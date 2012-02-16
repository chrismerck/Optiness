#!/usr/bin/env python2

"""
Optiness PyGTK GUI

Darren Alton
"""


import gtk
import common

from sys import maxint
import os

# hack for some deprecated thinger in PyGTK 2.24 that isn't in 2.22
if 'ComboBoxText' not in dir(gtk):  gtk.ComboBoxText = gtk.combo_box_new_text

# quick utility function
def is_iter(x):
	try:
		iterator = iter(x)
	except TypeError:
		return False
	else:
		return True


class OptinessArgEntry(gtk.HBox):
	def __init__(self, modpicker, key, args, validators={}):
		gtk.HBox.__init__(self, spacing=8)

		val = args[key]

		self.modpicker = modpicker
		self.key = key
		self.val = val
		self.lastval = val
		self.default = val

		self.validator = None
		if key in validators:
			self.validator = validators[key]

		self.label = gtk.Label( key )
		self.label.set_size_request(100,-1)
		self.label.set_alignment(1.0, 0.5)

		self.editor = None
		self.type = type(val)
		if self.validator is not None:
			if self.validator == os.path.isfile:
				self.file = gtk.FileChooserButton(key)
				self.file.set_filename(val)
				self.file.connect('file-set', self.file_set_cb)
				self.editor = self.file
			elif is_iter(self.validator):
				self.combo = gtk.ComboBoxText()
				self.combo.connect('changed', self.combo_changed_cb)
				index = 0
				for i in self.validator:
					self.combo.append_text(i)
					if i == val:
						self.combodefault = index
						self.combo.set_active(index)
					index += 1
				self.editor = self.combo

		if self.editor is not None:
			# if we added it from the validator, do nothing here
			# otherwise, add an appropriate widget for the variable type.
			pass
		elif self.type == bool:
			self.check = gtk.ToggleButton(label=str(val))
			self.check.set_active(val)
			self.check.connect('clicked', self.check_clicked_cb)
			self.editor = self.check
		elif self.type == int:
			self.spin = gtk.SpinButton()
			self.spin.set_numeric(True)
			self.spin.set_range(-maxint, maxint)
			self.spin.set_increments(1,10)
			self.spin.set_value(val)
			self.spin.connect('value-changed', self.spin_changed_cb)
			self.editor = self.spin
		else:
			self.entry = gtk.Entry()
			self.entry.set_text( str(val) )
			self.entry.connect('changed', self.entry_changed_cb)
			self.editor = self.entry

		self.reset = gtk.Button('x')
		self.reset.connect('clicked', self.reset_cb)

		self.pack_start(self.label, expand=False)
		self.pack_start(self.editor, expand=True)
		self.pack_start(self.reset, expand=False)

	def update_modpicker(self):
		evaluated = self.val
		try:
			evaluated = eval(self.val, {"__builtins__":None}, {})
		except:
			pass
		if hasattr(self.validator, '__call__') and not self.validator(evaluated):
			# restore last known good value
			tmp = self.default
			self.default = self.lastval
			self.reset_cb(None)
			self.default = tmp
		else:
			self.lastval = self.val
			self.modpicker.args[self.key] = self.val

	def check_clicked_cb(self, widget):
		self.val = widget.get_active()
		widget.set_label(str(self.val))
		self.update_modpicker()

	def spin_changed_cb(self, widget):
		self.val = widget.get_value_as_int()
		self.update_modpicker()

	def combo_changed_cb(self, widget):
		self.val = widget.get_active_text()
		self.update_modpicker()

	def file_set_cb(self, widget):
		self.val = widget.get_filename()
		self.update_modpicker()

	def entry_changed_cb(self, widget):
		self.val = widget.get_text()
		self.update_modpicker()

	def reset_cb(self, widget):
		t = type(self.editor)
		if t == gtk.ToggleButton:
			self.check.set_active(self.default)
		elif t == gtk.SpinButton:
			self.spin.set_value(self.default)
		elif t == gtk.FileChooserButton:
			self.file.set_filename(self.default)
			## NOTE: we don't have to do these last two lines for the other three,
			## because set_active, set_value, and set_text trigger their 'changed' callbacks.
			self.val = self.default
			self.update_modpicker()
		elif t == gtk.ComboBox:
			self.combo.set_active(self.combodefault)
		elif t == gtk.Entry:
			self.entry.set_text( str(self.default) )



class OptinessModulePicker(gtk.VBox):
	def __init__(self, name, listcontents):
		gtk.VBox.__init__(self, spacing=8)

		self.mod = None
		self.args = {}
		self.validators = {}

		self.combo = gtk.ComboBoxText()
		self.combo.connect('changed', self.changed_cb)
		for i in listcontents:
			self.combo.append_text(i)

		self.pack_start(gtk.Label(name), expand=False)
		self.pack_start(self.combo, expand=False)

	def changed_cb(self, widget):
		for i in self.get_children()[2:]:
			self.remove(i)

		self.mod = widget.get_active_text()
		self.args, self.validators = common.util.GetArgs(self.mod)
		for i in self.args:
			self.pack_start( OptinessArgEntry(self, i, self.args, self.validators), expand=False )

		self.show_all()

class OptinessGUI(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		self.set_default_size(500,200)
		self.set_border_width(16)
		self.connect('destroy', lambda widget: gtk.main_quit())

		self.game_picker  = OptinessModulePicker('Game', common.util.ListGames())
		self.brain_picker = OptinessModulePicker('Brain', common.util.ListBrains())

		button = gtk.Button('Start')
		button.connect('clicked', self.clicked_cb)

		self.savefile = gtk.Entry()
		self.savefile.set_text('output/last_run.pickle')
		hbox_output = gtk.HBox(spacing=4)
		hbox_output.pack_start(gtk.Label('output'), expand=False)
		hbox_output.pack_start(self.savefile)

		hbox = gtk.HBox(spacing=16, homogeneous=True)
		hbox.add(self.game_picker)
		hbox.add(self.brain_picker)

		vbox = gtk.VBox(spacing=16)
		vbox.pack_start(hbox, expand=False)
		vbox.pack_start(hbox_output, expand=False)
		vbox.pack_start(button, expand=False)

		self.add(vbox)

	def clicked_cb(self, widget):
		global driver, output

		g, ga = ( self.game_picker.mod, self.game_picker.args )
		b, ba = ( self.brain_picker.mod, self.brain_picker.args )
		output = self.savefile.get_text()

		print """
 game: {}
 args: {}
brain: {}
 args: {}
saving to {}
""".format(g, ga, b, ba, output)

		# it's generally a good idea not to run again without restarting the program,
		# though it's technically possible in some situations.  might explore this later.
		# but for now...
		self.destroy()

		driver = common.Driver(g, b, ga, ba)



if __name__ == "__main__":
	driver = None
	output = 'data/last_run.pickle'
	w = OptinessGUI()
	w.show_all()
	gtk.main()

	if driver is not None:
		driver.Run()
		driver.Save(output)

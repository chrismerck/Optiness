#!/usr/bin/env python2

"""
Optiness PyGTK GUI

Darren Alton
"""

import gtk
import common

# hack for some deprecated thinger in PyGTK 2.24 that isn't in 2.22
if 'ComboBoxText' not in dir(gtk):  gtk.ComboBoxText = gtk.combo_box_new_text

class OptinessArgEntry(gtk.HBox):
	def __init__(self, modpicker, key, val):
		gtk.HBox.__init__(self, spacing=4)

		self.modpicker = modpicker
		self.key = key
		self.val = val
		self.default = val

		self.label = gtk.Label( key )
		self.label.set_justify(gtk.JUSTIFY_LEFT)

		self.entry = gtk.Entry() # TODO: checkbox for bool, range for int?
		self.entry.set_text( str(val) )
		self.entry.set_alignment(1)
		self.entry.connect('changed', self.changed_cb)

		self.reset = gtk.Button('x')
		self.reset.connect('clicked', self.reset_cb)

		self.pack_start(self.label, expand=False)
		self.pack_start(self.entry)
		self.pack_start(self.reset, expand=False)

	def update_modpicker(self):
		self.modpicker.args[self.key] = self.val

	def changed_cb(self, widget):
		self.val = widget.get_text()
		self.update_modpicker()

	def reset_cb(self, widget):
		self.entry.set_text( str(self.default) )
		## NOTE: we don't have to do:
		#self.val = self.default
		#self.update_modpicker()
		## because set_text triggers the changed_cb above.



class OptinessModulePicker(gtk.VBox):
	def __init__(self, name, listcontents):
		gtk.VBox.__init__(self, spacing=8)

		self.mod = None
		self.args = {}

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
		self.args = common.util.GetArgs(self.mod)
		for i in self.args:
			self.pack_start( OptinessArgEntry(self, i, self.args[i]), expand=False )

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

		hbox = gtk.HBox(spacing=16)
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

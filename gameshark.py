#!/usr/bin/python2

'''
initial snapshot
snap+filter: (not) [<][=][>]

endian
word size
'''


import pygame
import gtk, gobject

import py_retro as retro
gtkvid = retro.gtk_video
#pgvid = retro.pygame_video # http://stackoverflow.com/a/341525
pginp = retro.pygame_input

import operator

from sys import argv
libpath, rompath = argv[1:3]

renderers = set()
class OffsetValueTable(gtk.TreeView):
	def __init__(self, es):
		self.es = es
		self.store = gtk.ListStore(int, int, int)
		self.init_store()

		gtk.TreeView.__init__(self, self.store)

		fields = ['offset', 'prev. val', 'cur. val']
		for i in xrange(len(fields)):
			cell = gtk.CellRendererText()
			renderers.add(cell)
			tvcolumn = gtk.TreeViewColumn(fields[i])
			tvcolumn.set_sort_column_id(i)
			tvcolumn.pack_start(cell, True)
			tvcolumn.add_attribute(cell, 'text', i)
			self.append_column(tvcolumn)

		self.set_search_column(0)
		self.set_enable_search(True)
		self.set_reorderable(True)
		self.show()

	def init_store(self):
		memdump = self.es._memory_to_string(retro.MEMORY_SYSTEM_RAM)
		self.store.clear()
		for ofs in xrange(len(memdump)):
			val = ord(memdump[ofs])
			self.store.append([ofs, val, val])

	def update(self):
		memdump = self.es._memory_to_string(retro.MEMORY_SYSTEM_RAM)
		for row in self.store:
			row[2] = ord(memdump[row[0]])
		
	def filter_values(self, comparator = lambda a,b: True):
		def filter_helper(model, path, treeiter, comparator):
			prev, cur = self.get_model().get(treeiter, 1, 2)
			if comparator(cur, prev):
				self.store.set_value(treeiter, 1, cur)
			else:
				self.store.remove(treeiter)

		self.get_model().foreach(filter_helper, comparator)

class ComparatorButtons(gtk.HBox):
	def __init__(self, ovtab):
		gtk.HBox.__init__(self)
		self.ovtab = ovtab
		self.b_lt = gtk.Button('<')
		self.b_eq = gtk.Button('=')
		self.b_gt = gtk.Button('>')
		self.b_lt.connect("clicked", self.on_lt_clicked)
		self.b_eq.connect("clicked", self.on_eq_clicked)
		self.b_gt.connect("clicked", self.on_gt_clicked)
		self.pack_start(self.b_lt)
		self.pack_start(self.b_eq)
		self.pack_start(self.b_gt)
		self.show_all()

	def on_lt_clicked(self, e):  self.ovtab.filter_values(operator.lt)
	def on_eq_clicked(self, e):  self.ovtab.filter_values(operator.eq)
	def on_gt_clicked(self, e):  self.ovtab.filter_values(operator.gt)

def main():
	es = retro.core.EmulatedSystem(libpath)
	es.load_game_normal(path=rompath)

	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	canvas = gtkvid.gtk_DrawingArea(es, False)
	treeview = OffsetValueTable(es)
	scroll = gtk.ScrolledWindow()
	scroll.add_with_viewport(treeview)
	buttonbox = ComparatorButtons(treeview)
	vbox = gtk.VBox()
	vbox.pack_start(scroll)
	vbox.pack_start(buttonbox)
	hbox = gtk.HBox()
	hbox.pack_start(canvas)
	hbox.pack_start(vbox)
	window.add(hbox)
	window.show_all()

	pygame.display.init()
	pginp.set_input_poll_joystick(es)

	fps = es.get_av_info()['fps'] or 60
	clock = pygame.time.Clock()
	def run_frame():
		es.run()
		treeview.update()
		pygame.event.pump()
		clock.tick(fps)
		return True
	timeout_handle = gobject.idle_add(run_frame)

	def shutdown(widget, data=None):
		gobject.source_remove(timeout_handle)
		pygame.quit()
		gtk.main_quit()
	window.connect("destroy", shutdown)

	gtk.main()

if __name__ == "__main__":
	main()


# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import traceback


class ShowKernBubbles(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Kern Bubbles',
			})
		self.generalContextMenus = [{
			'name': Glyphs.localize({
				'en': 'Do something',
				}), 
			'action': self.doSomething_
			}]

	@objc.python_method
	def collectBubbleShapes(self, layer, depth=0):
		# Input layer, transform, and bubble pursuit level.
		# Returns a layer attributes instance.
		try:
			if depth > 5:
				return None

			theMasterLayer = layer.parent.layers[layer.associatedMasterId]
			if theMasterLayer is None:
				return None

			bubbleLayer = layer.parent.layerForName_masterId_('bubble', layer.associatedMasterId)
			if bubbleLayer is None:
				return None
			bubblePath = bubbleLayer.bezierPath.copy()

			for c in theMasterLayer.components:
				componentPath = self.collectBubbleShapes(c.componentLayer, depth + 1)
				if componentPath is None:
					continue
				componentPath.transformUsingAffineTransform_(c.pyobjc_instanceMethods.transform())
				bubblePath.appendPath_(componentPath)

			return bubblePath
		except:
			print('collectBubbleShapes error: ', traceback.format_exc())

	@objc.python_method
	def drawBubble(self, layer):
		try:
			defaultColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25)
			defaultColor.set()

			theBubbles = self.collectBubbleShapes(layer)
			if theBubbles is not None:  # if there are some contents in li
				theBubbles.fill()
		except:
			print('inactiveLayerBackground error: ', traceback.format_exc())

	@objc.python_method
	def inactiveLayerBackground(self, layer):  # drawing for non-main glyphs
		self.drawBubble(layer)

	@objc.python_method
	def background(self, layer):  # drawing for the main glyph
		self.drawBubble(layer)

	def doSomething_(self, sender): # unused
		print('Just did something')

	@objc.python_method
	def conditionalContextMenus(self):

		# Empty list of context menu items
		contextMenus = []

		# Execute only if layers are actually selected
		if Glyphs.font.selectedLayers:
			layer = Glyphs.font.selectedLayers[0]
			
			# Exactly one object is selected and it’s an anchor
			if len(layer.selection) == 1 and type(layer.selection[0]) == GSAnchor:
				pass
				# Add context menu item
				# contextMenus.append({
				# 	'name': Glyphs.localize({
				# 		'en': 'Do something else',
				# 		'de': 'Tu etwas anderes',
				# 		'fr': 'Faire aute chose',
				# 		'es': 'Hacer algo más',
				# 		'pt': 'Faça outra coisa',
				# 		}), 
				# 	'action': self.doSomethingElse_
				# 	})

		# Return list of context menu items
		return contextMenus

	# def doSomethingElse_(self, sender):
	# 	print('Just did something else')

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__

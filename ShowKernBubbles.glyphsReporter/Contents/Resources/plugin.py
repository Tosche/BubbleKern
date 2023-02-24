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
from dataclasses import dataclass, field

@dataclass()
class layerAttributes:
	bubble: GSLayer = None
	transform: tuple = None
	children: list[int] = field(default_factory=list) # another layerAttributes?
	depth: int = 0

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
	def collectBubbleShapes(self, layer, theTransform=(1.0, 0.0, 0.0, 1.0, 0.0, 0.0), depth=0):
		# Input layer, transform, and bubble pursuit level.
		# Returns a layer attributes instance.
		try:
			m = Glyphs.font.selectedFontMaster
			thePath = None
			children = []
			theMasterLayer = layer.parent.layers[m.id]
			if theMasterLayer is not None:
				if theMasterLayer.components:
					for c in theMasterLayer.components:
						children.append(self.collectBubbleShapes(c.componentLayer, c.transform, depth+1))
			for l in layer.parent.layers:
				if l.name == 'bubble' and l.master == m: # path
					thePath = l.completeBezierPath
					break
			currentAttributes = layerAttributes(l, theTransform, children, depth)
			return currentAttributes
		except:
			print('collectBubbleShapes error: ', traceback.format_exc())

	@objc.python_method
	def buildBubble(self, theAttributes, li, inheritedTransforms=[], lastDepth=0):
		# receives bubble attributes, li (imaginary layer) to build a bubble, parent attributes.
		# Adds bubble shape to the li.
		try:
			if theAttributes.children: # if there are components
				for c in theAttributes.children: # c = attribute
					if theAttributes.transform is not None:
						inheritedTransforms.append(theAttributes.transform)
					self.buildBubble(c, li, inheritedTransforms)
			possibleBubble = theAttributes.bubble
			if possibleBubble.name == 'bubble':
				currentDepth = theAttributes.depth
				bubbleCopy = possibleBubble.copy()
				inheritedTransforms.append(theAttributes.transform)
				for t in inheritedTransforms:
					trans = NSAffineTransform()
					trans.setTransformStruct_(t)
					bubbleCopy.transform(trans)
				for s in bubbleCopy.shapes:
					li.shapes.append(s.copy())
				for i in range(currentDepth-lastDepth):
					if inheritedTransforms:
						inheritedTransforms.pop(-1)
				lastDepth = currentDepth
		except:
			print('buildBubble error: ', traceback.format_exc())

	@objc.python_method
	def inactiveLayerBackground(self, layer): # drawing for non-main glyphs
		try:
			defaultColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25)
			defaultColor.set()

			theBubbles = self.collectBubbleShapes(layer)
			li = GSLayer()
			self.buildBubble(theBubbles, li, [])

			if li.bezierPath is not None: # if there're some contents in li
				li.bezierPath.fill()
		except:
			print('inactiveLayerBackground error: ', traceback.format_exc())

	@objc.python_method
	def background(self, layer): # drawing for the main glyph
		try:
			defaultColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25)
			defaultColor.set()

			theBubbles = self.collectBubbleShapes(layer)
			li = GSLayer()
			self.buildBubble(theBubbles, li, [])
			if li.bezierPath is not None: # if there're some contents in li
				li.bezierPath.fill()
		except:
			print('background error: ', traceback.format_exc())
	
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

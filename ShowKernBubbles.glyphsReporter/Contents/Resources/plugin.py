# encoding: utf-8

###########################################################################################################
#
#
# Reporter Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from __future__ import division, print_function, unicode_literals
import objc
from AppKit import NSColor, NSMenuItem
from GlyphsApp import Glyphs, EDIT_MENU
from GlyphsApp.plugins import ReporterPlugin
import traceback


class ShowKernBubbles(ReporterPlugin):

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Kern Bubbles',
		})
		menuMane = Glyphs.localize({
			'en': 'Run Bubbles Kern',
		})
		if Glyphs.buildNumber >= 3320:
			from GlyphsApp.UI import MenuItem
			newMenuItem = MenuItem(menuMane, action=self.runBubblesKern_, target=self)
		else:
			newMenuItem = NSMenuItem(menuMane, self.runBubblesKern_)
		Glyphs.menu[EDIT_MENU].append(newMenuItem)
		self.generalContextMenus = [{
			'name': menuMane,
			'action': self.runBubblesKern_
		}]

	@objc.python_method
	def conditionalContextMenus(self):
		contextMenus = []
		selectedLayers = set(self.controller.selectedLayers)

		if selectedLayers:
			contextMenus.append({
				'name': Glyphs.localize({
					'en': 'Make Bubble Layers',
				}),
				'action': self.runMakeBuble_
			})
			hasBubbles = False
			for selectedLayer in selectedLayers:
				bubbleLayer = selectedLayer.parent.layerForName_masterId_("bubble", selectedLayer.associatedMasterId)
				if bubbleLayer:
					hasBubbles = True
					break
			if hasBubbles:
				contextMenus.append({
					'name': Glyphs.localize({
						'en': 'Delete Bubble Layers',
					}),
					'action': self.runDeleteBubble_
				})
		return contextMenus

	def runBubblesKern_(self, sender):
		from BubbleKern import BubbleKern
		BubbleKern()

	def runMakeBuble_(self, sender):
		from MakeBubbleLayers import MakeBubbleLayers
		MakeBubbleLayers()

	def runDeleteBubble_(self, sender):
		from DeleteBubbleLayers import deleteBubbleLayers
		selectedLayers = self.controller.selectedLayers
		font = self.controller.representedObject()
		deleteBubbleLayers(selectedLayers, font)

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
			if bubbleLayer is None or bubbleLayer.bezierPath is None:
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

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__

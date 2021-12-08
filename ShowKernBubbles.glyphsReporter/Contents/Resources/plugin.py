# encoding: utf-8

###########################################################################################################
#
#
# 	Reporter Plugin
#
# 	Read the docs:
# 	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from GlyphsApp.plugins import *


class ShowKernBubbles(ReporterPlugin):
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({"en": u"Kern Bubbles"})

	@objc.python_method
	def fillBubblePaths(self, givenLayer):  # give it master layer
		try:
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
			# NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.8, 0.8, 1.0, 1.0 ).set()
			for l in givenLayer.parent.layers:
				if l.name == "bubble" and l.associatedFontMaster() == givenLayer.associatedFontMaster():
					if len(l.paths) > 0:
						l.bezierPath.fill()
		except:
			pass

	# 			Glyphs.showMacroWindow()
	# 			print("Show Kern Bubbles Error (fillBubblePaths): %s" % e)

	@objc.python_method
	def fillBubbleCompo(self, givenLayer):  # give it the master layer
		try:
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
			# NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.8, 0.8, 1.0, 1.0 ).set()
			if len(givenLayer.components) > 0:
				for thisCompo in givenLayer.components:
					for thisLayer in thisCompo.component.layers:
						if thisLayer.name == "bubble" and thisLayer.associatedFontMaster() == givenLayer.associatedFontMaster():
							copiedLayer = thisLayer.copy()
							Transform = NSAffineTransform.transform()
							Transform.setTransformStruct_(thisCompo.transform)
							copiedLayer.transform_checkForSelection_(Transform, False)
							for pathCopy in copiedLayer.paths:
								pathCopy.bezierPath.fill()
		except:
			pass

	# 			Glyphs.showMacroWindow()
	# 			print("Show Kern Bubbles Error (fillBubbleCompo): %s" % e)

	@objc.python_method
	def fillBlackCompo(self, givenLayer):
		try:
			if len(givenLayer.components) > 0:
				for thisCompo in givenLayer.components:
					for thisLayer in thisCompo.component.layers:
						copiedLayer = thisLayer.copy()
						Transform = NSAffineTransform.transform()
						Transform.setTransformStruct_(thisCompo.transform)
						copiedLayer.transform_checkForSelection_(Transform, False)
						for pathCopy in copiedLayer.paths:
							pathCopy.bezierPath.fill()
		except:
			pass

	# 			Glyphs.showMacroWindow()
	# 			print("Show Kern Bubbles Error (fillBlackCompo): %s" % e)

	@objc.python_method
	def background(self, layer):
		try:
			self.fillBubblePaths(layer)
			self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
			if layer.name == "bubble":
				NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.5).set()
				parentLayer = layer.parent.layers[layer.associatedMasterId]
				if parentLayer.bezierPath:
					parentLayer.bezierPath.fill()
				if parentLayer.components:
					for c in layer.parent.layers[layer.associatedMasterId].components:
						c.bezierPath.fill()
		except:
			pass

	# 			Glyphs.showMacroWindow()
	# 			print("Show Kern Bubbles Error (background): %s" % e)

	@objc.python_method
	def inactiveLayers(self, layer):
		try:
			if layer.name == "bubble":
				# fill bubble
				if len(layer.paths) > 0:
					NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
					# NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.8, 0.8, 1.0, 1.0 ).set()
					layer.bezierPath.fill()
				self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
				# fill letterform
				NSColor.blackColor().set()
				parentLayer = layer.parent.layers[layer.associatedMasterId]
				if parentLayer.bezierPath:
					parentLayer.bezierPath.fill()
				if parentLayer.components:
					for c in parentLayer.components:
						c.bezierPath.fill()
			else:
				# fill bubble
				self.fillBubblePaths(layer)
				self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
				# fill letterform
				NSColor.blackColor().set()
				if layer.bezierPath:
					layer.bezierPath.fill()
				if layer.components:
					for c in layer.components:
						c.bezierPath.fill()
		except:
			pass


# 			Glyphs.showMacroWindow()
# 			print("Show Kern Bubbles Error (inactiveLayers): %s" % e)

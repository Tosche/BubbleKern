# encoding: utf-8

###########################################################################################################
#
#
#	 Reporter Plugin
#
#	 Read the docs:
#	 https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################


from GlyphsApp.plugins import *
import vanilla, traceback

class ShowKernBubbles(ReporterPlugin):
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({"en": u"Kern Bubbles"})

		defaultColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25)

		# testing with contextual menu stuff
		# viewWidth = 150
		# viewHeight = 80
		# self.sliderMenuView = vanilla.Window((viewWidth, viewHeight))
		# self.sliderMenuView.group = vanilla.Group((0, 0, viewWidth, viewHeight))
		# self.sliderMenuView.group.text = vanilla.TextBox((10, 0, -10, -10), self.menuName)
		# self.sliderMenuView.group.sliderR = vanilla.Slider((10, 18, -10, 23), callback=self.sliderCallback)
		# self.sliderMenuView.group.sliderG = vanilla.Slider((10, 18, -10, 23), callback=self.sliderCallback)
		# self.sliderMenuView.group.sliderB = vanilla.Slider((10, 18, -10, 23), callback=self.sliderCallback)
		# self.sliderMenuView.group.sliderA = vanilla.Slider((10, 18, -10, 23), callback=self.sliderCallback)
		
		# Define the menu
		# self.generalContextMenus = [
		#	 {"view": self.sliderMenuView.group.getNSView()}
		# ]

	# @objc.python_method
	# def sliderCallback(self, sender):
	#	 print('Slider value:', sender.get())

	# @objc.python_method
	# def colorWellCallback(self, sender):
	#	 print('Color value:', sender.get())

	# @objc.python_method
	# def collect_component_layers(self, layer, filter_func):
	#	 try:
	#		 if Glyphs.versionNumber >= 3:
	#			 components = [s for s in layer.shapes if type(s) == GSComponent]
	#		 else:
	#			 components = layer.componbents
	#		 for component in (components or []):
	#			 sub_glyph = component.component
	#			 for sub_layer in sub_glyph.layers:
	#				 if filter_func(sub_layer):
	#					 yield sub_layer, component.transform
	#					 for cl in collect_component_layers(sub_layer, filter_func):
	#						 yield cl
	#	 except Exception, e:
	#		 print(e)

	@objc.python_method
	def fillBubbles(self, l):
		try:
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
			m = l.associatedFontMaster()
			gatheredPaths = []
			for gl in l.parent.layers:
				if gl.name == "bubble" and gl.associatedFontMaster() == m:
					if len(gl.paths) > 0:
						# gatheredPaths.append(gl.bezierPath)
						gl.bezierPath.fill()

		
			# for compoLayerAndTransform in collect_component_layers(l, lambda l: l.layerId == m.id):
			#	 compoLayer = compoLayerAndTransform[0]
			#	 for l in compoLayer.parent.layers:
			#		 if l.name == 'bubble' and l.associatedMasterId == m.id:
			#			 bubbleLayer = l
			#			 compoTransform = compoLayerAndTransform[1]
			#			 break
			#	 print(bubbleLayer, compoTransform)
			#	 bubbleLayerPath = bubbleLayer.bezierPath
			#	 Transform = NSAffineTransform.transform()
			#	 Transform.setTransformStruct_(compoLayerAndTransform[1])
			#	 bubbleLayerPath.transform_checkForSelection_(Transform, False)
						
			#	 for p in bubbleLayerPath:
			#		 p.fill()

		except Exception as e:
			print(e)
			pass

	@objc.python_method
	def fillBubblePaths(self, givenLayer):
		try:
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
			# NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.8, 0.8, 1.0, 1.0 ).set()
			for l in givenLayer.parent.layers:
				if l.name == "bubble" and l.associatedFontMaster() == givenLayer.associatedFontMaster():
					if len(l.paths) > 0:
						l.bezierPath.fill()
		except:
			pass

	@objc.python_method
	def fillBubbleCompo(self, givenLayer):	# give it the master layer
		try:
			NSColor.colorWithCalibratedRed_green_blue_alpha_(0.5, 0.4, 1.0, 0.25).set()
			
			if Glyphs.versionNumber >= 3:	
				components = [s for s in givenLayer.shapes if type(s) == GSComponent]
			else:
				components = givenLayer.components
			if len(components) > 0:
				for c in components:
					for thisLayer in c.component.layers:
						if thisLayer.name == "bubble" and thisLayer.associatedFontMaster() == givenLayer.associatedFontMaster():
							copiedLayer = thisLayer.copy()
							Transform = NSAffineTransform.transform()
							Transform.setTransformStruct_(c.transform)
							copiedLayer.transform_checkForSelection_(Transform, False)
							for pathCopy in copiedLayer.paths:
								pathCopy.bezierPath.fill()
		except:
			print(givenLayer)
			print(traceback.format_exc())
			pass

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

	@objc.python_method
	def background(self, layer):
		try:
			# self.fillBubblePaths(layer)
			# self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
			if layer.name == "bubble":
				NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.5).set()
				parentLayer = layer.parent.layers[layer.associatedMasterId]
				if parentLayer.bezierPath:
					parentLayer.bezierPath.fill()
				if parentLayer.components:
					for c in layer.parent.layers[layer.associatedMasterId].components:
						c.bezierPath.fill()
			else:
				self.fillBubbles(layer)
		except:
			pass

	@objc.python_method
	# def inactiveLayers(self, layer):
	def inactiveLayerBackground(self, layer): # Non-active layers
		try:
			if layer.name == "bubble":
				# fill bubble
				if len(layer.paths) > 0:
					NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.5).set()
					layer.bezierPath.fill()
				self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
				# fill letterform
				# NSColor.blackColor().set()
				# parentLayer = layer.parent.layers[layer.associatedMasterId]
				# if parentLayer.bezierPath:
				#	 parentLayer.bezierPath.fill()
				# if parentLayer.components:
				#	 for c in parentLayer.components:
				#		 c.bezierPath.fill()
			else:
				# fill bubble
				self.fillBubbles(layer)
				# self.fillBubblePaths(layer)
				# self.fillBubbleCompo(layer.parent.layers[layer.associatedMasterId])
				# fill letterform
				# NSColor.blackColor().set()
				# if layer.bezierPath:
				#	 layer.bezierPath.fill()
				# if layer.components:
				#	 for c in layer.components:
				#		 c.bezierPath.fill()
		except:
			pass

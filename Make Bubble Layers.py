#MenuTitle: Make Bubble Layers...
# -*- coding: utf-8 -*-
__doc__="""
Create effect for selected glyphs.
"""

import vanilla
import GlyphsApp
import math

class MakeBubbleLayers( object ):
	def __init__( self ):
		# Window 'self.w':
		edY = 22
		txX = 116
		txY  = 17
		spX = 14
		spY = 12
		btnX = 60
		btnY = 20
		windowWidth  = 260
		windowHeight = 300
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Make Bubble Layers", # window title
			autosaveName = "com.Tosche.MakeBubbleLayers.mainwindow" # stores last window position and size
		)
		# Offset values:
		self.w.textH = vanilla.TextBox( (spX, spY, txX, txY), "Horizontal Offset:" )
		self.w.textV = vanilla.TextBox( (spX, spY*2+txY, txX, txY), "Vertical Offset:" )
		self.w.editH = vanilla.EditText( (-spX-80, spY, -spX, edY), "60")
		self.w.editV = vanilla.EditText( (-spX-80, spY*2+txY, -spX, edY), "60")
		self.w.line1 = vanilla.HorizontalLine((0, spY*3+txY*2+5, -0, 1))
		# Sidebearing modification:
		self.w.adhereToSB = vanilla.CheckBox((spX, spY*4+txY*2, -spX, edY), "Adhere to Sidebearigs", callback=self.checkBoxCallback, value=True)
		self.w.excess = vanilla.TextBox( (spX+16, spY*5+txY*3-7, -spX, txY), "Exceeding outlines are:" )
		self.w.excessRadio = vanilla.RadioGroup((spX+16, spY*6+txY*4-14, 160, edY), ["Nudged", "Trimmed"], isVertical = False,)
		self.w.line2 = vanilla.HorizontalLine((0, spY*6+txY*5-4, -0, 1))
		# Overwrite Behaviour:
		self.w.textOverwrite = vanilla.TextBox( (spX, spY*7+txY*5-8, -spX, txY), "Overwrite existing?" )
		self.w.overwriteRadio = vanilla.RadioGroup((spX, spY*8+txY*6-11, -spX, edY), ["Never", "If Empty", "Always"], isVertical = False,)
		self.w.line3 = vanilla.HorizontalLine((0, spY*9+txY*7-8, -0, 1))
		# Master preference
		self.w.masterRadio = vanilla.RadioGroup((spX, spY*9+txY*7, 0, edY), ["Current Master", "All Masters"], isVertical = False,)
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Go!", sizeStyle='regular', callback=self.MakeBubbleLayersMain )
		self.w.setDefaultButton( self.w.runButton )
		# Load Settings:
		if not self.LoadPreferences():
			self.w.excessRadio.set(0)
			self.w.overwriteRadio.set(1)
			self.w.masterRadio.set(1)
			print "Note: 'Make Bubble Layers' could not load preferences. Will resort to defaults"
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.editH"] = self.w.editH.get()
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.editV"] = self.w.editV.get()
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.adhereToSB"] = self.w.adhereToSB.get()
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.excessRadio"] = self.w.excessRadio.get()
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.overwriteRadio"] = self.w.overwriteRadio.get()
			Glyphs.defaults["com.Tosche.MakeBubbleLayers.masterRadio"] = self.w.masterRadio.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			self.w.editH.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.editH"] )
			self.w.editV.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.editV"] )
			self.w.adhereToSB.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.adhereToSB"] )
			self.w.excessRadio.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.excessRadio"] )
			self.w.overwriteRadio.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.overwriteRadio"] )
			self.w.masterRadio.set( Glyphs.defaults["com.Tosche.MakeBubbleLayers.masterRadio"] )
		except:
			return False
			
		return True

	def checkBoxCallback(self,sender):
		try:
			if sender.get():
				self.w.excessRadio.enable(True)
			else:
				self.w.excessRadio.enable(False)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "Make Bubble Layers Error (checkBoxCallback): %s" % e

	def offsetPath(self, Layer, h, v):
		try:
			GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")
			offsetCurveFilter = NSClassFromString("GlyphsFilterOffsetCurve")
			if GLYPHSAPPVERSION.startswith("1."):
				offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_position_error_shadow_( Layer, h, v, False, 0.5, None, None )
			else:
				offsetCurveFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_error_shadow_( Layer, h, v, False, False, 0.5, None,None)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "Make Bubble Layers Error (offsetPath): %s" % e

	def nudgeCurve(self, oncurveMv, offcurve1, offcurve2, oncurveSt, offsetX):
		try:
			distanceX = oncurveMv.x - oncurveSt.x
			distanceX1 = oncurveMv.x - offcurve1.x
			distanceX2 = offcurve2.x - oncurveSt.x
			if distanceX != 0:
				valueX1 = distanceX1/distanceX
				valueX2 = distanceX2/distanceX
			else:
				valueX1 = 0
				valueX2 = 0
			if distanceX1 != 0:
				offcurve1.x += (1-valueX1)*offsetX
			else:
				offcurve1.x += offsetX
			if distanceX2 != 0:
				offcurve2.x += (valueX2)*offsetX
		except Exception, e:
			Glyphs.showMacroWindow()
			print "Make Bubble Layers Error (nudgeCurve): %s" % e
	
	def fitToSidebearing(self, givenLayer, givenMaster):
		try:
			nudgeExcess = True if self.w.excessRadio.get() == 0 else False
			boundL = givenLayer.bounds.origin.x
			boundR = boundL + givenLayer.bounds.size.width
			for thisPath in givenLayer.paths:
				numOfNodes = len(thisPath.nodes)
				for i in range(numOfNodes):
					node = thisPath.nodes[i]
					interesting = False
					if node.type == 1 or node.type == 35:
						if node.x < 0 and nudgeExcess:
							interesting = True
							offsetX = -node.x
						elif (0 < node.x) and (node.x == boundL):
							interesting = True
							offsetX = -node.x
						elif (node.x == boundR) and (node.x < givenLayer.width):
							interesting = True
							offsetX = givenLayer.width - node.x
						elif givenLayer.width < node.x and nudgeExcess:
							interesting = True
							offsetX = givenLayer.width - node.x
						if interesting:
							nodeBefore = thisPath.nodes[i-1]
							if nodeBefore.type == 65:
								if thisPath.nodes[i-2].type == 65: # if two previous nodes are 65 (offcurve)
									oncurveMv = node
									offcurve1 = nodeBefore
									offcurve2 = thisPath.nodes[i-2]
									oncurveSt = thisPath.nodes[i-3]
									self.nudgeCurve(oncurveMv, offcurve1, offcurve2, oncurveSt, offsetX) # only moves offcurve
							nodeAfter = thisPath.nodes[i+1]
							if nodeAfter.type == 65:
								if thisPath.nodes[i+2].type ==65: # if two next nodes are 65 (offcurve)
									oncurveMv = node
									offcurve1 = nodeAfter
									offcurve2 = thisPath.nodes[i+2]
									oncurveSt = thisPath.nodes[i+3]
									self.nudgeCurve(oncurveMv, offcurve1, offcurve2, oncurveSt, offsetX) # only moves offcurve
							node.x += offsetX # on curve node moves here
			if nudgeExcess == False: # if Trim Option is on
				wi = givenLayer.width
				slant = givenMaster.italicAngle
				slantOrigin = givenMaster.xHeight / 2
				if slant == 0:
					(difBottom, difTop) = 0, 0
				else:
					difTop = math.tan(math.radians(slant)) * (3000-slantOrigin)
					difBottom = -( math.tan(math.radians(slant)) * (slantOrigin+3000) )
				eraserRectNodes = [
					[[-3000+difBottom,-3000],[0+difBottom,-3000],[0+difTop,3000],[-3000+difTop,3000]],
					[[wi+difBottom,-3000],[wi+3000+difBottom,-3000],[wi+3000+difTop,3000],[wi+difTop,3000]]
				]
				Erasers = NSMutableArray.alloc().init()
				for eraser in eraserRectNodes:
					eraserRect = GSPath()
					for node in eraser:
						newNode = GSNode()
						newNode.type = GSLINE
						newNode.position = ( node[0], node[1] )
						eraserRect.nodes.append( newNode )
					eraserRect.closed = True
					Erasers.append(eraserRect)
				PathOperator = GSPathOperator.alloc().init()
				Paths = givenLayer.pyobjc_instanceMethods.paths()
				PathOperator.subtractPaths_from_error_(Erasers, Paths, None)
				givenLayer.paths = Paths
		except Exception, e:
			Glyphs.showMacroWindow()
			print "Make Bubble Layers Error (fitToSidebearing): %s" % e
	
	def MakeBubbleLayersMain( self, sender ):
		try:
			font = Glyphs.font # frontmost font
			fontMaster = font.selectedFontMaster # active master
			selectedLayers = font.selectedLayers # active layers of selected glyphs
			GLYPHSAPPVERSION = NSBundle.bundleForClass_(GSMenu).infoDictionary().objectForKey_("CFBundleShortVersionString")

			font.disableUpdateInterface() # suppresses UI updates in Font View

			try:
				offsetH = int(self.w.editH.get())
				offsetV = int(self.w.editV.get())
			except:
				Glyphs.displayDialog_withTitle_("You typed something other than numbers in the text field.", "Invalid Input")

			if self.w.masterRadio.get() == 0:
				masters = [font.selectedFontMaster]
			else:
				masters = font.masters

			for gLayer in selectedLayers:
				glyph = gLayer.parent
				glyph.beginUndo() # begin undo grouping			

				if self.w.overwriteRadio.get() == 0: # never overwrite
					# bubbleList is a list of masters that have bubble layer
					bubbleList = [ layer.associatedFontMaster() for layer in glyph.layers if layer.name=='bubble' ]
				elif self.w.overwriteRadio.get() == 1: # make new only if empty
					bubbleList = [ layer.associatedFontMaster() for layer in glyph.layers if layer.name=='bubble' and len(layer.paths) > 0 ]
					bubblesToBeDeleted = [ layer for layer in glyph.layers if layer.name=='bubble' and len(layer.paths)==0 ]
				else: #Always delete and make new
					bubbleList = []
					bubblesToBeDeleted = [ layer for layer in glyph.layers if layer.name=='bubble' ]
				if 'bubblesToBeDeleted' in locals():
					for emptyBubble in bubblesToBeDeleted:
						glyph.removeLayerForKey_(emptyBubble.layerId)

				for master in masters:
					if not master in bubbleList: # if master is not mentioned in bubbleList = doesn't have bubble
						newBubbleLayer = GSLayer()
						newBubbleLayer.name = "bubble"
						newBubbleLayer.width = glyph.layers[master.id].width
						newBubbleLayer.associatedMasterId = master.id
						for pathToCopy in glyph.layers[master.id].paths:
							newBubbleLayer.addPath_( pathToCopy.copy() )
						self.offsetPath(newBubbleLayer, offsetH, offsetV) # SHOULD NOT BE EXECUTED IF SIDEBEARING OPTION IS OFF
						newBubbleLayer.removeOverlap()
						for path in newBubbleLayer.paths: # remove negative path because you don't need it
							if path.direction == 1:
								path.reverse()
						newBubbleLayer.removeOverlap() # remove overlap again to eliminate all negative path
						if self.w.adhereToSB.get():
							self.fitToSidebearing(newBubbleLayer, master)
						glyph.layers.append(newBubbleLayer)
				glyph.endUndo()   # end undo grouping		
			font.enableUpdateInterface() # re-enables UI updates in Font View
	
			if not self.SavePreferences( self ):
				print "Note: 'Make Bubble Layers' could not write preferences."
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Make Bubble Layers Error (MakeBubbleLayersMain): %s" % e

MakeBubbleLayers()
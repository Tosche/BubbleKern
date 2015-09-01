#!/usr/bin/env python
# encoding: utf-8

import objc
from Foundation import *
from AppKit import *
import sys, os, re

MainBundle = NSBundle.mainBundle()
path = MainBundle.bundlePath() + "/Contents/Scripts"
if not path in sys.path:
	sys.path.append( path )

import GlyphsApp

GlyphsReporterProtocol = objc.protocolNamed( "GlyphsReporter" )

class ShowKernBubbles ( NSObject, GlyphsReporterProtocol ):
	
	#def init( self ):
	#	"""
	#	Unless you know what you are doing, leave this at "return self".
	#	"""
	#	return self
		
	def title( self ):
		"""
		This is the name as it appears in the menu in combination with 'Show'.
		E.g. 'return "Nodes"' will make the menu item read "Show Nodes".
		"""
		return "Kern Bubbles"
		
	def interfaceVersion( self ):
		"""
		Must return 1.
		"""
		try:
			return 1
		except Exception as e:
			self.logToConsole( "interfaceVersion: %s" % str(e) )
		
	def logToConsole( self, message ):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole( "bla bla" ) for debugging.
		"""
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )
		NSLog( myLog )
		
	def keyEquivalent( self ):
		"""
		The key for the keyboard shortcut. Set modifier keys in modifierMask() further below.
		Pretty tricky to find a shortcut that is not taken yet, so be careful.
		If you are not sure, use 'return None'. Users can set their own shortcuts in System Prefs.
		"""
		try:
			return None
		except Exception as e:
			self.logToConsole( "keyEquivalent: %s" % str(e) )
		
	def modifierMask( self ):
		"""
		Use any combination of these to determine the modifier keys for your default shortcut:
			return NSShiftKeyMask | NSControlKeyMask | NSCommandKeyMask | NSAlternateKeyMask
		Or:
			return 0
		... if you do not want to set a shortcut.
		"""
		try:
			return 0
		except Exception as e:
			self.logToConsole( "modifierMask: %s" % str(e) )
		
	def drawForegroundForLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed IN FRONT OF the paths.
		"""
		try:
			pass
		except Exception as e:
			self.logToConsole( "drawForegroundForLayer_: %s" % str(e) )

	def drawLayer_(self, Layer):
		try:
			masters = Layer.parent.parent.masters
			theMaster = Layer.parent.parent.selectedFontMaster
			frontToBeFilled = False
			NSColor.colorWithCalibratedRed_green_blue_alpha_( 0.5, 0.4, 1.0, 0.25 ).set()
			layerToBeFilled = GSLayer()
			if Layer.name == "bubble" and Layer.associatedFontMaster() in masters: #if you are in a bubble layer
				try:
					for thisPath in Layer.paths:
						layerToBeFilled.addPath_(thisPath.copy())
					frontToBeFilled = True
				except:
					pass
			else: #if you are in a master layer and want to pick a bubbleLayer
				for thisLayer in Layer.parent.layers:
					if thisLayer.name == "bubble" and thisLayer.associatedFontMaster() == Layer.associatedFontMaster():
						try:
							for thisPath in thisLayer.paths:
								layerToBeFilled.addPath_(thisPath.copy())
						except:
							pass

			theComponents = Layer.components
			numberOfComponents = len( theComponents )
			if numberOfComponents != 0:
				for thisCompo in Layer.components:
					for thisLayer in thisCompo.component.layers:
						if thisLayer.name == "bubble" and thisLayer.associatedFontMaster() == Layer.associatedFontMaster():
							try:
								copiedLayer = thisLayer.copy()
								Transform = NSAffineTransform.transform()
								Transform.setTransformStruct_(thisCompo.transform)
								copiedLayer.transform_checkForSelection_(Transform, False)
								for pathCopy in copiedLayer.paths:
									layerToBeFilled.addPath_(pathCopy)
							except Exception, e:
								print e
								pass
			if layerToBeFilled: # is going to fill the bubble here! How exciting!
				if len( layerToBeFilled.paths ) > 0:
					try:
						layerToBeFilled.bezierPath().fill()
					except:
						pass # layerToBeFilled.bezierPath() is None
					try:
						layerToBeFilled.openBezierPath().fill()
					except:
						pass # layerToBeFilled.openBezierPath() is None
			if frontToBeFilled: # fill the base letter if you're in bubble layer
				masterLayer = Layer.parent.layerForName_(Layer.associatedFontMaster().name)
				NSColor.blackColor().set()
				if len( masterLayer.paths ) > 0:
					try:
						masterLayer.bezierPath().fill()
					except:
						pass # layerToBeFilled.bezierPath() is None
					try:
						masterLayer.openBezierPath().fill()
					except:
						pass # layerToBeFilled.openBezierPath() is None

		except Exception as e:
			self.logToConsole( "drawLayer_: %s" % str(e) )

	def drawBackgroundForLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed BEHIND the paths.
		"""
		try:
			self.drawLayer_(Layer)

		except Exception as e:
			self.logToConsole( "drawBackgroundForLayer_: %s" % str(e) )
			
	def drawBackgroundForInactiveLayer_( self, Layer ):
		"""
		Whatever you draw here will be displayed behind the paths, but for inactive masters.
		"""
		try:
			self.drawLayer_(Layer)
		except Exception as e:
			self.logToConsole( "drawBackgroundForInactiveLayer_: %s" % str(e) )
			
	def setController_( self, Controller ):
		"""
		Use self.controller as object for the current view controller.
		"""
		try:
			self.controller = Controller
		except Exception as e:
			self.logToConsole( "setController_: %s" % str(e) )

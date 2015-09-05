#MenuTitle: BubbleKern...
# -*- coding: utf-8 -*-
__doc__="""
Kerns glyphs automatically, given that the glyphs have bubble layer (components automatically inherit bubble layers).
Bubble layer should be named as "bubble".

This version supports pair list as flat text, and also has Pair List Builder like the one in Metrics Machine.
"""

#ToDo:
#	Drag & Drop
#	Disable duplicating chekcbox when group 1 & 2 are the same
#	Make Plus and Minus button fancier

import vanilla
import GlyphsApp
import os # for copying text to clipboard and loading text file
import re # for validating flat text
from robofab.interface.all.dialogs import AskString, AskYesNoCancel # for getting Save As name and Cancel
from vanilla.dialogs import askYesNo
from math import ceil # for rounding up kerning value
from AppKit import NSDragOperationMove

prevX = 180
edY = 22
txY  = 17
spX = 10
spY = 10
btnX = 160
btnY = 22
tab0options = [
	"Options", "  New Set", "  Save Set in Favourites",
	"  Save Set in Favourites As...", "  Delete Set from Favourites...","  Copy Set as Flat Text", "Favourites"]
Menlo12 = NSFont.fontWithName_size_("Menlo", 12)

toolOrderDragType = "toolOrderDragType"

# Load tab0 pairs
if Glyphs.defaults["com.Tosche.BubbleKern.favDic"] != None:
	favDic = Glyphs.defaults["com.Tosche.BubbleKern.favDic"]
	favDic = NSMutableDictionary.alloc().initWithDictionary_copyItems_(favDic, True)
else: # Fallback to default favourite dictionary
	favDic = {"Sample": [
		[u"A B C D E F G H I J K L M N O P Q R S T U V W X Y Z", u"A B C D E F G H I J K L M N O P Q R S T U V W X Y Z", False],
		[u"a b c d e f g h i j k l m n o p q r s t u v w x y z", u"a b c d e f g h i j k l m n o p q r s t u v w x y z", False],
		[u"A B C D E F G H I J K L M N O P Q R S T U V W X Y Z", u"a b c d e f g h i j k l m n o p q r s t u v w x y z", False], 
		[u"a b c d e f g h i j k l m n o p q r s t u v w x y z", u"exclam question", True],
	] }

def favNameList(dic):
	return sorted([i for i,value in dic.iteritems()], key=lambda s: s.lower())

class BubbleKern( object ):
	def __init__( self ):
		windowWidth  = 600
		windowHeight = 260
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"BubbleKern", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			autosaveName = "com.Tosche.BubbleKern.mainwindow" # stores last window position and size
		)

		self.w.tabs = vanilla.Tabs((spX, spY, -spX, -spY*2-btnY), ["Pair List Builder", "Flat Text"])
		tab0 = self.w.tabs[0]
		tab0.options = vanilla.PopUpButton((spX, 0, 200, btnY), tab0options, callback=self.optionTasks )
		tab0.options._nsObject.menu().setAutoenablesItems_(False)
		emptyPermutation = [{" ":"", "Left":"", "Right":"", "Add Flipped":"", "Pair Count":"0" }]
		GroupColumnWidth = int((self.w.getPosSize()[2]-180-spX*5-prevX)/2+1)
		tab0.permList = vanilla.List((spX, spY+btnY, -prevX-spX*2, -spY*3), emptyPermutation,
			columnDescriptions=[
				{"title":" ", "width":20},
				{"title":"Left", "width":GroupColumnWidth},
				{"title":"Right", "width":GroupColumnWidth},
				{"title":"Add Flipped","cell":vanilla.CheckBoxListCell(), "width":70},
				{"title":"Pair Count", "width":90}
			],
		#	dragSettings = dict( type=NSString, callback=self.dragCallback ), # WHY DOES THIS THING NOT WORK?
			selfDropSettings=dict(type=toolOrderDragType, operation=NSDragOperationMove, callback=self.dropListSelfCallback),
			allowsMultipleSelection = False,
			selectionCallback = self.permListSelected,
			doubleClickCallback= self.permListDoubleClick,
		)

		tableView = tab0.permList._tableView
		tableView.setAllowsColumnReordering_(False)
		tableView.unbind_("sortDescriptors") # Disables sorting by clicking the title bar
		tableView.tableColumns()[0].setResizingMask_(0)
		tableView.tableColumns()[1].setResizingMask_(1)
		tableView.tableColumns()[2].setResizingMask_(1)
		tableView.tableColumns()[3].setResizingMask_(0)
		tableView.tableColumns()[4].setResizingMask_(0)
		tableView.setColumnAutoresizingStyle_(1)
# setResizingMask_() 0=Fixed, 1=Auto-Resizable (Not user-resizable). There may be more options?
# setColumnAutoresizingStyle accepts value from 0 to 5.
# For detail,see: http://api.monobjc.net/html/T_Monobjc_AppKit_NSTableViewColumnAutoresizingStyle.htm

		tab0.sectionPreview = vanilla.TextBox((-prevX-spX, spY+btnY-2, -spX, txY), "Section Preview", sizeStyle = "small")
		tab0.preview = vanilla.TextEditor((-prevX-spX, spY+btnY+txY, -spX, -spY*3), "", readOnly=True)
		tab0.preview._textView.setFont_( Menlo12 )
		tab0.total = vanilla.TextBox((-prevX-spX*2-75, -spY-txY, 100, txY), "", sizeStyle = "small")
		# Add & Delete Buttons:
		tab0.add = vanilla.SquareButton((spX, -spY*3-1, 30, 20), "+", sizeStyle = 'regular', callback=self.addButton)
		tab0.delete = vanilla.SquareButton((spX+29, -spY*3-1, 30, 20), u"–", sizeStyle = 'regular', callback=self.delButton)

		tab1 = self.w.tabs[1]
		tab1.loadButton = vanilla.Button((spX, 0, 160, btnY), "Load a Text File", callback=self.loadFile)

		tab1.flatPairs = vanilla.TextEditor((spX, spY+btnY, -spX, -spY*3), "", callback=self.refreshPairNum)
		tab1.flatPairs._textView.setFont_( Menlo12 )
		tab1.pairNum = vanilla.TextBox((10, -spY-txY, -10, txY), "", sizeStyle = "small")

		self.w.allButton = vanilla.Button((-spX*2-btnX*2-60, -btnY-spY, btnX, btnY), "Kern All Pairs", sizeStyle='regular', callback=self.BubbleKernMain)
		self.w.selButton = vanilla.Button((-spX-btnX-60, -btnY-spY, btnX+60, btnY), "Kern Pairs with Selected Glyphs", sizeStyle='regular', callback=self.BubbleKernMain )

		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'BubbleKern' could not load preferences. Will resort to defaults"

		self.refreshTotal()
		self.refreshSectionPreview(0)
		self.refreshPairNum(self.w)
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	def SavePreferences( self, saveName, deleteBool ):
		try:
			if deleteBool == False: # you need to save
				permList = []
				for i in range(len(self.w.tabs[0].permList)):
					perm = []
					perm.append(self.w.tabs[0].permList[i]["Left"])
					perm.append(self.w.tabs[0].permList[i]["Right"])
					perm.append(self.w.tabs[0].permList[i]["Add Flipped"])
					permList.append(perm)
				favDic[saveName] = permList
			elif deleteBool == True:
				del favDic[saveName]
#			favDicToSave = NSMutableDictionary.dictionaryWithDictionary_(favDic)
			Glyphs.defaults["com.Tosche.BubbleKern.favDic"] = favDic
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (SavePreferences): %s" % e

	def favDicToList(self, favName): # set List view using favDic and name key
		try:
			self.w.tabs[0].permList.set([{" ":"1", "Left":"", "Right":"", "Add Flipped":False, "Pair Count":0}])
			favourites = favDic[favName] # list of favourites
			columnItemsToShow = []

			for i in range(len(favourites)): #fav is a list of columns containing Left, Right, flipped
				fav = favourites[i]
				newDic = {}
				newDic[" "] = str(i+1)
				( newDic["Left"], newDic["Right"], newDic["Add Flipped"] ) = fav[0], fav[1], fav[2]
				newDic["Pair Count"] = len(fav[0].split())*len(fav[1].split())*2 if fav[2] else len(fav[0].split())*len(fav[1].split())
				if favourites.index(fav) == 0:
					self.w.tabs[0].permList[i] = newDic
				else:
					self.w.tabs[0].permList.append(newDic)

#			for fav in favourites: #fav is a list of columns containing Left, Right, flipped
#				newDic = {}
#				newDic[" "] = str(favourites.index(fav)+1)
#				( newDic["Left"], newDic["Right"], newDic["Add Flipped"] ) = fav[0], fav[1], fav[2]
#				newDic["Pair Count"] = len(fav[0].split())*len(fav[1].split())*2 if fav[2] else len(fav[0].split())*len(fav[1].split())
#				if favourites.index(fav) == 0:
#					self.w.tabs[0].permList[favourites.index(fav)] = newDic
#				else:
#					self.w.tabs[0].permList.append(newDic)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (favDicToList): %s" % e

	def favNameList(self): # Returns list of favDic keys so you can use it in options
		return sorted([i for i,value in favDic.iteritems()], key=lambda s: s.lower())

	def LoadPreferences( self ):
		try:
			# Load tab0 pairs
			# favDic already loaded
			favNameList = self.favNameList()
			self.refreshOptions()
			self.w.tabs[0].options.set(8)

			self.favDicToList(favNameList[0])

			# Load tab1 text
			if Glyphs.defaults["com.Tosche.BubbleKern.flatPairs"] != None:
				flatPairs = Glyphs.defaults["com.Tosche.BubbleKern.flatPairs"]
			else: # Fall Back to Default Text
				flatPairs = "Welcome!\n\nBelow is a sample of flat pairs. Each line should be a pair, two glyph names separated by a space.\n\nA T\nT A\nT a\nT adieresis\n\nWhen you actually kern, there should be no junk lines such as this welcome text."
			self.w.tabs[1].flatPairs.set(flatPairs)
			return True

		except Exception, e:
			print "BubbleKern Error (LoadPreferences): %s" % e
			return False

	def refreshOptions( self ): # refresh option items
		try:
			favNameList = self.favNameList()
			self.w.tabs[0].options.setItems(tab0options+favNameList)
			menu = self.w.tabs[0].options._nsObject.menu()
			menu.itemAtIndex_(0).setEnabled_(False)
			divider0 = NSMenuItem.separatorItem()
			menu.insertItem_atIndex_(divider0, 6)
			menu.itemAtIndex_(7).setEnabled_(False)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (refreshOptions): %s" % e

	def optionTasks( self, sender ): # variety of stuff tabs[0].option has to do
		try:
			favNameList = self.favNameList()
			index = sender.get()
			global lastIndex
			emptyList = [{" ":"1", "Left":"", "Right":"", "Add Flipped":False, "Pair Count":0}]
			if not "lastIndex" in globals(): # only the case with first access
				lastIndex = 8
			if index == 1: # New Set
				lastIndex = 1
				self.w.tabs[0].permList.set(emptyList)
				self.refreshSectionPreview(0)
				self.w.tabs[0].options.set(0)
			elif index == 2: # Save Set in Favourites
				if lastIndex == 1:
					setName = AskString("Save As:", title="Save Pair List")
				else:
					setName = favNameList[lastIndex-8]
				self.SavePreferences(setName, False) # deleteBool = False
				self.refreshOptions()
				favNameList = self.favNameList()
				self.w.tabs[0].options.set(favNameList.index(setName)+8)
			elif index == 3: # Save Set in Favourites As...
				newName = AskString("Save As:", title="Save Pair List")
				if newName == "": #exists already or empty, or None:
					self.w.tabs[0].options.set(lastIndex)
				elif newName in favDic:
					Glyphs.displayDialog_("A set with the same name already exists.")
					self.w.tabs[0].options.set(lastIndex)
				else:
					self.SavePreferences(newName, False) # deleteBool = False
					self.refreshOptions()
					favNameList = self.favNameList()
					self.w.tabs[0].options.set(favNameList.index(newName)+8)
			elif index == 4: # Delete Set from Favourites...
				lastName = favNameList[lastIndex-8]
				if len(favNameList)==1:
					Glyphs.displayDialog_("Actually, you can't empty the Favourites list.\nSorry for my incompetent coding.")
				else:
					if askYesNo(messageText='Are you sure you want to delete "%s"?' % lastName, alertStyle=1,) == 1:
						self.SavePreferences(lastName, True) # deleteBool = True
						self.refreshOptions()
						self.w.tabs[0].permList.set(emptyList)
						self.w.tabs[0].options.set(0)
					else:
						self.w.tabs[0].options.set(lastIndex)
			elif index == 5: # Copy Set As Flat Text
				self.BubbleKernMain(sender)
				self.w.tabs[0].options.set(lastIndex)
			elif index >= 8: # if one of Favourites
				lastIndex = index
				self.favDicToList(favNameList[index-8])
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (optionTasks): %s" % e

	def refreshSectionPreview( self, i ): # i = row index
		try:
			isFlipped = self.w.tabs[0].permList[i]["Add Flipped"]
			selectedDic = self.w.tabs[0].permList[i]
			mixA = selectedDic["Left"].split()
			mixB = selectedDic["Right"].split()
			preview = ["%s %s" % (charA, charB) for charA in mixA for charB in mixB ]
			if isFlipped == True:
				preview.extend(["%s %s" % (charB, charA) for charA in mixA for charB in mixB ])
			self.w.tabs[0].preview.set('\n'.join(preview))
		except Exception, e:
			print "BubbleKern Error (refreshSectionPreview): %s" % e

	def permListSelected(self, sender): # Used to refresh Pair Count and Section Preview.
		try:
			for i in range(len(self.w.tabs[0].permList)):
				A = self.w.tabs[0].permList[i]["Left"].split()
				B = self.w.tabs[0].permList[i]["Right"].split()
				# Force-disable duplicates.
				if A == B: # I want to setEnabled_(False) to the forbidden cell!
					self.w.tabs[0].permList[i]["Add Flipped"] = False
					#self.w.tabs[0].permList._tableView.cellAtColumn_row_(3, i).setEnabled_(False)
					#self.w.tabs[0].permList._tableView.tableColumns()[3].tableRows()[i].setEnabled_(False)
				elif A != B:
					#self.w.tabs[0].permList._tableView.tableColumns()[3].??????.setEnabled_(True)
					pass

				# Refresh all pair numbers because clicking the chekbox won't handle its row.
				isFlipped = self.w.tabs[0].permList[i]["Add Flipped"]
				if isFlipped == False:
					self.w.tabs[0].permList[i]["Pair Count"] = len(A)*len(B)
				else:
					self.w.tabs[0].permList[i]["Pair Count"] = len(A)*len(B)*2
				self.refreshTotal()
			try: # Making section preview
				self.refreshSectionPreview(sender.getSelection()[0])
			except IndexError:
				pass
		except Exception, e:
			print "BubbleKern Error (permListSelected): %s" % e

	def permListDoubleClick(self, sender): # Make a new sheet appear
		try:
			groupText1 = sender[sender.getSelection()[0]]["Left"]
			groupText2 = sender[sender.getSelection()[0]]["Right"]
			sWidth = 600
			self.s = vanilla.Sheet((sWidth, 300), self.w)
			edWidth = int((sWidth-spX*3)/2)
			self.s.text1 = vanilla.TextBox((spX, 5, edWidth, txY), "Left", sizeStyle="small")
			self.s.text2 = vanilla.TextBox((spX*2+edWidth, 5, edWidth, txY), "Right", sizeStyle="small")
			self.s.group1 = vanilla.TextEditor((spX, 10+txY, edWidth, -spY*2-btnY), groupText1)
			self.s.group1._textView.setFont_( Menlo12 )
			self.s.group2 = vanilla.TextEditor((spX*2+edWidth, 10+txY, edWidth, -spY*2-btnY), groupText2)
			self.s.group2._textView.setFont_( Menlo12 )
			self.s.cancel = vanilla.Button((-spX*2-200, -spY-btnY, 100, -spY), "Cancel", callback=self.cancelChange)
			self.s.ok = vanilla.Button((-spX-100, -spY-btnY, -spX, -spY), "OK", callback=self.confirmChange)
			self.s.setDefaultButton( self.s.ok )
			self.s.open()
		except IndexError:
				pass
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (permListDoubleClick): %s" % e

	def dragCallback(self, sender, indexes):
		return indexes
	
	def dropListSelfCallback(self, sender, dropInfo):
		isProposal = dropInfo["isProposal"]
		
		if not isProposal:
			indexes = [int(i) for i in sorted(dropInfo["data"])]
			indexes.sort()
			source = dropInfo["source"]
			rowIndex = dropInfo["rowIndex"]

			items = sender.get()

			toMove = [items[index] for index in indexes]

			for index in reversed(indexes):
				del items[index]

			rowIndex -= len([index for index in indexes if index < rowIndex])
			for font in toMove:
				items.insert(rowIndex, font)
				rowIndex += 1

			sender.set(items)
		return True

	def _dragCallback(self, sender, indexes): # It's supposed to initialise dragging?
					#Added "indexes" because some other script was doing it, though I don't know why.
		try:
			print indexes
			print 'being dragged!'
			return sender.getSelection()[0]
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (dragCallback): %s" % e

	def dropCallback(self, sender, info): # It's supposed to accept dropped item and reorder. I don't know how to make it work.
		try:
			print "dropped!"
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (dropCallback): %s" % e

	def addButton(self, sender): # Adds a new line at the bottom of the List
		try:
			emptyPermutation = {" ": len(self.w.tabs[0].permList)+1, "Left":"", "Right":"", "Add Flipped":False, "Pair Count":0 }
			self.w.tabs[0].permList.append(emptyPermutation)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (addButton): %s" % e

	def delButton(self, sender): # Deletes the selected row in the List
		try:
			indexNum = self.w.tabs[0].permList.getSelection()[0] # Need to improve selection!
			del self.w.tabs[0].permList[indexNum]
		except IndexError:
			pass

	def refreshTotal( self ): # Deletes the selected row in the List
		try:
			totalPairs = 0
			for i in range(len(self.w.tabs[0].permList)):
				totalPairs += self.w.tabs[0].permList[i]["Pair Count"]
			self.w.tabs[0].total.set("Total: %s" % totalPairs)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (refreshTotal): %s" % e

# Functions specific to sheet from here
	def cancelChange(self, sender):
		try:
			self.s.close()
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (cancelChange): %s" % e

	def cleanUpText(self, text): # Function to clean up the text in sheet
		try:
			text.decode('ascii')
			if text.count("/") >= 1: # if text is slash-separated
				text = re.sub("/", " ", text)
			text = re.sub("[,\n\t]", " ", text)
			text = re.sub(r"  +", " ", text)
			if text[0] == " ":
				text = text[1:]
			return text
		except: # The text wasn't ascii-decodable. Probably not a string of glyph names.
			return False

	def confirmChange(self, sender):
		try:
			text1 = self.s.group1.get()
			text2 = self.s.group2.get()
			newText1 = self.cleanUpText(text1)
			newText2 = self.cleanUpText(text2)
			if newText1 == False or newText2 == False:
				Glyphs.displayDialog_("Invalid input. Only a string of glyph names separated by space, comma, or slash is accepted.")
			else:
				i = self.w.tabs[0].permList.getSelection()[0]
				self.w.tabs[0].permList[i]["Left"] = newText1
				self.w.tabs[0].permList[i]["Right"] = newText2
				self.s.close()
				self.refreshSectionPreview(i)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (confirmChange): %s" % e

# Functions specific to tabs[1] from here
	def loadFile( self, sender ):
		try:
			textFilePath = GetOpenFile(
				message = "Select a Text File. Metrics Machine format can be accepted.",
				allowsMultipleSelection = False,
				filetypes = ["text", "txt"]
			)
			theFile = open( os.path.expanduser(textFilePath) )
			theFileContent = theFile.read()
			if theFileContent[:5]:
				theFileContent = '\n'.join(theFileContent.split('\n')[1:]) 
			self.w.tabs[1].flatPairs.set( theFileContent )
			theFile.close()
			self.refreshPairNum(self)
		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (loadFile): %s" % e

	def refreshPairNum( self, sender ): # function to refresh pair number count.
		try:
			textEditorContent = self.w.tabs[1].flatPairs.get()
			someText = re.sub('\n\n', '\n', textEditorContent)
			someList = someText.lstrip().rstrip().split('\n')
			isSafe = True
			textToSet = ''
			if someText == '':
				textToSet = 'Nothing'
				isSafe = False
			if '\n\n' in someText:
				textToSet += "Consecutive blank lines found. "
				isSafe = False
			if any(i for i in someList if not re.match("^[\w\d.\-]+\s[\w\d.\-]+$", i)):
				textToSet += "Invalid line(s) found."
				isSafe = False
			if isSafe:
				suffix = 'pair' if len(someList) == 1 else 'pairs'
				textToSet = "%s %s" % (len(someList), suffix)
			self.w.tabs[1].pairNum.set( textToSet )
			if sender == self.w.allButton or self.w.selButton:
				return isSafe, someList
		except Exception, e:
			print "BubbleKern Error (refreshPairNum): %s" % e

	def BubbleKernMain( self, sender ):
		try:
			# Only the "Copy" funciton has been implemented
			if self.w.tabs.get() == 0: # if source is pair list builder
				pairList = []
				for i in range(len(self.w.tabs[0].permList)):
					selectedDic = self.w.tabs[0].permList[i]
					mixA = selectedDic["Left"].split()
					mixB = selectedDic["Right"].split()
					isFlipped = selectedDic["Add Flipped"]
					pairList.extend(["%s %s" % (charA, charB) for charA in mixA for charB in mixB ])
					if isFlipped == True:
						pairList.extend(["%s %s" % (charB, charA) for charA in mixA for charB in mixB ])
				pairText = '\n'.join(pairList)
				if sender == self.w.tabs[0].options: # If it came from "Copy" popup menu item
					os.system("echo '%s' | pbcopy" % pairText)
					return
			elif self.w.tabs.get() == 1: # if source is flat text
				if self.refreshPairNum(sender)[0]: # it's safe to process
					pairList = self.refreshPairNum(sender)[1]
				else:
					Glyphs.displayDialog_("You need to clean up your text first!")	
			font = Glyphs.font
			theMaster = font.selectedFontMaster
			# Resolution of bubble. 1 unit is most accurate, unnecessarily accurate, and really slow.
			# 20 sounds a bit rough, but the result is not bad in my opinion.
			unit = 10
			# Making a dictionary of bubbles of all glyphs (only in current layer)
			bubbleDic = {}
			# bubbleDic > glyph.name > LB > height : value
			#							RB > height : value
			pairList = set(pairList) # pairList until this point may contain duplicates, which are deleted here
			if sender == self.w.selButton:
				selectedGlyphNames = [i.parent.name for i in font.selectedLayers]
				pairList = {pair for pair in pairList for gName in selectedGlyphNames if gName == pair.split()[0] or gName == pair.split()[1]}

			# List of unique glyph names made from pairList. May contain non-existent glyphs.
			charSet = {letters for pair in pairList for letters in pair.split()}
			
			for glyphName in charSet:
				if font.glyphs[glyphName]:
					glyph = font.glyphs[glyphName]
					finalBubbleLayer = GSLayer() # gather all bubble outline data in this ghost layer. Initialise at every glyph
					for layer in glyph.layers:
						if layer.name == "bubble" and layer.associatedFontMaster().name == theMaster.name: # if bubble layer exists in a glyph
							finalBubbleLayer.width = layer.width
							for pathToCopy in layer.paths:
								finalBubbleLayer.addPath_(pathToCopy.copy())
						if layer == glyph.layers[theMaster.id]:
							theComponents = layer.components
							numberOfComponents = len( theComponents )
							if numberOfComponents != 0: # if the master layer has components
								for thisCompo in theComponents:
									for thisLayer in thisCompo.component.layers:
										if thisLayer.name == "bubble" and thisLayer.associatedFontMaster().name == theMaster.name: # if component has a bubble
												try:
													copiedLayer = thisLayer.copy()
													Transform = NSAffineTransform.transform()
													Transform.setTransformStruct_(thisCompo.transform)
													copiedLayer.transform_checkForSelection_(Transform, False)
													for pathCopy in copiedLayer.paths:
														finalBubbleLayer.addPath_(pathCopy)
												except:
													pass

					if 'finalBubbleLayer' in locals():
						if len(finalBubbleLayer.paths) > 0:
							bubbleDic[glyph.name] = {}
							bubbleDic[glyph.name]["LB"] = {}
							bubbleDic[glyph.name]["RB"] = {}
							highest = int(finalBubbleLayer.bounds.origin.y + finalBubbleLayer.bounds.size.height)
							lowest = int(round(finalBubbleLayer.bounds.origin.y/unit)*unit-unit)
							for y in range( lowest, highest, unit ):
								intersections = finalBubbleLayer.intersectionsBetweenPoints((-4000, y), (4000, y))
								if len( intersections ) > 2:
									bubbleDic[glyph.name]["LB"][y] = round(intersections[1].x)
									bubbleDic[glyph.name]["RB"][y] = glyph.layers[theMaster.id].width - round(intersections[-2].x)

			#　function that rounds up the given number to nearest 10, used for applying minimal kernValue
			# I use this because kern value may be negative.
			def roundup(givenNumber):
				return int(ceil(givenNumber / 10.0)) * 10
			
			for pair in pairList:
				(left, right) = pair.split()
				if font.glyphs[left] and font.glyphs[right] and (left in bubbleDic) and (right in bubbleDic): # only if both glyphs exist:
					# some arbitrary big number to start with
					kernValue = 1000
					# maximum possible kern value, half width of whichever is narrower
					maxKern = min(font.glyphs[left].layers[theMaster.id].width, font.glyphs[right].layers[theMaster.id].width)/2-1
					for y, value in bubbleDic[left]["RB"].iteritems():
						if y in bubbleDic[right]["LB"]:
							if value + bubbleDic[right]["LB"][y] <= kernValue:
								kernValue = value + bubbleDic[right]["LB"][y]
					if kernValue < maxKern:
						if abs(kernValue) >= 10: # kerned as is if larger than 10 units
							font.setKerningForPair(theMaster.id, left, right, -kernValue)
						elif 8 <= abs(kernValue) < 10: # kerned 10 units if it's between 7 and 10
							font.setKerningForPair(theMaster.id, left, right, -roundup(kernValue))
					else: # activates fail-safe by using maxKern if kernValue is too large or infinite
						font.setKerningForPair(theMaster.id, left, right, -int(maxKern))
		# When do you save flat text?

		except Exception, e:
			Glyphs.showMacroWindow()
			print "BubbleKern Error (BubbleKernMain): %s" % e

BubbleKern()
try:
	del lastIndex
except:
	pass
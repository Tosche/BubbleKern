from __future__ import print_function

# MenuTitle: Delete Bubble Layers
# -*- coding: utf-8 -*-
__doc__ = """
Deletes bubble layers in selected glyphs (for current master only).
"""

from GlyphsApp import Glyphs

font = Glyphs.font  # frontmost font
fontMaster = font.selectedFontMaster  # active master
selectedLayers = font.selectedLayers  # active layers of selected glyphs
thisDoc = Glyphs.currentDocument

font.disableUpdateInterface()  # suppresses UI updates in Font View
Glyphs.clearLog()

for layer in selectedLayers:
	glyph = layer.parent
	glyph.beginUndo()  # begin undo grouping
	bubbleLayerList = [bubbleLayer for bubbleLayer in glyph.layers if bubbleLayer.name == "bubble"]
	print(bubbleLayerList)
	for bubble in bubbleLayerList:
		if bubble.associatedMasterId == fontMaster.id:
			print("delete")
			if Glyphs.versionNumber >= 3:
				glyph.removeLayerForId_(bubble.layerId)
			else:
				glyph.removeLayerForKey_(bubble.layerId)
	glyph.endUndo()  # end undo grouping

font.enableUpdateInterface()  # re-enables UI updates in Font View
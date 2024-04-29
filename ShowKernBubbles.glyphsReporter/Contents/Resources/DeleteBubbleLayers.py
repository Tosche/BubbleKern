from __future__ import print_function

# MenuTitle: Delete Bubble Layers
# -*- coding: utf-8 -*-
__doc__ = """
Deletes bubble layers in selected glyphs (for current master only).
"""


def deleteBubbleLayers(selectedLayers, font):

	font.disableUpdateInterface()  # suppresses UI updates in Font View

	for layer in selectedLayers:
		glyph = layer.parent
		glyph.beginUndo()  # begin undo grouping
		bubbleLayerList = [bubbleLayer for bubbleLayer in glyph.layers if bubbleLayer.name == "bubble" and bubbleLayer.associatedMasterId == layer.associatedMasterId]
		print(bubbleLayerList)
		for bubble in bubbleLayerList:
			print("delete")
			del glyph.layers[bubble.layerId]
		glyph.endUndo()  # end undo grouping

	font.enableUpdateInterface()  # re-enables UI updates in Font View

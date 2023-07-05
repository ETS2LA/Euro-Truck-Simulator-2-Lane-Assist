from enum import Enum

class LaneModelType(Enum):
	UFLD_TUSIMPLE = 0
	UFLD_CULANE = 1
	UFLDV2_TUSIMPLE = 2
	UFLDV2_CULANE = 3

class OffsetType(Enum):
	UNKNOWN = "To Be Determined ..."
	RIGHT = "Please Keep Right"
	LEFT = "Please Keep Left"
	CENTER = "Good Lane Keeping"

class CurvatureType(Enum):
	UNKNOWN = "To Be Determined ..."
	STRAIGHT = "Keep Straight Ahead"
	EASY_LEFT =  "Gentle Left Curve Ahead"
	HARD_LEFT = "Hard Left Curve Ahead"
	EASY_RIGHT = "Gentle Right Curve Ahead"
	HARD_RIGHT = "Hard Right Curve Ahead"

lane_colors = [(255, 0, 0),(46,139,87),(50,205,50),(0,255,255)]

tusimple_row_anchor = [ 64,  68,  72,  76,  80,  84,  88,  92,  96, 100, 104, 108, 112,
			116, 120, 124, 128, 132, 136, 140, 144, 148, 152, 156, 160, 164,
			168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216,
			220, 224, 228, 232, 236, 240, 244, 248, 252, 256, 260, 264, 268,
			272, 276, 280, 284]
culane_row_anchor = [121, 131, 141, 150, 160, 170, 180, 189, 199, 209, 219, 228, 238, 248, 258, 267, 277, 287]
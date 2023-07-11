import numpy as np

# Sample input data
points =  [{'IsEmpty': False, 'X': 32831.39, 'Y': 17884.5078}, {'IsEmpty': False, 'X': 32825.1328, 'Y': 17871.7773}, {'IsEmpty': False, 'X': 32819.1563, 'Y': 17858.9121}, {'IsEmpty': False, 'X': 32813.3633, 'Y': 17845.959}, {'IsEmpty': False, 'X': 32807.68, 'Y': 17832.9531}, {'IsEmpty': False, 'X': 32802.01, 'Y': 17819.94}, {'IsEmpty': False, 'X': 32796.2773, 'Y': 17806.957}, {'IsEmpty': False, 'X': 32790.3867, 'Y': 17794.0469}]
lanesLeft = 2
lanesRight = 2
roadSizeRight = 1.0
roadSizeLeft = 1.0

# Calculate lane width
totalRoadWidth = roadSizeRight + roadSizeLeft
laneWidth = totalRoadWidth / (lanesRight + lanesLeft)

# Calculate the points for each lane
newPoints = []

for point in points:
    x = point['X']
    y = point['Y']

    # Calculate the tangent vector at the point
    yPoints = np.array([point['Y'] for point in points])
    xPoints = np.array([point['X'] for point in points])
    tangentVector = np.gradient(yPoints, xPoints).T

    # Calculate the normal vector (perpendicular to the tangent)
    normalVector = np.array([-tangentVector[1], tangentVector[0]])

    # Normalize the normal vector
    normalVector /= np.linalg.norm(normalVector, axis=0)

    # Calculate the offset for each lane
    laneOffsets = np.arange(-lanesLeft, lanesRight + 1) * laneWidth

    # Calculate the new points for each lane
    for laneOffset in laneOffsets:
        offsetVector = laneOffset * normalVector

        newPoint = np.array([x, y]) + offsetVector.T
        newPoints.append(newPoint.tolist())

# Print the new points
for lanePoints in newPoints:
    print("Lane")
    print(lanePoints)
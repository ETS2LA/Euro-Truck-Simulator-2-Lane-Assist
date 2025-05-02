import Modules.BetterShowImage.main as ShowImage
import ETS2LA.Handlers.pytorch as pytorch
import variables as MLVSSVariables
import utils as MLVSSUtils
import numpy as np
import math
import time
import cv2


def initialize():
    global Model
    global Images
    global FRAME

    ShowImage.Initialize(Name="Mapping", TitleBarColor=(0, 0, 0))

    Model = pytorch.Model(HuggingFaceOwner="OleFranz", HuggingFaceRepository="MLVSS", HuggingFaceModelFolder="models/mapping", PluginSelf=MLVSSVariables.plugin_self, DType=pytorch.torch.float32)
    Model.Load()

    Images = []
    FRAME = np.zeros((500, 500, 3), np.uint8)


def GenerateImage(Frame):
    Prediction = GenerateMask(Frame)
    Prediction = cv2.cvtColor(Prediction, cv2.COLOR_GRAY2BGRA)
    Prediction[:, :, 2] = 0
    Frame = cv2.cvtColor(Frame, cv2.COLOR_BGR2BGRA)
    Frame = cv2.addWeighted(Frame, 1, Prediction, 0.5, 0)
    Frame = cv2.cvtColor(Frame, cv2.COLOR_BGRA2BGR)
    return Frame


def GenerateMask(Frame):
    Size = Frame.shape
    Frame = cv2.resize(cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB), (Model.ImageWidth, Model.ImageHeight))
    Frame = pytorch.transforms.ToTensor()(Frame)
    with pytorch.torch.no_grad():
        Prediction = Model.Model(Frame.unsqueeze(0).to(Model.Device))
    Prediction = Prediction.squeeze(0).cpu()[0].numpy() * 255
    Prediction = Prediction.astype(np.uint8)
    Prediction = cv2.resize(Prediction, (Size[1], Size[0]))
    return Prediction


def run():
    Frame = MLVSSVariables.latest_frame
    if Model.Loaded == False: time.sleep(0.1); return
    if type(Frame) == type(None) or Frame.shape[0] <= 0 or Frame.shape[1] <= 0:
        return


    AllCoordinatesValid = True
    Points = []


    OffsetX = 60
    OffsetZ = 14

    PointX = MLVSSUtils.truck_x + OffsetX * math.sin(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.cos(MLVSSUtils.truck_rotation_radians_x)
    PointY = MLVSSUtils.truck_y + math.tan(math.radians(MLVSSUtils.truck_rotation_y * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
    PointZ = MLVSSUtils.truck_z - OffsetX * math.cos(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.sin(MLVSSUtils.truck_rotation_radians_x)

    X, Y, D = MLVSSUtils.convert_to_screen_coordinate(PointX, PointY, PointZ)
    if X == None or Y == None:
        AllCoordinatesValid = False
    else:
        TopLeft = X, Y
        Points.append((PointX, PointZ))


    OffsetX = 60
    OffsetZ = -14

    PointX = MLVSSUtils.truck_x + OffsetX * math.sin(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.cos(MLVSSUtils.truck_rotation_radians_x)
    PointY = MLVSSUtils.truck_y + math.tan(math.radians(MLVSSUtils.truck_rotation_y * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
    PointZ = MLVSSUtils.truck_z - OffsetX * math.cos(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.sin(MLVSSUtils.truck_rotation_radians_x)

    X, Y, D = MLVSSUtils.convert_to_screen_coordinate(PointX, PointY, PointZ)
    if X == None or Y == None:
        AllCoordinatesValid = False
    else:
        TopRight = X, Y
        Points.append((PointX, PointZ))


    OffsetX = 15
    OffsetZ = 5

    PointX = MLVSSUtils.truck_x + OffsetX * math.sin(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.cos(MLVSSUtils.truck_rotation_radians_x)
    PointY = MLVSSUtils.truck_y + math.tan(math.radians(MLVSSUtils.truck_rotation_y * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
    PointZ = MLVSSUtils.truck_z - OffsetX * math.cos(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.sin(MLVSSUtils.truck_rotation_radians_x)

    X, Y, D = MLVSSUtils.convert_to_screen_coordinate(PointX, PointY, PointZ)
    if X == None or Y == None:
        AllCoordinatesValid = False
    else:
        BottomLeft = X, Y
        Points.append((PointX, PointZ))


    OffsetX = 15
    OffsetZ = -5

    PointX = MLVSSUtils.truck_x + OffsetX * math.sin(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.cos(MLVSSUtils.truck_rotation_radians_x)
    PointY = MLVSSUtils.truck_y + math.tan(math.radians(MLVSSUtils.truck_rotation_y * 360)) * math.sqrt(OffsetX**2 + OffsetZ**2)
    PointZ = MLVSSUtils.truck_z - OffsetX * math.cos(MLVSSUtils.truck_rotation_radians_x) - OffsetZ * math.sin(MLVSSUtils.truck_rotation_radians_x)

    X, Y, D = MLVSSUtils.convert_to_screen_coordinate(PointX, PointY, PointZ)
    if X == None or Y == None:
        AllCoordinatesValid = False
    else:
        BottomRight = X, Y
        Points.append((PointX, PointZ))


    if AllCoordinatesValid:
        try:
            CroppedWidth = round(max(TopRight[0] - TopLeft[0], BottomRight[0] - BottomLeft[0]))
            CroppedHeight = round(max(BottomLeft[1] - TopLeft[1], BottomRight[1] - TopRight[1]))
            SourcePoints = np.float32([TopLeft, TopRight, BottomLeft, BottomRight])
            DestinationPoints = np.float32([[0, 0], [CroppedWidth, 0], [0, CroppedHeight], [CroppedWidth, CroppedHeight]])
            Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
            CroppedFrame = cv2.warpPerspective(Frame, Matrix, (CroppedWidth, CroppedHeight))

            RoadMask = GenerateMask(CroppedFrame)
            cv2.threshold(RoadMask, 127, 255, cv2.THRESH_BINARY, RoadMask)
            CroppedFrame = cv2.bitwise_and(CroppedFrame, CroppedFrame, mask=RoadMask)

            MinX = min(Points[0][0], Points[1][0], Points[2][0], Points[3][0])
            MinZ = min(Points[0][1], Points[1][1], Points[2][1], Points[3][1])
            Scale = 12
            OnFrameX1 = (Points[0][0] - MinX) * Scale
            OnFrameY1 = (Points[0][1] - MinZ) * Scale
            OnFrameX2 = (Points[2][0] - MinX) * Scale
            OnFrameY2 = (Points[2][1] - MinZ) * Scale
            OnFrameX3 = (Points[3][0] - MinX) * Scale
            OnFrameY3 = (Points[3][1] - MinZ) * Scale
            OnFrameX4 = (Points[1][0] - MinX) * Scale
            OnFrameY4 = (Points[1][1] - MinZ) * Scale

            SourcePoints = np.float32([[0, 0], [CroppedFrame.shape[1], 0], [0, CroppedFrame.shape[0]], [CroppedFrame.shape[1], CroppedFrame.shape[0]]])
            DestinationPoints = np.float32([[OnFrameX1, OnFrameY1], [OnFrameX4, OnFrameY4], [OnFrameX2, OnFrameY2], [OnFrameX3, OnFrameY3]])
            Matrix = cv2.getPerspectiveTransform(SourcePoints, DestinationPoints)
            Frame = cv2.warpPerspective(CroppedFrame, Matrix, (500, 500), flags=cv2.INTER_NEAREST)
            Images.append((Frame, Points))
        except:
            import traceback
            print(traceback.format_exc())

    Canvas = FRAME.copy()
    CenterX, CenterZ = 250, 250

    for i, (Image, Points) in enumerate(Images):
        MinX = min(Point[0] for Point in Points)
        MinZ = min(Point[1] for Point in Points)
        MaxX = max(Point[0] for Point in Points)
        MaxZ = max(Point[1] for Point in Points)

        CenterImageX = (MaxX + MinX) / 2
        CenterImageZ = (MaxZ + MinZ) / 2

        OffsetX = int((CenterImageX - MLVSSUtils.truck_x) * 12 + CenterX - Image.shape[1] / 2)
        OffsetZ = int((CenterImageZ - MLVSSUtils.truck_z) * 12 + CenterZ - Image.shape[0] / 2)

        StartX = max(0, OffsetX)
        StartZ = max(0, OffsetZ)
        EndX = min(Canvas.shape[1], OffsetX + Image.shape[1])
        EndZ = min(Canvas.shape[0], OffsetZ + Image.shape[0])

        CropStartX = max(0, -OffsetX)
        CropStartZ = max(0, -OffsetZ)
        CropEndX = Image.shape[1] - max(0, (OffsetX + Image.shape[1]) - Canvas.shape[1])
        CropEndZ = Image.shape[0] - max(0, (OffsetZ + Image.shape[0]) - Canvas.shape[0])

        Region = Canvas[StartZ:EndZ, StartX:EndX]
        ImageRegion = Image[CropStartZ:CropEndZ, CropStartX:CropEndX]

        if Region.shape == ImageRegion.shape and ImageRegion.size > 0:
            Mask = cv2.cvtColor(ImageRegion, cv2.COLOR_BGR2GRAY) > 0
            Region[Mask] = ImageRegion[Mask]

    Frame = Canvas

    def ConvertToFrameCoordinate(X, Z):
        Scale = 12
        CenterX, CenterZ = 180, 180  # Some magic numbers, not correct

        FrameX = int((X) * Scale + CenterX)
        FrameZ = int((Z) * Scale + CenterZ)

        return FrameX, FrameZ

    for i in range(len(MLVSSUtils.wheel_coordinates)):
        point_x = MLVSSUtils.wheel_coordinates[i][0] - MLVSSUtils.truck_x
        point_z = MLVSSUtils.wheel_coordinates[i][2] - MLVSSUtils.truck_z
        cv2.circle(Frame, [*ConvertToFrameCoordinate(point_x, point_z)], 5, (0, 0, 255), 2)

    ShowImage.Show(Name="Mapping", Frame=Frame)
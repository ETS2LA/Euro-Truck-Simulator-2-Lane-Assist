import cv2
import logging
import numpy as np
try :
    from plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import  lane_colors, OffsetType
except :
    from ..plugins.UFLDLaneDetection.UFLD.ultrafastLaneDetector.utils import lane_colors, OffsetType

class PerspectiveTransformation(object):
    """ This a class for transforming image between frontal view and bird view

    Attributes:
        src (np.array): Coordinates of 4 source points
        dst (np.array): Coordinates of 4 destination points
        M (np.array): Matrix to transform image from frontal view to bird view
        M_inv (np.array): Matrix to transform image from bird view to frontal view
    """
    def __init__(self, img_size=(1280, 720), logger=None ):
        """Init PerspectiveTransformation."""
        self.img_size = img_size
        self.logger = logger

        self.src = np.float32([(self.img_size[0]*0.3, self.img_size[1]*0.7),     # top-left
                               (self.img_size[0]*0.2, self.img_size[1]),         # bottom-left
                               (self.img_size[0]*0.95, self.img_size[1]),        # bottom-right
                               (self.img_size[0]*0.8, self.img_size[1]*0.7)])    # top-right
        self.offset_x = self.img_size[0]/4
        self.offset_y = 0
        self.dst = np.float32([(self.offset_x, self.offset_y), 
                                (self.offset_x, img_size[1]-self.offset_y),
                                (img_size[0]-self.offset_x, img_size[1]-self.offset_y),
                                (img_size[0]-self.offset_x, self.offset_y),])
        self.M = cv2.getPerspectiveTransform(self.src, self.dst)
        self.M_inv = cv2.getPerspectiveTransform(self.dst, self.src)


    def updateTransformParams(self, left_lanes, right_lanes, type="Default") :
        """ 
        Update the transition area of the frontal view

        Args:
            left_lanes (np.array): Left lanes points.[[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]
            right_lanes (np.array): Right lanes points.[[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]
            type: Adjust the area of specific points, type-"Top", "Bottom", "Default"

        Returns:
            None
        """
        if (len(left_lanes) and len(right_lanes)) :
            left_lanes = np.squeeze(left_lanes)
            right_lanes = np.squeeze(right_lanes)
            if (type=="Top"):
                top_y = min(min(left_lanes[:, 1]), min(right_lanes[:, 1]))
                top_left     = ( max(left_lanes[:, 0])-20, top_y )
                bottom_left  = ( self.src[1][0], self.src[1][1] )
                bottom_right = ( self.src[2][0], self.src[2][1] )
                top_right    = ( min(right_lanes[:, 0])+20, top_y )
            elif (type=="Bottom") :
                top_left     = ( self.src[0][0], self.src[0][1] )
                bottom_left  = ( min(left_lanes[:, 0]), self.src[1][1] )
                bottom_right = ( max(right_lanes[:, 0]), self.src[2][1] )
                top_right    =  ( self.src[3][0], self.src[3][1] )
            elif (type=="Default") :
                top_y = min(min(left_lanes[:, 1]), min(right_lanes[:, 1]))
                top_left     = ( max(left_lanes[:, 0])-20, top_y )
                bottom_left  = ( min(left_lanes[:, 0]), self.src[1][1] )
                bottom_right = ( max(right_lanes[:, 0]), self.src[2][1] )
                top_right    = ( min(right_lanes[:, 0])+20, top_y)
            else :
                return 
            # print("top-left :", top_left )
            # print("bottom-left :", bottom_left )
            # print("bottom-right :", bottom_right )
            # print("top-right :", top_right )
            self.src = np.float32([ top_left, bottom_left, bottom_right, top_right]) 
            self.M = cv2.getPerspectiveTransform(self.src, self.dst)
            self.M_inv = cv2.getPerspectiveTransform(self.dst, self.src)


    def transformToBirdView(self, img, flags=cv2.INTER_LINEAR):
        """ Take a frontal view image and transform to bird view

        Args:
            img (np.array): A frontal view image
            img_size (tuple): Size of the image (width, height)
            flags : flag to use in cv2.warpPerspective()

        Returns:
            Image (np.array): Bird view image
        """
        # new_size = ( self.img_size[0], int(self.img_size[1]/0.33))
        # img_input = cv2.resize(img, new_size).astype(np.float32)
        # img = img_input[self.img_size[1]:-self.img_size[1], :, :]
        return cv2.warpPerspective(img, self.M, self.img_size, flags=flags)


    def transformToFrontalView(self, img, flags=cv2.INTER_LINEAR):
        """ Take a bird view image and transform it to frontal view

        Args:
            img (np.array): A bird view image
            img_size (tuple): Size of the image (width, height)
            flags (int): flag to use in cv2.warpPerspective()

        Returns:
            Image (np.array): Frontal view image
        """
        return cv2.warpPerspective(img, self.M_inv, self.img_size, flags=flags)
    

    def transformToBirdViewPoints(self, points):
        """
        To get bird view points in the new perspective from frontal view points in the image.

        Args:
            points: Frontal view lane points.

        Returns:
            [[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]. array shape=(xn, 2)
        """
        points_array = []
        if (len(points)) :
            for x, y in points :
                points_array.append([x, y])
                # dst_y = (y/0.33)
                # if ( (dst_y > self.img_size[1]) and (dst_y <= int(self.img_size[1]/0.33)*(2/3)) ) :
                #     points_array.append([x, dst_y-self.img_size[1]])
            if (len(points_array)) :
                points_array = np.array(points_array)
                new_points = np.einsum('kl, ...l->...k', self.M,  np.concatenate([points_array, np.broadcast_to(1, (*points_array.shape[:-1], 1)) ], axis = -1) )
               
                return np.asarray(new_points[...,:2] / new_points[...,2][...,None], dtype = 'int')
        return []


    def calcCurveAndOffset(self, img, left_lanes, right_lanes):
        """
        Calculate the offset and road curve from the center of the vehicle.
        
        Args:
            img: Bird view image.
            left_lanes (np.array): Left lanes points.[[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]
            right_lanes (np.array): Right lanes points.[[x1, y1], [x2, y2], [x3, y3] ... [xn, yn]]

        Returns:
            direction (string): Type contains "L", "R" or "F".
            curvature (float): Road curve.
            offset (float): Offset from the center point.
            
            Output format tuple(tuple(direction, curvature), offset)
        """
        if (len(left_lanes) and len(right_lanes)) :
            left_lanes = np.squeeze(left_lanes)
            right_lanes = np.squeeze(right_lanes)
            left_fit = np.polyfit(left_lanes[:, 1], left_lanes[:, 0], 2)
            right_fit = np.polyfit(right_lanes[:, 1], right_lanes[:, 0], 2)

            # Define direction conditions
            if abs(left_fit[0]) > abs(right_fit[0]):
                side_cr = left_fit[0]
            else:
                side_cr = right_fit[0]

            if side_cr < -0.00015 and ( left_lanes[0, 0] <= left_lanes[ int(len(left_lanes)/2), 0]):
                curvature_direction = "L"
            elif  side_cr > 0.00015  and (right_lanes[0, 0] >= right_lanes[ int(len(right_lanes)/2), 0] ):
                curvature_direction = "R"
            else :
                curvature_direction = "F"

            # Define y-value where we want radius of curvature
            ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )
            leftx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
            rightx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
            # print("left :", leftx[0], leftx[-1])

            # Define conversions in x and y from pixels space to meters
            ym_per_pix = 30/720 # meters per pixel in y dimension
            xm_per_pix = 3.7/700 # meters per pixel in x dimension
            y_eval = np.max(ploty)
            # Fit new polynomials to x,y in world space
            left_fit_cr = np.polyfit(ploty*ym_per_pix, leftx*xm_per_pix, 2)
            right_fit_cr = np.polyfit(ploty*ym_per_pix, rightx*xm_per_pix, 2)
            # Calculate the new radii of curvature
            left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
            right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])

            curvature = ((left_curverad + right_curverad) / 2)
            lane_width = np.absolute(leftx[719] - rightx[719])

            lane_xm_per_pix = 3.7 / lane_width
            veh_pos = ((leftx[719] + rightx[719])  / 2.)

            cen_pos = (img.shape[1]/ 2.)
            cv2.arrowedLine(img, (int(veh_pos), int(y_eval)), (int(veh_pos), int(img.shape[1]/3)), (255, 255, 255), 5, 0, 0 , 0.2)
            cv2.arrowedLine(img, (int(cen_pos), int(y_eval)), (int(cen_pos), int(img.shape[0]/1.3)), (150, 150, 150), 10, 0, 0 , 0.5)
            distance_from_center = (veh_pos - cen_pos)* lane_xm_per_pix
        else :
            curvature_direction, curvature = None, None
            distance_from_center = None
            return (curvature_direction, curvature), distance_from_center

        cv2.putText(img,  'Offset: %.1f m' % distance_from_center, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
        cv2.putText(img,  'R : %.1f m' % curvature, (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
        return (curvature_direction, curvature), distance_from_center


    def DrawDetectedOnBirdView(self, image, lanes_points, type=OffsetType.UNKNOWN) :
        for lane_num, lane_points in enumerate(lanes_points):
            if ( lane_num==1 and type == OffsetType.RIGHT) :
                color = (0, 0, 255)
            elif (lane_num==2 and type == OffsetType.LEFT) :
                color = (0, 0, 255)
            else :
                color = lane_colors[lane_num]
            for x, y in lane_points:
                cv2.circle(image, (int(x), int(y)), 10, color, -1)


    def DrawTransformFrontalViewArea(self, image):
        vector = np.vectorize(np.int_)
        cv2.line(image, vector(self.src[0]), vector(self.src[1]), (0, 0, 255), 5)
        cv2.line(image, vector(self.src[1]), vector(self.src[2]), (0, 0, 255), 5)
        cv2.line(image, vector(self.src[2]), vector(self.src[3]), (0, 0, 255), 5)
        cv2.line(image, vector(self.src[3]), vector(self.src[0]), (0, 0, 255), 5)
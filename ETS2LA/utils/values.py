from typing import List, Literal, Tuple
import time

class SmoothedValue:
    valueArray: List[float] | List[Tuple[int, float]]
    smoothingType: Literal["frames", "time"]
    smoothingAmount: int | float
    
    def __init__(self, smoothingType: Literal["frames", "time"] = "frames", smoothingAmount: int | float = 10) -> None:
        self.valueArray = []
        self.smoothingType = smoothingType
        self.smoothingAmount = smoothingAmount
        
    def get(self):
        if self.smoothingType == "frames":
            return sum(self.valueArray) / len(self.valueArray)
        elif self.smoothingType == "time":
            while self.valueArray[-1][0] - self.valueArray[0][0] > self.smoothingAmount:
                self.valueArray.pop(0) 
            if len(self.valueArray) == 0:
                return 0
            return sum([v for t, v in self.valueArray]) / len(self.valueArray)
        else:
            raise ValueError("Invalid smoothing type")
        
    def smooth(self, value):
        if self.smoothingType == "frames":
            self.valueArray.append(value)
            if len(self.valueArray) > self.smoothingAmount:
                self.valueArray.pop(0)
            return sum(self.valueArray) / len(self.valueArray)
        elif self.smoothingType == "time":
            self.valueArray.append([time.time(), value])
            while self.valueArray[-1][0] - self.valueArray[0][0] > self.smoothingAmount:
                self.valueArray.pop(0)
            return sum([v for t, v in self.valueArray]) / len(self.valueArray)
        else:
            raise ValueError("Invalid smoothing type")
        
    def __call__(self, value):
        return self.smooth(value)
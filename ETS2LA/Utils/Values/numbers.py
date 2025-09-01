# type: ignore
# TODO: Make this file type-safe.
from typing import List, Literal, Tuple
import time


class SmoothedValue:
    valueArray: List[float] | List[Tuple[int, float]]
    smoothingType: Literal["frames", "time"]
    smoothingAmount: int | float

    def __init__(
        self,
        smoothingType: Literal["frames", "time"] = "frames",
        smoothingAmount: int | float = 10,
    ) -> None:
        self.smoothingType = smoothingType
        self.smoothingAmount = smoothingAmount
        if smoothingType == "frames":
            self.valueArray = [0]
        elif smoothingType == "time":
            self.valueArray = [[time.perf_counter(), 0]]

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
            self.valueArray.append([time.perf_counter(), value])
            while self.valueArray[-1][0] - self.valueArray[0][0] > self.smoothingAmount:
                self.valueArray.pop(0)
            return sum([v for t, v in self.valueArray]) / len(self.valueArray)
        else:
            raise ValueError("Invalid smoothing type")

    def zero_percent_jitter(self, side: Literal["upper", "lower"] = "upper"):
        if self.smoothingType == "frames":
            sorted_values = sorted(self.valueArray)
            if side == "upper":
                return sorted_values[int(len(sorted_values) * 0.99)] - sorted_values[0]
            else:
                return sorted_values[0] - sorted_values[int(len(sorted_values) * 0.99)]
        elif self.smoothingType == "time":
            sorted_values = sorted([v for t, v in self.valueArray])
            if side == "upper":
                return sorted_values[int(len(sorted_values) * 0.99)] - sorted_values[0]
            else:
                return sorted_values[0] - sorted_values[int(len(sorted_values) * 0.99)]
        else:
            raise ValueError("Invalid smoothing type")

    def one_percent_jitter(self, side: Literal["upper", "lower"] = "upper"):
        if self.smoothingType == "frames":
            sorted_values = sorted(self.valueArray)
            if side == "upper":
                return (
                    sorted_values[int(len(sorted_values) * 0.99)]
                    - sorted_values[int(len(sorted_values) * 0.01)]
                )
            else:
                return (
                    sorted_values[int(len(sorted_values) * 0.01)]
                    - sorted_values[int(len(sorted_values) * 0.99)]
                )
        elif self.smoothingType == "time":
            sorted_values = sorted([v for t, v in self.valueArray])
            if side == "upper":
                return (
                    sorted_values[int(len(sorted_values) * 0.99)]
                    - sorted_values[int(len(sorted_values) * 0.01)]
                )
            else:
                return (
                    sorted_values[int(len(sorted_values) * 0.01)]
                    - sorted_values[int(len(sorted_values) * 0.99)]
                )
        else:
            raise ValueError("Invalid smoothing type")

    def ten_percent_jitter(self, side: Literal["upper", "lower"] = "upper"):
        if self.smoothingType == "frames":
            sorted_values = sorted(self.valueArray)
            if side == "upper":
                return (
                    sorted_values[int(len(sorted_values) * 0.9)]
                    - sorted_values[int(len(sorted_values) * 0.1)]
                )
            else:
                return (
                    sorted_values[int(len(sorted_values) * 0.1)]
                    - sorted_values[int(len(sorted_values) * 0.9)]
                )
        elif self.smoothingType == "time":
            sorted_values = sorted([v for t, v in self.valueArray])
            if side == "upper":
                return (
                    sorted_values[int(len(sorted_values) * 0.9)]
                    - sorted_values[int(len(sorted_values) * 0.1)]
                )
            else:
                return (
                    sorted_values[int(len(sorted_values) * 0.1)]
                    - sorted_values[int(len(sorted_values) * 0.9)]
                )
        else:
            raise ValueError("Invalid smoothing type")

    def __call__(self, value):
        return self.smooth(value)

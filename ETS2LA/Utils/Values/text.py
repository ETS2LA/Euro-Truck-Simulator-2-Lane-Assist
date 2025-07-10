class ScrollingText():
    def __init__(self, text: str, max_width: int = 20):
        self.text = text
        self.max_width = max_width
        self.current_index = 0
        self.start_wait_time = 5
        self.end_wait_time = 5
        self.direction = 1
        
    def get(self):
        if len(self.text) <= self.max_width:
            return self.text
        
        start = self.current_index
        end = start + self.max_width
        
        result = self.text[start:end]
        
        if self.start_wait_time > 0:
            self.start_wait_time -= 1
            return result
        
        if end > len(self.text):
            if self.end_wait_time > 0:
                self.end_wait_time -= 1
                return result
            
            self.current_index = 0
            self.end_wait_time = 5
            self.start_wait_time = 5
            return result
        
        self.current_index += self.direction
        return result
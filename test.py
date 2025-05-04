class Description:
    name: str
    def __init__(self, name: str):
        self.name = name

class Test:
    description: Description = Description("Tester")
    
print(Test.description.name)
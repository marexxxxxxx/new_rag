def splitting(eingang):
    text = ""
    sammlung = []
    is_enter = 0
    for i in eingang:
        if i == "\n" and is_enter == 1:
            sammlung.append(text)
            is_enter = 0
            text =""
        if i == "\n":
            is_enter = 1
        if i != "\n":
            is_enter = 0
        text +=i
    for i in sammlung:
        print(i)
        print("\n \n \n")

with open("test.txt", "r") as t: 
    splitting(t.read())
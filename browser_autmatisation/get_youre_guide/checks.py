from state import state


def check(state:state):
    if len(state["current_obj"]) >0:
        return 0
    elif len(state["current_obj"]) == 0 and state["list_with_text"] != []:
        return 1
    elif state["list_with_text"] == []:
        return 2


def schreibe_alles(state:state):
    with open("ergebnisse.txt", "w") as t:
        t.write(str(state["ergebnisse"]))


def get_data_check(state:state):
    if state["link"] == []:
        return 0
    if state["link"] == []:
        return 1

def go_deeper(state:state):
    if state["ergebnisse"] == []:
        return 0
    elif state["ergebnisse"] != []:
        return 1
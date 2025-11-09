from state import state


def check(state:state):
    if len(state["current_obj"]) >0:
        return 0
    elif len(state["current_obj"]) == 0 and state["list_with_text"] != []:
        return 1
    elif state["list_with_text"] == []:
        return 2
    else:
        raise Exception("check hat nicht funktioniert")


def schreibe_alles(state:state):
    with open("ergebnisse.txt", "w") as t:
        t.write(str(state["result_list"]))
        


def get_data_check(state:state):
    if state["link"] != []:
        return 0
    if state["link"] == []:
        return 1
    else:
        raise Exception("get_data_check hat nicht funktioniert")

def go_deeper_check(state:state):
    if state["ergebnisse"] != []:
        return 0
    elif state["ergebnisse"] == []:
        return 1
    else:
        raise Exception("go_deeper hat nicht funktioniert")
    
def memgraph_check(state:state):
    if state["ergebnisse"] != []:
        return 0
    if state["ergebnisse"] == []:
        return 20
    else:
        raise Exception("Unkown state of Ergebnis")

def check_if_link(state:state): #dafür zuständig zu überprüfen ob da ein Link drinne ist. falls nicht wird das näcshte Objekt genutzt
    if state["link"] == "":
        return 0
    if state["link"] != "":
        return 1
    else:
        raise Exception("Fehler bei get_deep_link")
    

def platzhalter(state:state):
    None
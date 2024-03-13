import hou

contexts = ["/obj","/mat","/stage"]

def changeParms(node, search, replace):
    string_parms = [p for p in node.parms() if p.parmTemplate().type() == hou.parmTemplateType.String]
    for parm in string_parms:
        if (search in parm.eval()):
            newValue = parm.rawValue().replace(search, replace)
            parm.set(newValue)

input = hou.ui.readMultiInput("Tell me what to look for: ", ("search","replace"), buttons=('OK',"Cancel"), default_choice=0, close_choice=1, title="Replace Files")
if (input[0] == 0):
    search = input[1][0]
    replace = input[1][1]
    for rootNode in contexts:
        for node in hou.node(rootNode).allSubChildren():
            changeParms(node, search, replace)
import string

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0  
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

def cmp_el(a,b):
    if a.tag < b.tag:
        return -1
    elif a.tag > b.tag:
        return 1
#    print a.tag
#    print a.tail
#    print a.text
#    print b.tail
#    print b.text
    translator = str.maketrans({key: None for key in string.whitespace})
    if a.tail != None and b.tail !=None:
        if a.tail.translate(translator) < b.tail.translate(translator):
            return -1
        elif a.tail.translate(translator) > b.tail.translate(translator):
            return 1
    if a.text != None and b.text !=None:
        if a.text.translate(translator) < b.text.translate(translator):
            return -1
        elif a.text.translate(translator) > b.text.translate(translator):
            return 1

    #compare attributes
    aitems = list(a.attrib.items())
    aitems.sort()
    bitems = list(b.attrib.items())
    bitems.sort()
    if aitems < bitems:
        return -1
    elif aitems > bitems:
        return 1

    #compare child nodes
    achildren = list(a)
    achildren.sort(key=cmp_to_key(cmp_el))
    bchildren = list(b)
    bchildren.sort(key=cmp_to_key(cmp_el))

    for achild, bchild in zip(achildren, bchildren):
        cmpval = cmp_el(achild, bchild)
        if  cmpval < 0:
            return -1
        elif cmpval > 0:
            return 1

    #must be equal
    return 0

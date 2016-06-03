import string

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
    if a.tail != None and b.tail !=None:
        if a.tail.translate(None, string.whitespace) < b.tail.translate(None, string.whitespace):
            return -1
        elif a.tail.translate(None, string.whitespace) > b.tail.translate(None, string.whitespace):
            return 1
    if a.text != None and b.text !=None:
        if a.text.translate(None, string.whitespace) < b.text.translate(None, string.whitespace):
            return -1
        elif a.text.translate(None, string.whitespace) > b.text.translate(None, string.whitespace):
            return 1

    #compare attributes
    aitems = a.attrib.items()
    aitems.sort()
    bitems = b.attrib.items()
    bitems.sort()
    if aitems < bitems:
        return -1
    elif aitems > bitems:
        return 1

    #compare child nodes
    achildren = list(a)
    achildren.sort(cmp=cmp_el)
    bchildren = list(b)
    bchildren.sort(cmp=cmp_el)

    for achild, bchild in zip(achildren, bchildren):
        cmpval = cmp_el(achild, bchild)
        if  cmpval < 0:
            return -1
        elif cmpval > 0:
            return 1

    #must be equal
    return 0

'''
Helper functions to be used by views.
'''


def FQNameToNameAndScope(fully_qualified_name):
    fqn = fully_qualified_name
    return (list(reversed(fqn.rsplit('.', 1)))
            if fqn.find('.') >= 0
            else [fqn, ''])


def FQNamesToIterList(names):
    for n in names:
        yield FQNameToNameAndScope(n)


def FQNamesToList(names):
    return list(FQNamesToIterList(names))


def FilterFQNamesToIterList(names, name=None, namespace=None):
    for i in FQNamesToIterList(names):
        if ((name and i[0].find(name) >= 0) or
            (namespace and i[1].find(namespace) >= 0)):
            yield i


def FQNamesToDict(names):
    '''
        Takes a list of fully qualified names and turns it into a dict
        Where the object names are the keys.
        (note: dunno if this more useful than the plain dict() method.)
    '''
    return dict(FQNamesToIterList(names))


def JSONImplementsOneOf(json_obj, obj_types):
    try:
        return not JSONImplementedType(json_obj, obj_types) == None
    except:
        return False


def JSONImplementedType(json_obj, obj_types):
    '''
        Here we determine if our JSON request payload implements an object
        contained within a set of implemented object types.

        I think this is a good place to implement our schema validators,
        but for right now let's just validate that it refers to an object
        type that is implementable.
        The convention we will use is this:
        - Our JSON will be a dictionary
        - This dictionary will contain a key called 'obj_type'
        - Key 'obj_type' will be in the format '<namespace>.<object_name>',
          where:
            - <namespace> refers to the python module namespace where
              the python class definition lives.
            - <object_name> refers to the name of the python class that
              implements the object.
        - This is not currently enforced, but It is understood that all
          other keys of the dictionary will conform to the referred object's
          construction method(s)

        :param json_obj: JSON payload
        :param obj_types: list of fully qualified object names.
    '''
    if not type(json_obj) == dict:
        raise ValueError('JSON needs to be a dict')

    if not 'obj_type' in json_obj:
        raise ValueError('JSON object needs to contain an obj_type')

    name, scope = FQNameToNameAndScope(json_obj['obj_type'])
    if name in FQNamesToDict(obj_types):
        return PyClassFromName(json_obj['obj_type'])

    return None


def PyClassFromName(fully_qualified_name):
    name, scope = FQNameToNameAndScope(fully_qualified_name)
    my_module = __import__(scope, globals(), locals(), [str(name)], -1)
    return getattr(my_module, name)

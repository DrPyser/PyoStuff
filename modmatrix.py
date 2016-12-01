#from pyo import *

def find(pred, lst):
    for i in range(len(lst)):
        if pred(lst[i]):
            return i
    else:
        return None

class ModMatrix(object):
    """Modulation matrix. Interface to manage a complex network of 
    signal souces and destinations, i.e. signal generators which can modulate
    the parameters of other objects, or themselves be modulated by other signal generators,
    and sometimes both at the same time. A ModMatrix instance allows for a centralised way to
    manage such a network, and offers an abstraction for "linking" objects
    (i.e. setting one as a modulation source for the parameter of another),
    and then for "unlinking" them(i.e. returning the modulated parameters to their previous value and
    unregistering the link). Also offers methods to query the ModMatrix instance for information about which object
    modulate which parameter of which other object.
    Also offers a textual representation of the modulation matrix, 
    which is more compact and easier to read than the code of a whole program"""
    def __init__(self, objects=None):
        self._links = []
        if objects is not None:
            self._namespace = dict(objects)
        else:
            self._namespace = {}

    def add(self, name, object):
        """Add object to namespace. If 'name' already in namespace,
        raise an exception
        
        name : string, name of object to add

        object : PyoObject, signal generator 
        that can be a source or a destination for modulation"""
        
        if name in self._namespace:
            raise Exception("Cannot register '%s', name already in namespace."%(name))
        else:
            self._namespace[name] = object

    def remove(self, name):
        if name not in self._namespace:
            raise Exception("Cannot remove '%s', name not in namespace"%(name))
        else:
            self.unlinkAll(name)
            self.retire(name)
            del self._namespace[name]

    def __getitem__(self,key):
        return self._namespace[key]

    def __setitem__(self, key, value):
        self.remove(key)
        self.add(key, value)

    def __delitem__(self,key):
        self.remove(key)

    def __iter__(self):
        return iter(self._namespace)

    def iterkeys(self):
        return iter(self._namespace)

    def __contains__(self, item):
        return item in self._namespace
        
        
    def link(self, src, dest, parameter):
        """Set a source to modulation a parameter of a destination,
        saving the previous value and registering the link.

        src : string, name in namespace.

        dest : string, name in namespace.

        parameter : string, name of parameter of 'src' object."""
        if not (src in self._namespace and dest in self._namespace):
            raise Exception("There is no entry '%s' in this modulatio matrix."%(src if src in self._matrix else dest))
        else:
            src_ref, dest_ref = self._namespace[src], self._namespace[dest]
            if not hasattr(dest_ref,parameter):
                raise Exception("Invalid attribute '%s' for object %s"%(parameter, dest))
            else:
                self.unlink(dest, parameter) # undo previous links to this destination and parameter
                #We add an entry into the table: (source, destination, parameter, old_value)
                self._links.append((src, dest, parameter, getattr(dest_ref, parameter)))
                setattr(dest_ref, parameter, src_ref)
        
    def unlink(self, dest, parameter):
        """Remove modulation on a specific parameter for an object in the matrix,
        returning the parameter to its previous value.

        dest : string, name in namespace.
        
        parameter : string, name of parameter of the 'dest' object."""
        
        if dest not in self._namespace:
            raise Exception("No entry %s in namespace"%(dest))
        elif not hasattr(self._namespace[dest],parameter):
            raise Exception("No parameter %s for object %s"%(parameter, dest))
        elif self.isModulated(dest, parameter):
            pos = next(self._getIndices(dest=dest, parameter=parameter))
            src, dest, parameter, prev = self._links.pop(pos)
            setattr(self._namespace[dest], parameter, prev) # set parameter of 'dest' to previous value

    def unlinkAll(self, dest):
        """Remove all modulations on the object 'dest' from this matrix,
        returning each parameter to their previous value.
        
        dest : string, name in namespace."""
        if dest not in self._namespace:
            raise Exception("No entry %s in namespace"%(dest))
        else:
            offset = 0
            for i in self._getIndices(dest=dest):
                src, dest, parameter, prev = self._links.pop(i-offset)
                setattr(self._namespace[dest], parameter, prev) # set parameter of 'dest' to previous value
                offset += 1

    def retire(self, src):
        """Remove all modulation destinations for source."""
        if src not in self._namespace:
            raise Exception("No entry %s in namespace"%(src))
        else:
            offset = 0
            for i in self._getIndices(src=src):
                src, dest, parameter, prev = self._links.pop(i-offset)
                setattr(self._namespace[dest], parameter, prev) # set parameter of 'dest' to previous value
                offset += 1
        
    def _getIndices(self, src=None, dest=None, parameter=None):
        if src is None and dest is None and parameter is None:
            return iter(self._links)
        elif src is None:
            if dest is None:
                return (i for i in range(len(self._links)) if self._links[i][2] == parameter)
            elif parameter is None:
                return (i for i in range(len(self._links)) if self._links[i][1] == dest)
            else:
                return (i for i in range(len(self._links)) if self._links[i][1] == dest and self._links[i][2] == parameter)
        elif dest is None:
            if parameter is None:
                return (i for i in range(len(self._links)) if self._links[i][0] == src)
            else:
                return (i for i in range(len(self._links)) if self._links[i][0] == src and self._links[i][2] == parameter)
        elif parameter is None:
            return (i for i in range(len(self._links)) if self._links[i][0] == src and self._links[i][1] == dest)
        else:
            return (i for i in range(len(self._links)) if self._links[i][0] == src and self._links[i][1] == dest and self._links[i][2] == parameter)

    def getEntries(self, src=None, dest=None, parameter=None):
        return map(lambda x:self._links[x], self._getIndices(src=src, dest=dest, parameter=parameter))

    def isModulated(self, dest, parameter):
        return len(tuple(self._getIndices(dest=dest, parameter=parameter))) > 0
    
    def __str__(self):
        def source_repr(src):
            dests = set(map(lambda x:(x[1], x[2]), self.getEntries(src=src)))
            if len(dests) == 0:
                yield ""
            else:
                for (dest, param) in dests:
                    yield "%s(%s)"%(dest, param)
                
        def dest_repr(dest):
            srcs = set(map(lambda x:(x[0], x[2]), self.getEntries(dest=dest)))
            if len(srcs) == 0:
                yield ""
            else:
                for (src, param) in srcs:
                    yield "%s(%s)"%(src, param)
        def entry():
            if len(self._namespace) == 0:
                yield "Nothing"
            else:
                for obj in self._namespace:
                    yield "%s : %s\n\tsource for: %s\n\n\tdestination for: %s"%(obj, str(self._namespace[obj]),
                                                                                ", ".join(source_repr(obj)),
                                                                                ", ".join(dest_repr(obj)))
        return "\n\n".join(entry())
                

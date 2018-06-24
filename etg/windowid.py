#---------------------------------------------------------------------------
# Name:        etg/windowid.py
# Author:      Robin Dunn
#
# Created:     15-Nov-2010
# Copyright:   (c) 2010-2018 by Total Control Software
# License:     wxWindows License
#---------------------------------------------------------------------------

import etgtools
import etgtools.tweaker_tools as tools
from etgtools import ClassDef, MethodDef, ParamDef

PACKAGE   = "wx"
MODULE    = "_core"
NAME      = "windowid"   # Base name of the file to generate to for this script
DOCSTRING = ""

# The classes and/or the basename of the Doxygen XML files to be processed by
# this script.
ITEMS  = [ 'wxIdManager' ]

#---------------------------------------------------------------------------

def run():
    # Parse the XML file(s) building a collection of Extractor objects
    module = etgtools.ModuleDef(PACKAGE, MODULE, NAME, DOCSTRING)
    etgtools.parseDoxyXML(module, ITEMS)

    #-----------------------------------------------------------------
    # Tweak the parsed meta objects in the module object as needed for
    # customizing the generated code and docstrings.

    c = module.find('wxIdManager')
    assert isinstance(c, etgtools.ClassDef)
    # no tweaks needed for this class


    # wxWindowIDRef is not documented (and probably rightly so) but we're going
    # to use it from Python anyway to help with preallocating IDs in a way that
    # allows them to be reused and be also be protected from conflicts from
    # other auto allocated IDs.

    # First, add defintions of the existing C++ class and its elements
    klass = ClassDef(name='wxWindowIDRef', bases = [],
        briefDoc="""\
            A wxWindowIDRef object wraps an ID value and marks it as being in-use until all references to that ID are gone.
            """,
        items = [
            MethodDef(name='wxWindowIDRef', className='wxWindowIDRef', isCtor=True,
                briefDoc='Default constructor',
                overloads=[
                MethodDef(name='wxWindowIDRef', className='wxWindowIDRef', isCtor=True,
                    briefDoc='Create reference from an ID',
                    items=[ ParamDef(type='int', name='id') ]),
                
                MethodDef(name='wxWindowIDRef', className='wxWindowIDRef', isCtor=True,
                    briefDoc='Copy an ID reference',
                    items=[ ParamDef(type='const wxWindowIDRef&', name='idref') ]),
                ]),
            
            MethodDef(name='~wxWindowIDRef', className='wxWindowIDRef', isDtor=True),

            MethodDef(type='int', name='GetValue',
                briefDoc='Get the ID value'),
        ])

    # Now tweak it a bit
    klass.addCppMethod('int', 'GetId', '()',
        doc="Alias for GetValue allowing the IDRef to be passed as the source parameter to :meth:`wx.EvtHandler.Bind`.",
        body="""\
            return self->GetValue();
            """)


    klass.addCppMethod('int', '__int__', '()',
        doc="Alias for GetValue allowing the IDRef to be passed as the WindowID parameter when creating widgets or etc.",
        body="""\
            return self->GetValue();
            """)

    klass.addPyMethod('__repr__', '(self)', 'return "WindowIDRef: {}".format(self.GetId())')

    # and finish it up by adding it to the module
    module.addItem(klass)

    # Now, let's add a new Python function to the global scope that reserves an 
    # ID (or range) and returns a ref object for it. 
    module.addPyFunction('NewIdRef', '(count=1)', 
        doc="""\
            Reserves a new Window ID (or range of WindowIDs) and returns a 
            :class:`wx.WindowIDRef` object (or list of them) that will help 
            manage the reservation of that ID.

            This function is intended to be a drop-in replacement of the old 
            and deprecated :func:`wxNewId` function.
            """,
        body="""\
            if count == 1:
                return WindowIDRef(IdManager.ReserveId())
            else:
                start = IdManager.ReserveId(count)
                IDRefs = []
                for id in range(start, start+count):
                    IDRefs.append(WindowIDRef(id))
                return IDRefs
            """)

    #-----------------------------------------------------------------
    tools.doCommonTweaks(module)
    tools.runGenerators(module)


#---------------------------------------------------------------------------
if __name__ == '__main__':
    run()


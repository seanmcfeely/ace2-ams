from __future__ import annotations
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules
from pydantic import BaseModel, Field
import re
import sys

def find(name:str, base:type) -> dict:
    ''' finds all subclasses of base in module (not recursive)

    Args:
        name (str): the name of the module we are importing from
        base (type): the base class to search for subclasses of

    Returns:
        dict: a mapping of attribute name to attribute of the found subclasses
    '''

    subclasses = {}
    module = sys.modules[name]
    package_dir = Path(module.__file__).resolve().parent
    for (_, module_name, _) in iter_modules([package_dir]):
        sub_module = import_module(f"{module.__name__}.{module_name}")
        for attribute_name in dir(sub_module):
            attribute = getattr(sub_module, attribute_name)
            if isclass(attribute) and attribute != base and issubclass(attribute, base):
                subclasses[attribute_name] = attribute
    return subclasses

class Private():
    ''' container class for model's private attributes '''

    def __getattr__(self, name):
        ''' changes get attribute behavior to return None if the attribute does not exist

        Args:
            name (str): the name of the attribute to get
        '''

        # return the attribute if it exists
        if name in self.__dict__:
            return self.__dict__[name]

        # return None if the attribute does not exist
        return None

class PrivateModel(BaseModel):
    ''' BaseModel with a private attribute for storing private attributes '''

    # pydantic uses some thing called slots to have attributes that are not in the model
    __slots__ = ('private',)

    def __init__(self, **kwargs):
        ''' initializes the Model with a private attribute for storing private attributes '''

        # init the model
        super().__init__(**kwargs)

        # add the private attribute for storing private attributes
        object.__setattr__(self, 'private', Private())

model_types = {}
class TypedModel(PrivateModel):
    ''' Model class that allows for polymorphic subclass loading '''

    type: str = Field(description='the type string used to identify sub types')

    def __new__(cls, type:str, *args, **kwargs):
        ''' Uses type to construct the correct subclass if one is registered, otherwise constructs the current class

        Args:
            type (str): the type string to lookup the subclass with

        Returns:
            cls: an instantiated cls object
        '''

        # get the subclass from the mapping via type string
        # use current class if no subclass is registered for this type string
        cls = model_types.get(cls.__name__, {}).get(type, cls)

        # construct an instance of the desired class
        return super().__new__(cls)

    def __init_subclass__(cls):
        ''' maps all subclasses using the type value so they can be found when constructing new instances
        
        Args:
            cls (type): the subclass to init
        '''

        # find the base type
        base = TypedModel.get_base_type(cls)

        # skip type registration if this is the base class
        if base == cls:
            return

        # use the class name as the type
        cls.type = cls.__name__

        # add a mapping dictionary for this base type if it does not already exist
        if base.__name__ not in model_types:
            model_types[base.__name__] = {}

        # map subclass to the type string but with a constructor that we can use for loading from a dict
        model_types[base.__name__][cls.type] = type(
            cls.__name__,
            (cls,), 
            {
                '__init__': base.__init__,
                '__init_subclass__': lambda x : None, # NOTE: prevents infinite recursion loop registering new class
            }
        )

    @classmethod
    def get_base_type(cls, target):
        ''' recursviely walks the base classes to find the base model that subclasses TypeModel

        Args:
            target (type): the class to find the base model for

        Returns:
            type: the base class that subclasses TypeModel
        '''
        for base in target.__bases__:
            if base == TypedModel:
                return target
            base = cls.get_base_type(base)
            if base:
                return base
        return None

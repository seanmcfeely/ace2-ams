from __future__ import annotations
from pydantic import BaseModel, Field
import re

camel_case = re.compile(r'([a-z0-9])([A-Z])')

model_types = {}

class TypedModel(BaseModel):
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

        # generate type for this class
        cls.type = cls.get_type_string()

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
    def get_type_string(cls) -> str:
        ''' converts class name from camel case to snake case 

        Returns:
            str: class name in snake case
        '''

        return camel_case.sub(r'\1_\2', cls.__name__).lower()

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

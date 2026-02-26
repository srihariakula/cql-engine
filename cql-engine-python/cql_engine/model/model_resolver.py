"""
Model resolver interface for CQL engine.

Provides support for mapping logical models (e.g., QDM or FHIR) onto Python implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class ModelResolver(ABC):
    """
    A ModelResolver provides support for mapping a logical model (e.g. QDM or FHIR)
    onto a Python implementation of that model.

    Different implementations of the same model might map to different implementation
    schemes with the simplest example being classes in different package names, but also
    possibly with different property naming schemes, etc.
    """

    @abstractmethod
    def get_package_name(self) -> str:
        """
        Deprecated: Use get_package_names() instead.

        Returns:
            The package name
        """
        pass

    @abstractmethod
    def set_package_name(self, package_name: str) -> None:
        """
        Deprecated: Use set_package_names() instead.

        Args:
            package_name: The package name to set
        """
        pass

    def get_package_names(self) -> List[str]:
        """
        Return the package names of Python objects supported by this model.

        Default implementation returns a single-element list containing get_package_name().

        Returns:
            List of Python package names for model objects that support this model
        """
        return [self.get_package_name()]

    def set_package_names(self, package_names: List[str]) -> None:
        """
        Set the package names of Python objects supported by this model.

        Default implementation is a no-op to provide backwards compatibility for models
        that implement a single package name and still use get/set_package_name methods.

        Args:
            package_names: List of Python package names for model objects
        """
        pass

    @abstractmethod
    def resolve_path(self, target: object, path: str) -> object:
        """
        Resolve the provided path expression for the provided target.

        Paths can be things like simple dotted property notation (e.g. Patient.id)
        or more complex things like list indexed property expressions (e.g. Patient.name[0].given).
        The exact details are configured in the model definition.

        Args:
            target: The target object to resolve the path on
            path: The path expression

        Returns:
            Result of the provided expression. None is expected whenever a path doesn't exist on the target.
        """
        pass

    @abstractmethod
    def get_context_path(self, context_type: str, target_type: str) -> object:
        """
        Get the path expression that expresses the relationship between the targetType and the given contextType.

        For example, in a FHIR model, with context type "Patient" and targetType "Condition",
        the resulting path is "subject" because that is the model property on the Condition object
        that links the Condition to the Patient.

        Args:
            context_type: The context type
            target_type: The target type

        Returns:
            The path expression linking context to target
        """
        pass

    @abstractmethod
    def resolve_type(self, value_or_name) -> type:
        """
        Resolve the Python class that corresponds to the given model type or object instance.

        Can be called with either a string type name or an object instance.

        Args:
            value_or_name: Model type name (string) or object instance.
                          Type names are namespaced in the ELM (e.g. FHIR.Patient),
                          but the namespace is removed prior to calling this method.

        Returns:
            Type object that represents the specified model type or object's type
        """
        pass

    @abstractmethod
    def is_instance(self, value: object, type_: type) -> Optional[bool]:
        """
        Check whether or not a specified value instance is of the specified type.

        Args:
            value: The value to check
            type_: The type to check against

        Returns:
            True when the value is of the specified type, False otherwise, None if value is None
        """
        pass

    @abstractmethod
    def as_type(self, value: object, type_: type, is_strict: bool = False) -> object:
        """
        Cast the specified value to the specified type.

        When type conversion is not possible, None should be returned unless the is_strict
        flag is set to True wherein an Exception will be thrown.

        Args:
            value: Model object instance
            type_: Type to which the value should be cast
            is_strict: Flag indicating how to handle invalid type conversion

        Returns:
            The result of the value conversion or None if conversion is not possible
        """
        pass

    @abstractmethod
    def create_instance(self, type_name: str) -> object:
        """
        Create an instance of the model object that corresponds to the specified type.

        Args:
            type_name: Model type to create

        Returns:
            New instance of the specified model type
        """
        pass

    @abstractmethod
    def set_value(self, target: object, path: str, value: object) -> None:
        """
        Set the value of a particular property on the given model object.

        Args:
            target: Model object
            path: Path to the property that will be set
            value: Value to set to the property indicated by the path expression
        """
        pass

    @abstractmethod
    def object_equal(self, left: object, right: object) -> Optional[bool]:
        """
        Compare two objects for equality.

        Args:
            left: Left hand side of the equality expression
            right: Right hand side of the equality expression

        Returns:
            Flag indicating whether the objects are equal
        """
        pass

    @abstractmethod
    def object_equivalent(self, left: object, right: object) -> Optional[bool]:
        """
        Compare two objects for equivalence.

        Args:
            left: Left hand side of the equivalence expression
            right: Right hand side of the equivalence expression

        Returns:
            Flag indicating whether the objects are equivalent
        """
        pass

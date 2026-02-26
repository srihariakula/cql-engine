"""
System data provider for CQL runtime types.

Provides model resolution for system CQL types like DateTime, Date, Time, Interval, etc.
"""

from typing import Iterable, List, Optional, Any
from decimal import Decimal
from cql_engine.model.base_model_resolver import BaseModelResolver
from cql_engine.data.data_provider import DataProvider
from cql_engine.runtime.code import Code
from cql_engine.runtime.interval import Interval
from cql_engine.runtime.quantity import Quantity
from cql_engine.runtime.date import Date
from cql_engine.runtime.datetime import DateTime
from cql_engine.runtime.time import Time
from cql_engine.runtime.tuple import Tuple
from cql_engine.runtime.cql_type import CqlType


class SystemDataProvider(BaseModelResolver, DataProvider):
    """
    A DataProvider for the CQL system types defined in the org.opencds.cqf.cql.engine.runtime package.

    Provides model resolution for built-in CQL types and system data types.
    Does not support data retrieval.
    """

    def retrieve(
        self,
        context: str,
        context_path: Optional[str],
        context_value: object,
        data_type: str,
        template_id: Optional[str],
        code_path: Optional[str],
        codes: Optional[Iterable[Code]],
        value_set: Optional[str],
        date_path: Optional[str],
        date_low_path: Optional[str],
        date_high_path: Optional[str],
        date_range: Optional[Interval]
    ) -> Iterable[object]:
        """
        Retrieval is not supported by the SystemDataProvider.

        Raises:
            ValueError: Always raised as system provider does not support retrieval
        """
        raise ValueError("SystemDataProvider does not support retrieval.")

    def get_package_name(self) -> str:
        """Deprecated: Use get_package_names() instead."""
        return "org.opencds.cqf.cql.engine.runtime"

    def set_package_name(self, package_name: str) -> None:
        """Deprecated: Use set_package_names() instead."""
        pass  # No-op for system provider

    def get_property(self, clazz: type, path: str) -> Any:
        """
        Get a property from a class using reflection.

        Args:
            clazz: The class to get the property from
            path: The property name

        Returns:
            The property descriptor

        Raises:
            ValueError: If property cannot be found
        """
        try:
            return getattr(clazz, path)
        except AttributeError:
            # Check base classes
            for base in clazz.__mro__[1:]:
                if hasattr(base, path):
                    return getattr(base, path)
            raise ValueError(
                f"Could not determine field for path {path} of type {clazz.__name__}"
            )

    def get_read_accessor(self, clazz: type, path: str) -> Optional[callable]:
        """
        Get a getter method for a property.

        Args:
            clazz: The class to get the accessor from
            path: The property name

        Returns:
            The getter method or None if not found
        """
        accessor_method_name = f"get_{path}"
        if hasattr(clazz, accessor_method_name):
            return getattr(clazz, accessor_method_name)

        # Try property
        if hasattr(clazz, path):
            attr = getattr(clazz, path)
            if isinstance(attr, property):
                return attr.fget
        return None

    def get_write_accessor(self, clazz: type, path: str) -> Optional[callable]:
        """
        Get a setter method for a property.

        Args:
            clazz: The class to set the accessor on
            path: The property name

        Returns:
            The setter method or None if not found

        Raises:
            ValueError: If no setter can be found
        """
        accessor_method_name = f"set_{path}"
        if hasattr(clazz, accessor_method_name):
            return getattr(clazz, accessor_method_name)

        # Try property setter
        if hasattr(clazz, path):
            attr = getattr(clazz, path)
            if isinstance(attr, property) and attr.fset:
                return attr.fset

        raise ValueError(
            f"Could not determine accessor function for property {path} of type {clazz.__name__}"
        )

    def resolve_path(self, target: object, path: str) -> object:
        """
        Resolve the provided path expression for the provided target.

        Args:
            target: The object to resolve the path on
            path: The path expression

        Returns:
            The resolved value or None if path doesn't exist
        """
        if target is None:
            return None

        if isinstance(target, Tuple):
            return target.get_element(path)

        clazz = type(target)
        accessor = self.get_read_accessor(clazz, path)
        if accessor is None:
            return None

        try:
            if callable(accessor):
                return accessor(target)
            else:
                return accessor
        except Exception as e:
            raise ValueError(
                f"Errors occurred attempting to invoke the accessor function for property {path} of type {clazz.__name__}: {str(e)}"
            )

    def set_value(self, target: object, path: str, value: object) -> None:
        """
        Set the value of a particular property on the given model object.

        Args:
            target: The object to set the value on
            path: The property path
            value: The value to set

        Raises:
            ValueError: If setter cannot be invoked
        """
        if target is None:
            return

        clazz = type(target)
        accessor = self.get_write_accessor(clazz, path)
        try:
            if callable(accessor):
                accessor(target, value)
            else:
                setattr(target, path, value)
        except Exception as e:
            raise ValueError(
                f"Errors occurred attempting to invoke the accessor function for property {path} of type {clazz.__name__}: {str(e)}"
            )

    def resolve_type(self, value_or_name) -> type:
        """
        Resolve the Python type that corresponds to the given model type or object.

        Args:
            value_or_name: Either a type name string or an object instance

        Returns:
            The corresponding Python type

        Raises:
            ValueError: If type cannot be resolved
        """
        if isinstance(value_or_name, str):
            type_name = value_or_name
            type_map = {
                "Boolean": bool,
                "Integer": int,
                "Decimal": Decimal,
                "String": str,
                "Quantity": Quantity,
                "Interval": Interval,
                "Long": int,
                "Tuple": Tuple,
                "DateTime": DateTime,
                "Date": Date,
                "Time": Time,
            }

            if type_name in type_map:
                return type_map[type_name]

            # Try to import from runtime package
            try:
                module_name = f"cql_engine.runtime.{type_name.lower()}"
                module = __import__(module_name, fromlist=[type_name])
                return getattr(module, type_name)
            except (ImportError, AttributeError):
                raise ValueError(
                    f"Could not resolve type {self.get_package_name()}.{type_name}."
                )
        else:
            # Object instance
            if value_or_name is None:
                return object
            return type(value_or_name)

    def create_instance(self, type_name: str) -> object:
        """
        Create an instance of the model object that corresponds to the specified type.

        Args:
            type_name: The name of the type to instantiate

        Returns:
            A new instance of the specified type

        Raises:
            ValueError: If instance cannot be created
        """
        clazz = self.resolve_type(type_name)
        try:
            return clazz()
        except Exception as e:
            raise ValueError(
                f"Could not create an instance of class {clazz.__name__}: {str(e)}"
            )

    def object_equal(self, left: object, right: object) -> Optional[bool]:
        """
        Compare two objects for equality.

        Args:
            left: Left operand
            right: Right operand

        Returns:
            True if equal, False if not, None if either is None
        """
        if left is None:
            return None
        if right is None:
            return None
        return left == right

    def object_equivalent(self, left: object, right: object) -> Optional[bool]:
        """
        Compare two objects for equivalence.

        Uses CqlType.equivalent() if available, otherwise falls back to equality.

        Args:
            left: Left operand
            right: Right operand

        Returns:
            True if equivalent, False if not
        """
        if left is None and right is None:
            return True
        if left is None:
            return False

        if isinstance(left, CqlType):
            return left.equivalent(right)

        return left == right

    def get_context_path(self, context_type: str, target_type: str) -> object:
        """Get the path expression that expresses the relationship between types."""
        return None

"""Abstract base class for FHIR model resolution."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Set
from datetime import datetime, date
from calendar import Calendar
from zoneinfo import ZoneInfo

# Placeholder for CQL engine runtime types
# from cql_engine.runtime import Date, DateTime, Time, BaseTemporal, Interval, Code, Concept


class FhirModelResolver(ABC):
    """Abstract base class for FHIR version-specific model resolution.

    Handles:
    - Type resolution and class creation
    - Property access and mutation
    - Path resolution for nested elements
    - Temporal type conversions
    - FHIR-to-CQL type conversions
    """

    def __init__(self, fhir_context: Any) -> None:
        """Initialize the model resolver.

        Args:
            fhir_context: FHIR context providing type definitions
        """
        self.fhir_context = fhir_context
        self.package_names: List[str] = []
        self.initialize()

    @abstractmethod
    def initialize(self) -> None:
        """Initialize version-specific type handling.

        Subclasses should set up package names and register custom types.
        """
        pass

    @abstractmethod
    def _equals_deep(self, left: Any, right: Any) -> bool:
        """Deep equality comparison for FHIR types.

        Args:
            left: First value
            right: Second value

        Returns:
            True if values are deeply equal
        """
        pass

    def get_fhir_context(self) -> Any:
        """Get the FHIR context.

        Returns:
            The FHIR context
        """
        return self.fhir_context

    def get_package_names(self) -> List[str]:
        """Get package names to search for types.

        Returns:
            List of package names
        """
        return self.package_names

    def set_package_names(self, package_names: List[str]) -> None:
        """Set package names to search for types.

        Args:
            package_names: List of package names
        """
        self.package_names = package_names

    def resolve_type(self, type_name: str) -> Optional[type]:
        """Resolve a type name to a Python class.

        Args:
            type_name: Name of the type to resolve

        Returns:
            The resolved type class, or None if not found
        """
        if not type_name:
            return None

        # Remove FHIR prefix if present
        if type_name.startswith("FHIR."):
            type_name = type_name[5:]

        # Try to get from FHIR context
        try:
            element_def = self.fhir_context.get_element_definition(type_name)
            if element_def:
                return element_def.get_implementing_class()
        except Exception:
            pass

        # Try resource definitions
        try:
            resource_def = self.fhir_context.get_resource_definition(type_name)
            if resource_def:
                return resource_def.get_implementing_class()
        except Exception:
            pass

        # Try package imports
        for package_name in self.package_names:
            try:
                return self._import_class(f"{package_name}.{type_name}")
            except (ImportError, AttributeError):
                pass

        # Try Enumerations
        for package_name in self.package_names:
            try:
                enum_class = self._import_class(
                    f"{package_name}.Enumerations.{type_name}"
                )
                return enum_class
            except (ImportError, AttributeError):
                pass

        return None

    def resolve_type_of_value(self, value: Any) -> Optional[type]:
        """Resolve the type of a value.

        Args:
            value: The value

        Returns:
            The type of the value
        """
        if value is None:
            return type(None)

        return type(value)

    def create_instance(self, type_name: str) -> Any:
        """Create an instance of a type by name.

        Args:
            type_name: Type name

        Returns:
            New instance of the type

        Raises:
            TypeError: If instance cannot be created
        """
        type_class = self.resolve_type(type_name)
        if not type_class:
            raise TypeError(f"Could not resolve type {type_name}")

        return self.create_instance_of_class(type_class)

    def create_instance_of_class(self, type_class: type) -> Any:
        """Create an instance of a class.

        Args:
            type_class: The class

        Returns:
            New instance

        Raises:
            TypeError: If instance cannot be created
        """
        try:
            return type_class()
        except Exception as e:
            raise TypeError(f"Could not create instance of {type_class}: {str(e)}")

    def resolve_path(self, target: Any, path: str) -> Any:
        """Resolve a dot-separated path in an object.

        Args:
            target: Target object
            path: Path to resolve (e.g., "patient.name.given[0]")

        Returns:
            Value at the path, or None if not found
        """
        if not target or not path:
            return None

        identifiers = path.split(".")

        for identifier in identifiers:
            if not target:
                break

            # Handle array indexing: item[0].code
            if "[" in identifier:
                bracket_idx = identifier.index("[")
                prop_name = identifier[:bracket_idx]
                index = int(identifier[bracket_idx + 1])

                target = self.resolve_property(target, prop_name)
                if isinstance(target, (list, tuple)):
                    target = target[index]
            else:
                target = self.resolve_property(target, identifier)

        return target

    def resolve_property(self, target: Any, path: str) -> Any:
        """Resolve a single property in an object.

        Args:
            target: Target object
            path: Property name

        Returns:
            Property value, or None if not found
        """
        if not target:
            return None

        # Try attribute access
        if hasattr(target, path):
            return getattr(target, path)

        # Try get method
        if hasattr(target, "get"):
            try:
                return target.get(path)
            except (KeyError, TypeError):
                pass

        # Try indexed access for arrays
        if isinstance(target, (list, tuple)):
            try:
                return target[int(path)]
            except (ValueError, IndexError):
                pass

        return None

    def set_value(self, target: Any, path: str, value: Any) -> None:
        """Set a value in an object.

        Args:
            target: Target object
            path: Property path
            value: Value to set
        """
        if not target or not path:
            return

        # Try direct attribute setting
        if hasattr(target, path):
            setattr(target, path, value)
            return

        # Try set method
        if hasattr(target, "set"):
            try:
                target.set(path, value)
                return
            except (KeyError, TypeError):
                pass

    def object_equal(self, left: Any, right: Any) -> Optional[bool]:
        """Test equality of two objects.

        Args:
            left: First value
            right: Second value

        Returns:
            True if equal, False if not equal, None if incomparable
        """
        if left is None:
            return None
        if right is None:
            return None

        return self._equals_deep(left, right)

    def object_equivalent(self, left: Any, right: Any) -> bool:
        """Test equivalence of two objects.

        Args:
            left: First value
            right: Second value

        Returns:
            True if equivalent
        """
        if left is None and right is None:
            return True
        if left is None or right is None:
            return False

        return self._equals_deep(left, right)

    def get_context_path(
        self, context_type: Optional[str], target_type: Optional[str]
    ) -> Optional[str]:
        """Get the path from context type to target type.

        Args:
            context_type: Source type
            target_type: Target type

        Returns:
            Path from source to target, or None if not found
        """
        if not target_type or not context_type:
            return None

        # Special context types that have no path
        if context_type in ("Unfiltered", "Unspecified", "Population"):
            return None

        # Same type uses ID
        if context_type == target_type:
            return "id"

        # Would need to traverse type hierarchy
        # This is a simplified implementation
        return None

    @staticmethod
    def _import_class(fully_qualified_name: str) -> type:
        """Import a class by fully qualified name.

        Args:
            fully_qualified_name: Module.Class name

        Returns:
            The class

        Raises:
            ImportError: If class cannot be imported
        """
        parts = fully_qualified_name.rsplit(".", 1)
        if len(parts) != 2:
            raise ImportError(f"Invalid class name: {fully_qualified_name}")

        module_name, class_name = parts
        try:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(
                f"Cannot import {fully_qualified_name}: {str(e)}"
            )

"""
Composite data provider that delegates to separate model and retrieve providers.
"""

from typing import Iterable, List, Optional
from cql_engine.data.data_provider import DataProvider
from cql_engine.model.model_resolver import ModelResolver
from cql_engine.retrieve.retrieve_provider import RetrieveProvider
from cql_engine.runtime.code import Code
from cql_engine.runtime.interval import Interval


class CompositeDataProvider(DataProvider):
    """
    A DataProvider that delegates to separate ModelResolver and RetrieveProvider implementations.

    This allows composition of different model and retrieve implementations
    into a single unified data provider.
    """

    def __init__(self, model_resolver: ModelResolver, retrieve_provider: RetrieveProvider):
        """
        Initialize with a model resolver and retrieve provider.

        Args:
            model_resolver: The ModelResolver to use for model operations
            retrieve_provider: The RetrieveProvider to use for data retrieval
        """
        self.model_resolver = model_resolver
        self.retrieve_provider = retrieve_provider

    def get_package_name(self) -> str:
        """Deprecated: Use get_package_names() instead."""
        return self.model_resolver.get_package_name()

    def set_package_name(self, package_name: str) -> None:
        """Deprecated: Use set_package_names() instead."""
        self.model_resolver.set_package_name(package_name)

    def get_package_names(self) -> List[str]:
        """Get the package names of Java objects supported by this model."""
        return self.model_resolver.get_package_names()

    def set_package_names(self, package_names: List[str]) -> None:
        """Set the package names of Java objects supported by this model."""
        self.model_resolver.set_package_names(package_names)

    def resolve_path(self, target: object, path: str) -> object:
        """Resolve the provided path expression for the provided target."""
        return self.model_resolver.resolve_path(target, path)

    def get_context_path(self, context_type: str, target_type: str) -> object:
        """Get the path expression that expresses the relationship between types."""
        return self.model_resolver.get_context_path(context_type, target_type)

    def resolve_type(self, value_or_name) -> type:
        """Resolve the Java class that corresponds to the given model type or object."""
        if isinstance(value_or_name, str):
            return self.model_resolver.resolve_type(value_or_name)
        else:
            return self.model_resolver.resolve_type(value_or_name)

    def is_instance(self, value: object, type_: type) -> Optional[bool]:
        """Check whether or not a specified value instance is of the specified type."""
        return self.model_resolver.is_instance(value, type_)

    def as_type(self, value: object, type_: type, is_strict: bool = False) -> object:
        """Cast the specified value to the specified type."""
        return self.model_resolver.as_type(value, type_, is_strict)

    def create_instance(self, type_name: str) -> object:
        """Create an instance of the model object that corresponds to the specified type."""
        return self.model_resolver.create_instance(type_name)

    def set_value(self, target: object, path: str, value: object) -> None:
        """Set the value of a particular property on the given model object."""
        self.model_resolver.set_value(target, path, value)

    def object_equal(self, left: object, right: object) -> Optional[bool]:
        """Compare two objects for equality."""
        return self.model_resolver.object_equal(left, right)

    def object_equivalent(self, left: object, right: object) -> Optional[bool]:
        """Compare two objects for equivalence."""
        return self.model_resolver.object_equivalent(left, right)

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
        """Retrieve data based on specified criteria."""
        return self.retrieve_provider.retrieve(
            context, context_path, context_value, data_type, template_id,
            code_path, codes, value_set, date_path, date_low_path, date_high_path, date_range
        )

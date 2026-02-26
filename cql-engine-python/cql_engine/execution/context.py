"""
Evaluation context for CQL engine.

Thread-affine execution context that tracks state during CQL library evaluation.
"""

from typing import Dict, List, Optional, Set, Stack as StackType, Any
from datetime import datetime, timezone, timedelta
from collections import OrderedDict
from cql_engine.execution.library_loader import LibraryLoader, VersionedIdentifier, Library
from cql_engine.execution.variable import Variable
from cql_engine.execution.expression_result import ExpressionResult
from cql_engine.execution.namespace_helper import NamespaceHelper
from cql_engine.data.data_provider import DataProvider
from cql_engine.data.system_data_provider import SystemDataProvider
from cql_engine.data.external_function_provider import ExternalFunctionProvider
from cql_engine.terminology.terminology_provider import TerminologyProvider


class CqlException(Exception):
    """Exception raised during CQL execution."""
    pass


class Context:
    """
    Thread-affine evaluation context for CQL expression evaluation.

    Maintains the state necessary for evaluating CQL expressions including
    libraries, data providers, parameters, variables, and expression caches.

    NOTE: This class uses Python's threading.local equivalent concept where needed,
    but is not strictly thread-local as Python's design differs from Java.
    """

    # Shared UCUM service
    _shared_ucum_service = None

    def __init__(
        self,
        library: Library,
        evaluation_datetime: Optional[datetime] = None,
        system_data_provider: Optional[DataProvider] = None,
        ucum_service: Optional[object] = None
    ):
        """
        Initialize the evaluation context.

        Args:
            library: The main library to evaluate
            evaluation_datetime: Optional datetime for evaluation (default: now)
            system_data_provider: Optional data provider for system types
            ucum_service: Optional UCUM service for units
        """
        if evaluation_datetime is None:
            evaluation_datetime = datetime.now(timezone.utc)

        if system_data_provider is None:
            system_data_provider = SystemDataProvider()

        # Expression caching
        self.enable_expression_cache = False
        self.expressions: Dict[VersionedIdentifier, Dict[str, ExpressionResult]] = {}

        # Evaluated resources tracking
        self.evaluated_resource_stack: List[List[object]] = []

        # Parameters and state
        self.parameters: Dict[str, object] = {}
        self.current_context: List[str] = []
        self.context_values: Dict[str, object] = {}
        self.windows: List[List[Variable]] = []

        # Libraries
        self.libraries: Dict[str, Library] = {}
        self.current_library: List[Library] = []
        self.library_loader: Optional[LibraryLoader] = None

        # Data providers
        self.data_providers: Dict[str, DataProvider] = {}
        self.package_map: Dict[str, DataProvider] = {}

        # Terminology provider
        self.terminology_provider: Optional[TerminologyProvider] = None

        # External function providers
        self.external_function_providers: Dict[VersionedIdentifier, ExternalFunctionProvider] = {}

        # Function cache
        self.function_cache: Dict[str, List[object]] = {}

        # DateTime state
        self.set_evaluation_datetime(evaluation_datetime)

        # UCUM service
        if ucum_service is not None:
            self.ucum_service = ucum_service
        else:
            self.ucum_service = self.get_shared_ucum_service()

        # Debug state
        self.debug_map: Optional[object] = None
        self.debug_result: Optional[object] = None

        # Initialize
        self.push_window()
        self.register_data_provider("urn:hl7-org:elm-types:r1", system_data_provider)
        self.library_loader = self._create_default_library_loader()

        if library.get_identifier() is not None:
            lib_id = library.get_identifier().get_id() if hasattr(library.get_identifier(), 'get_id') else library.get_identifier().id
            self.libraries[lib_id] = library

        self.current_library.append(library)
        self.push_evaluated_resource_stack()

    @staticmethod
    def _create_default_library_loader():
        """Create a default library loader."""
        from cql_engine.execution.default_library_loader import DefaultLibraryLoader
        return DefaultLibraryLoader()

    def set_evaluation_datetime(self, evaluation_datetime: datetime) -> None:
        """Set the evaluation datetime."""
        self.evaluation_datetime = evaluation_datetime
        self.evaluation_offset_datetime = evaluation_datetime
        from cql_engine.runtime.datetime import DateTime
        self.evaluation_datetime_obj = DateTime(evaluation_datetime)

    def get_evaluation_datetime(self) -> datetime:
        """Get the evaluation datetime."""
        return self.evaluation_datetime

    def get_ucum_service(self) -> Optional[object]:
        """Get the UCUM service."""
        return self.ucum_service

    @staticmethod
    def get_shared_ucum_service() -> Optional[object]:
        """Get or create the shared UCUM service."""
        # Placeholder - actual UCUM service would be loaded here
        return None

    def set_expression_caching(self, enable: bool) -> None:
        """Enable or disable expression caching."""
        self.enable_expression_cache = enable

    def is_expression_caching_enabled(self) -> bool:
        """Check if expression caching is enabled."""
        return self.enable_expression_cache

    def get_evaluated_resources(self) -> List[object]:
        """Get the current evaluated resources list."""
        if not self.evaluated_resource_stack:
            raise IllegalStateException("Attempted to get the evaluatedResource stack when it's empty")
        return self.evaluated_resource_stack[-1]

    def clear_evaluated_resources(self) -> None:
        """Clear the evaluated resources stack."""
        self.evaluated_resource_stack.clear()
        self.push_evaluated_resource_stack()

    def push_evaluated_resource_stack(self) -> None:
        """Push a new resources list onto the stack."""
        self.evaluated_resource_stack.append([])

    def pop_evaluated_resource_stack(self) -> None:
        """Pop resources from the stack and merge into parent."""
        if not self.evaluated_resource_stack:
            raise IllegalStateException("Attempted to pop the evaluatedResource stack when it's empty")
        if len(self.evaluated_resource_stack) == 1:
            raise IllegalStateException("Attempted to pop the evaluatedResource stack when only the root remains")
        resources = self.evaluated_resource_stack.pop()
        self.evaluated_resource_stack[-1].extend(resources)

    def get_debug_map(self) -> Optional[object]:
        """Get the debug map."""
        return self.debug_map

    def set_debug_map(self, debug_map: Optional[object]) -> None:
        """Set the debug map."""
        self.debug_map = debug_map

    def get_debug_result(self) -> Optional[object]:
        """Get the debug result."""
        return self.debug_result

    def clear_expressions(self) -> None:
        """Clear the expression cache."""
        self.expressions.clear()

    def register_library_loader(self, library_loader: LibraryLoader) -> None:
        """Register a library loader."""
        if library_loader is None:
            raise CqlException("Library loader implementation must not be null.")
        self.library_loader = library_loader

    def get_current_library(self) -> Library:
        """Get the currently active library."""
        return self.current_library[-1] if self.current_library else None

    def enter_library(self, library_name: str) -> bool:
        """Enter a library by name."""
        if library_name is not None:
            # Would need to implement library resolution
            return True
        return False

    def exit_library(self, entered: bool) -> None:
        """Exit a library."""
        if entered and self.current_library:
            self.current_library.pop()

    def resolve_expression_ref(self, name: str) -> Optional[object]:
        """Resolve an expression definition by name."""
        lib = self.get_current_library()
        if lib and hasattr(lib, 'get_statements') and lib.get_statements():
            for expr_def in lib.get_statements().get_def():
                expr_name = expr_def.get_name() if hasattr(expr_def, 'get_name') else expr_def.name
                if expr_name == name:
                    return expr_def
        raise CqlException(f'Could not resolve expression reference \"{name}\" in library \"{lib.get_identifier().get_id() if lib else "Unknown"}\".')

    def push_window(self) -> None:
        """Push a new variable window."""
        self.windows.append([])

    def pop_window(self) -> None:
        """Pop a variable window."""
        if self.windows:
            self.windows.pop()

    def push(self, variable: Variable) -> None:
        """Push a variable onto the current window."""
        if self.windows:
            self.windows[-1].append(variable)

    def pop(self) -> None:
        """Pop a variable from the current window."""
        if self.windows and self.windows[-1]:
            self.windows[-1].pop()

    def resolve_variable(self, name: str, must_resolve: bool = True) -> Optional[Variable]:
        """Resolve a variable by name."""
        for window in reversed(self.windows):
            for var in window:
                if var.get_name() == name:
                    return var
        if must_resolve:
            raise CqlException(f"Could not resolve variable reference {name}")
        return None

    def enter_context(self, context: Optional[str]) -> None:
        """Enter a context."""
        if context is not None:
            self.current_context.append(context)

    def exit_context(self) -> None:
        """Exit the current context."""
        if self.current_context:
            self.current_context.pop()

    def get_current_context(self) -> Optional[str]:
        """Get the current context."""
        return self.current_context[-1] if self.current_context else None

    def set_context_value(self, context: str, value: object) -> None:
        """Set the value for a context."""
        if self.context_values.get(context) != value:
            self.clear_expressions()
        self.context_values[context] = value

    def get_current_context_value(self) -> Optional[object]:
        """Get the value of the current context."""
        context = self.get_current_context()
        if context and context in self.context_values:
            return self.context_values[context]
        return None

    def set_parameter(self, library_name: str, name: str, value: object) -> None:
        """Set a parameter value."""
        entered = self.enter_library(library_name)
        try:
            lib = self.get_current_library()
            lib_id = lib.get_identifier().get_id() if hasattr(lib.get_identifier(), 'get_id') else lib.get_identifier().id
            full_name = f"{lib_id}.{name}" if library_name else name
            self.parameters[full_name] = value
        finally:
            self.exit_library(entered)

    def register_data_provider(self, model_uri: str, data_provider: DataProvider) -> None:
        """Register a data provider for a model."""
        self.data_providers[model_uri] = data_provider
        for package_name in data_provider.get_package_names():
            self.package_map[package_name] = data_provider

    def resolve_data_provider(self, package_or_uri: str, must_resolve: bool = True) -> Optional[DataProvider]:
        """Resolve a data provider by package name or URI."""
        provider = self.package_map.get(package_or_uri) or self.data_providers.get(package_or_uri)
        if provider is None and must_resolve:
            raise CqlException(f"Could not resolve data provider for package/model '{package_or_uri}'.")
        return provider

    def register_terminology_provider(self, tp: TerminologyProvider) -> None:
        """Register a terminology provider."""
        self.terminology_provider = tp

    def resolve_terminology_provider(self) -> Optional[TerminologyProvider]:
        """Resolve the terminology provider."""
        return self.terminology_provider

    def register_external_function_provider(
        self, identifier: VersionedIdentifier, provider: ExternalFunctionProvider
    ) -> None:
        """Register an external function provider."""
        self.external_function_providers[identifier] = provider

    def get_external_function_provider(self) -> ExternalFunctionProvider:
        """Get the external function provider for the current library."""
        lib = self.get_current_library()
        identifier = lib.get_identifier()
        provider = self.external_function_providers.get(identifier)
        if provider is None:
            raise CqlException(
                f"Could not resolve external function provider for library '{identifier}'."
            )
        return provider

    def resolve_path(self, target: object, path: str) -> object:
        """Resolve a path on an object."""
        if target is None:
            return None

        clazz = type(target)
        if clazz.__module__.startswith('builtins') or clazz.__module__.startswith('java'):
            raise CqlException(
                f"Invalid path: {path} for type: {clazz.__name__} - this is likely an issue with the data model."
            )

        data_provider = self.resolve_data_provider(clazz.__module__, must_resolve=False)
        if data_provider:
            return data_provider.resolve_path(target, path)
        return None

    def set_value(self, target: object, path: str, value: object) -> None:
        """Set a value on an object."""
        if target is None:
            return

        clazz = type(target)
        data_provider = self.resolve_data_provider(clazz.__module__)
        data_provider.set_value(target, path, value)

    def object_equal(self, left: object, right: object) -> Optional[bool]:
        """Compare two objects for equality."""
        if left is None:
            return None

        clazz = type(left)
        data_provider = self.resolve_data_provider(clazz.__module__)
        return data_provider.object_equal(left, right)

    def object_equivalent(self, left: object, right: object) -> Optional[bool]:
        """Compare two objects for equivalence."""
        if left is None and right is None:
            return True
        if left is None:
            return False

        clazz = type(left)
        data_provider = self.resolve_data_provider(clazz.__module__)
        return data_provider.object_equivalent(left, right)


class IllegalStateException(Exception):
    """Raised when an illegal state is encountered."""
    pass

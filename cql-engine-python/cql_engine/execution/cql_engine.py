"""
CQL Engine for evaluating CQL libraries.

Core execution engine for evaluating CQL expressions.
"""

from typing import Dict, Set, Optional, Map, Tuple as TupleType
from enum import Enum
from datetime import datetime, timezone
from cql_engine.execution.library_loader import LibraryLoader, VersionedIdentifier, Library
from cql_engine.execution.context import Context
from cql_engine.execution.evaluation_result import EvaluationResult
from cql_engine.execution.expression_result import ExpressionResult
from cql_engine.execution.in_memory_library_loader import InMemoryLibraryLoader
from cql_engine.execution.namespace_helper import NamespaceHelper
from cql_engine.data.data_provider import DataProvider
from cql_engine.data.system_data_provider import SystemDataProvider
from cql_engine.terminology.terminology_provider import TerminologyProvider


class CqlEngineOptions(Enum):
    """Options for CQL engine behavior."""
    ENABLE_EXPRESSION_CACHING = "EnableExpressionCaching"
    ENABLE_VALIDATION = "EnableValidation"


class CqlException(Exception):
    """Exception raised during CQL execution."""
    pass


class CqlEngine:
    """
    Core CQL evaluation engine.

    Coordinates the evaluation of CQL libraries with support for multiple data providers,
    terminology services, expression caching, and validation.
    """

    def __init__(
        self,
        library_loader: LibraryLoader,
        data_providers: Optional[Dict[str, DataProvider]] = None,
        terminology_provider: Optional[TerminologyProvider] = None,
        engine_options: Optional[Set[CqlEngineOptions]] = None
    ):
        """
        Initialize the CQL engine.

        Args:
            library_loader: The LibraryLoader to use for loading libraries
            data_providers: Optional map of model URI to DataProvider
            terminology_provider: Optional TerminologyProvider for terminology services
            engine_options: Optional set of engine options to enable

        Raises:
            ValueError: If library_loader is None
        """
        if library_loader is None:
            raise ValueError("libraryLoader can not be null.")

        if engine_options is None:
            engine_options = {CqlEngineOptions.ENABLE_EXPRESSION_CACHING}

        self.library_loader = library_loader
        self.data_providers = data_providers
        self.terminology_provider = terminology_provider
        self.engine_options = engine_options

    def evaluate(
        self,
        library_name: str,
        expressions: Optional[Set[str]] = None,
        context_parameter: Optional[TupleType[str, object]] = None,
        parameters: Optional[Dict[str, object]] = None
    ) -> EvaluationResult:
        """
        Evaluate a library by name.

        Args:
            library_name: The name of the library to evaluate
            expressions: Optional set of expression names to evaluate (all if None)
            context_parameter: Optional (context_name, context_value) tuple
            parameters: Optional map of parameter names to values

        Returns:
            EvaluationResult containing results for each expression
        """
        from cql_engine.execution.library_loader import VersionedIdentifier as VI
        lib_id = VI() if not hasattr(VI, '__init__') else VI()
        if hasattr(lib_id, 'with_id'):
            lib_id = lib_id.with_id(library_name)
        else:
            lib_id.set_id(library_name)
        return self.evaluate_versioned(
            lib_id, expressions, context_parameter, parameters, None, None
        )

    def evaluate_versioned(
        self,
        library_identifier: VersionedIdentifier,
        expressions: Optional[Set[str]] = None,
        context_parameter: Optional[TupleType[str, object]] = None,
        parameters: Optional[Dict[str, object]] = None,
        debug_map: Optional[object] = None,
        evaluation_datetime: Optional[datetime] = None
    ) -> EvaluationResult:
        """
        Evaluate a library by versioned identifier.

        Args:
            library_identifier: The versioned identifier of the library
            expressions: Optional set of expression names to evaluate
            context_parameter: Optional (context_name, context_value) tuple
            parameters: Optional map of parameters
            debug_map: Optional debug map for debugging
            evaluation_datetime: Optional datetime for evaluation

        Returns:
            EvaluationResult containing results for each expression

        Raises:
            ValueError: If library_identifier is None or library cannot be loaded
        """
        if library_identifier is None:
            raise ValueError("libraryIdentifier can not be null.")

        library_cache: Dict[VersionedIdentifier, Library] = {}
        library = self.load_and_validate(library_cache, library_identifier)

        if expressions is None:
            expressions = self.get_expression_set(library)

        if evaluation_datetime is None:
            evaluation_datetime = datetime.now(timezone.utc)

        context = self.initialize_context(library_cache, library, debug_map, evaluation_datetime)
        self.set_parameters_for_context(library, context, context_parameter, parameters)

        return self.evaluate_expressions(context, expressions)

    def evaluate_expressions(
        self,
        context: Context,
        expressions: Set[str]
    ) -> EvaluationResult:
        """
        Evaluate a set of expressions within a context.

        Args:
            context: The evaluation context
            expressions: The expression names to evaluate

        Returns:
            EvaluationResult with results for each expression
        """
        result = EvaluationResult()

        for expression_name in expressions:
            expr_def = context.resolve_expression_ref(expression_name)

            if expr_def is None:
                raise CqlException(f'Unable to resolve expression "{expression_name}."')

            # Skip function definitions
            if hasattr(expr_def, '__class__') and 'FunctionDef' in expr_def.__class__.__name__:
                continue

            context.enter_context(expr_def.get_context() if hasattr(expr_def, 'get_context') else None)
            obj = expr_def.evaluate(context) if hasattr(expr_def, 'evaluate') else expr_def
            result.expression_results[expression_name] = ExpressionResult(
                obj, context.get_evaluated_resources()
            )

        result.set_debug_result(context.get_debug_result())
        context.clear_expressions()

        return result

    def set_parameters_for_context(
        self,
        library: Library,
        context: Context,
        context_parameter: Optional[TupleType[str, object]],
        parameters: Optional[Dict[str, object]]
    ) -> None:
        """
        Set parameters in the evaluation context.

        Args:
            library: The library being evaluated
            context: The evaluation context
            context_parameter: Optional context parameter
            parameters: Optional additional parameters
        """
        if context_parameter is not None:
            context.set_context_value(context_parameter[0], context_parameter[1])

        if parameters is not None:
            lib_id = library.get_identifier().get_id() if hasattr(library.get_identifier(), 'get_id') else library.get_identifier().id
            for param_name, param_value in parameters.items():
                context.set_parameter(lib_id, param_name, param_value)

            if (hasattr(library, 'get_includes') and library.get_includes() is not None and
                    hasattr(library.get_includes(), 'get_def')):
                for include_def in library.get_includes().get_def():
                    include_name = include_def.get_local_identifier() if hasattr(include_def, 'get_local_identifier') else include_def.local_identifier
                    for param_name, param_value in parameters.items():
                        context.set_parameter(include_name, param_name, param_value)

    def initialize_context(
        self,
        library_cache: Dict[VersionedIdentifier, Library],
        library: Library,
        debug_map: Optional[object],
        evaluation_datetime: datetime
    ) -> Context:
        """
        Initialize the evaluation context.

        Args:
            library_cache: Cache of loaded libraries
            library: The main library being evaluated
            debug_map: Optional debug map
            evaluation_datetime: The datetime for evaluation

        Returns:
            An initialized Context
        """
        context = Context(library, evaluation_datetime)

        context.register_library_loader(InMemoryLibraryLoader(library_cache.values()))

        if CqlEngineOptions.ENABLE_EXPRESSION_CACHING in self.engine_options:
            context.set_expression_caching(True)

        if self.terminology_provider is not None:
            context.register_terminology_provider(self.terminology_provider)

        if self.data_providers is not None:
            for model_uri, provider in self.data_providers.items():
                context.register_data_provider(model_uri, provider)

        context.set_debug_map(debug_map)

        return context

    def load_and_validate(
        self,
        library_cache: Dict[VersionedIdentifier, Library],
        library_identifier: VersionedIdentifier
    ) -> Library:
        """
        Load a library and validate its requirements.

        Args:
            library_cache: Cache for loaded libraries
            library_identifier: The library identifier to load

        Returns:
            The loaded Library

        Raises:
            ValueError: If library cannot be loaded or requirements are not met
        """
        if library_identifier in library_cache:
            return library_cache[library_identifier]

        library = self.library_loader.load(library_identifier)

        if library is None:
            lib_desc = self.get_library_description(library_identifier)
            raise ValueError(f"Unable to load library {lib_desc}")

        if CqlEngineOptions.ENABLE_VALIDATION in self.engine_options:
            self.validate_terminology_requirements(library)
            self.validate_data_requirements(library)

        if (hasattr(library, 'get_includes') and library.get_includes() is not None and
                hasattr(library.get_includes(), 'get_def')):
            for include_def in library.get_includes().get_def():
                include_path = include_def.get_path() if hasattr(include_def, 'get_path') else include_def.path
                uri_part = NamespaceHelper.get_uri_part(include_path)
                name_part = NamespaceHelper.get_name_part(include_path)
                version = include_def.get_version() if hasattr(include_def, 'get_version') else getattr(include_def, 'version', None)

                from cql_engine.execution.library_loader import VersionedIdentifier as VI
                include_id = VI() if not hasattr(VI, '__init__') else VI()
                if hasattr(include_id, 'with_system'):
                    include_id = include_id.with_system(uri_part)
                else:
                    include_id.system = uri_part
                if hasattr(include_id, 'with_id'):
                    include_id = include_id.with_id(name_part)
                else:
                    include_id.id = name_part
                if hasattr(include_id, 'with_version'):
                    include_id = include_id.with_version(version)
                else:
                    include_id.version = version

                self.load_and_validate(library_cache, include_id)

        library_cache[library_identifier] = library
        return library

    def validate_data_requirements(self, library: Library) -> None:
        """
        Validate that required data providers are registered.

        Args:
            library: The library to validate

        Raises:
            ValueError: If required data providers are missing
        """
        if (hasattr(library, 'get_usings') and library.get_usings() is not None and
                hasattr(library.get_usings(), 'get_def')):
            usings = library.get_usings().get_def()
            if usings:
                for using_def in usings:
                    using_uri = using_def.get_uri() if hasattr(using_def, 'get_uri') else using_def.uri
                    if using_uri == "urn:hl7-org:elm-types:r1":
                        continue

                    if self.data_providers is None or using_uri not in self.data_providers:
                        lib_desc = self.get_library_description(library.get_identifier())
                        raise ValueError(
                            f"Library {lib_desc} is using {using_uri} and no data provider is registered for uri {using_uri}."
                        )

    def validate_terminology_requirements(self, library: Library) -> None:
        """
        Validate that a terminology provider is registered if needed.

        Args:
            library: The library to validate

        Raises:
            ValueError: If terminology services are required but not registered
        """
        has_code_systems = (hasattr(library, 'get_code_systems') and
                           library.get_code_systems() is not None and
                           hasattr(library.get_code_systems(), 'get_def') and
                           library.get_code_systems().get_def())
        has_codes = (hasattr(library, 'get_codes') and
                    library.get_codes() is not None and
                    hasattr(library.get_codes(), 'get_def') and
                    library.get_codes().get_def())
        has_value_sets = (hasattr(library, 'get_value_sets') and
                         library.get_value_sets() is not None and
                         hasattr(library.get_value_sets(), 'get_def') and
                         library.get_value_sets().get_def())

        if has_code_systems or has_codes or has_value_sets:
            if self.terminology_provider is None:
                lib_desc = self.get_library_description(library.get_identifier())
                raise ValueError(
                    f"Library {lib_desc} has terminology requirements and no terminology provider is registered."
                )

    def get_library_description(self, library_identifier: VersionedIdentifier) -> str:
        """
        Get a human-readable description of a library identifier.

        Args:
            library_identifier: The library identifier

        Returns:
            A string description of the library
        """
        lib_id = library_identifier.get_id() if hasattr(library_identifier, 'get_id') else library_identifier.id
        version = library_identifier.get_version() if hasattr(library_identifier, 'get_version') else getattr(library_identifier, 'version', None)
        return f"{lib_id}" + (f"-{version}" if version else "")

    def get_expression_set(self, library: Library) -> Set[str]:
        """
        Get the set of all expression names in a library.

        Args:
            library: The library

        Returns:
            Set of expression names
        """
        expression_names = set()
        if (hasattr(library, 'get_statements') and library.get_statements() is not None and
                hasattr(library.get_statements(), 'get_def')):
            for expr_def in library.get_statements().get_def():
                expr_name = expr_def.get_name() if hasattr(expr_def, 'get_name') else expr_def.name
                expression_names.add(expr_name)
        return expression_names

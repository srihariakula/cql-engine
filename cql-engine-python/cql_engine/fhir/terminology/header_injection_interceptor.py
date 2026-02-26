"""HTTP header injection interceptor for FHIR requests."""

from typing import Any, Dict, Optional


class HeaderInjectionInterceptor:
    """Injects custom headers into FHIR HTTP requests.

    Used to add authorization, user agent, and other headers to
    terminology service requests.
    """

    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Initialize the interceptor.

        Args:
            headers: Dictionary of headers to inject
        """
        self.headers = headers or {}

    def add_header(self, name: str, value: str) -> None:
        """Add a header to inject.

        Args:
            name: Header name
            value: Header value
        """
        self.headers[name] = value

    def remove_header(self, name: str) -> None:
        """Remove a header.

        Args:
            name: Header name
        """
        if name in self.headers:
            del self.headers[name]

    def get_headers(self) -> Dict[str, str]:
        """Get all injected headers.

        Returns:
            Dictionary of headers
        """
        return self.headers.copy()

    def intercept_request(self, request: Any) -> Any:
        """Intercept and modify an HTTP request.

        Args:
            request: HTTP request object

        Returns:
            Modified request
        """
        if hasattr(request, "headers"):
            for name, value in self.headers.items():
                request.headers[name] = value
        return request

    def intercept_response(self, response: Any) -> Any:
        """Intercept an HTTP response.

        Args:
            response: HTTP response object

        Returns:
            Response (unmodified)
        """
        return response

from typing import Callable, Optional, Awaitable, Iterable, Any, Pattern
import muffin

Route = Callable[[muffin.Request], Awaitable[muffin.Response]]


class Application(muffin.Application):
    def add_route(self, target: Route, *paths: str | Pattern[str], methods: Optional[str | Iterable[str]] = None, **opts: Any) -> None:
        router = self.router

        if hasattr(target, "__route__"):
            target.__route__(router, *paths, methods=methods, **opts) # type: ignore
            return 
        if not router.validator(target): # type: ignore
            raise router.RouterError("Invalid target: %r" % target)

        target = router.converter(target) # type: ignore
        router.bind(target, *paths, methods=methods, **opts)  # type: ignore
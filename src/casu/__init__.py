from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, Iterable, Any, Pattern
import muffin

Route = Callable[[muffin.Request], Awaitable[muffin.Response]]

@dataclass
class RouteData:
    handler: Route
    paths: list[str]
    methods: Optional[str | Iterable[str]]
    opts: Any

class Blueprint:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix.removesuffix("/")
        self.routes: list[RouteData] = []

    def route(self, *paths: str, methods: Optional[str | Iterable[str]] = None, **opts: Any) -> Callable[[Route], Route]:

        def deco(route: Route) -> Route:
            self.routes.append(RouteData(route, [self.prefix + path for path in paths], methods, opts))

            return route
        
        return deco


class Application(muffin.Application):
    def add_route(self, handler: Route, *paths: str | Pattern[str], methods: Optional[str | Iterable[str]] = None, **opts: Any) -> None:
        router = self.router

        if hasattr(handler, "__route__"):
            handler.__route__(router, *paths, methods=methods, **opts) # type: ignore
            return 
        if not router.validator(handler): # type: ignore
            raise router.RouterError("Invalid target: %r" % handler)

        handler = router.converter(handler) # type: ignore
        router.bind(handler, *paths, methods=methods, **opts)  # type: ignore

    def add_blueprint(self, blueprint: Blueprint) -> None:
        for route in blueprint.routes:
            self.add_route(route.handler, *route.paths, methods=route.methods, **route.opts)


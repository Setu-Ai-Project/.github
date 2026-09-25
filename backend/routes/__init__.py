from routes.user import router as user_router
from routes.module import router as module_router
from routes.sub_module import router as sub_module_router
from routes.progress import router as progress_router
from routes.bug_trigger import router as bug_trigger_router
from routes.spark_term import router as spark_term_router
from routes.byte_fact import router as byte_fact_router

__all__ = [
    "user_router",
    "module_router",
    "sub_module_router",
    "progress_router",
    "bug_trigger_router",
    "spark_term_router",
    "byte_fact_router",
]

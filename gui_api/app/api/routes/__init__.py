from fastapi import APIRouter

from api.routes.alert import router as alert_router
from api.routes.alert_comment import router as alert_comment_router
from api.routes.alert_disposition import router as alert_disposition_router
from api.routes.alert_tool import router as alert_tool_router
from api.routes.alert_tool_instance import router as alert_tool_instance_router
from api.routes.alert_type import router as alert_type_router
from api.routes.analysis import router as analysis_router
from api.routes.api_auth import router as auth_router
from api.routes.event import router as event_router
from api.routes.event_comment import router as event_comment_router
from api.routes.event_prevention_tool import router as event_prevention_tool_router
from api.routes.event_remediation import router as event_remediation_router
from api.routes.event_severity import router as event_severity_router
from api.routes.event_status import router as event_status_router
from api.routes.event_type import router as event_type_router
from api.routes.event_vector import router as event_vector_router
from api.routes.metadata_directive import router as metadata_directive_router
from api.routes.metadata_tag import router as metadata_tag_router
from api.routes.observable import router as observable_router
from api.routes.observable_type import router as observable_type_router
from api.routes.ping import router as ping_router
from api.routes.queue import router as queue_router
from api.routes.test import router as test_router
from api.routes.threat import router as threat_router
from api.routes.threat_actor import router as threat_actor_router
from api.routes.threat_type import router as threat_type_router
from api.routes.user import router as user_router


router = APIRouter()

router.include_router(alert_comment_router)
router.include_router(alert_router)
router.include_router(alert_disposition_router)
router.include_router(alert_tool_router)
router.include_router(alert_tool_instance_router)
router.include_router(alert_type_router)
router.include_router(analysis_router)
router.include_router(auth_router)
router.include_router(event_comment_router)
router.include_router(event_router)
router.include_router(event_prevention_tool_router)
router.include_router(event_remediation_router)
router.include_router(event_severity_router)
router.include_router(event_status_router)
router.include_router(event_type_router)
router.include_router(event_vector_router)
router.include_router(metadata_directive_router)
router.include_router(metadata_tag_router)
router.include_router(observable_router)
router.include_router(observable_type_router)
router.include_router(ping_router)
router.include_router(queue_router)
router.include_router(test_router)
router.include_router(threat_router)
router.include_router(threat_actor_router)
router.include_router(threat_type_router)
router.include_router(user_router)

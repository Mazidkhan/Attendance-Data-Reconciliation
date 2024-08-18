import structlog

logger = structlog.getLogger(__name__)


class DependentObject:

    def __init__(self, database_connection, master_config, master_constants):
        logger.info("Initializing Dependent Object")
        self.database_connection = database_connection
        self.master_config = master_config
        self.master_constants = master_constants
        self.validator = None
        self.daily_attendance_details = None
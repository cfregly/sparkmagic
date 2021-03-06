from datetime import datetime
import importlib
import remotespark.utils.configuration as conf
import remotespark.utils.constants as constants


class SparkEvents:
    def __init__(self):
        """
        Create an instance from the handler mentioned in the config file.
        """
        module, class_name = conf.events_handler_class().rsplit('.', 1)
        events_handler_module = importlib.import_module(module)
        events_handler = getattr(events_handler_module, class_name)

        self.handler = events_handler()

    def emit_session_creation_start_event(self, session_guid, language):
        """
        Emitting Start Session Event
        """
        assert language in constants.SESSION_KINDS_SUPPORTED

        event_name = constants.SESSION_CREATION_START_EVENT
        time_stamp = SparkEvents.get_utc_date_time()

        kwargs_list = [(constants.EVENT_NAME, event_name), (constants.TIMESTAMP, time_stamp), (constants.SESSION_GUID, session_guid),
                       (constants.LIVY_KIND, language)]

        self.handler.handle_event(kwargs_list)

    def emit_session_creation_end_event(self, session_guid, language, session_id, status):
        """
        Emitting End Session Event
        """
        assert language in constants.SESSION_KINDS_SUPPORTED
        assert session_id >= 0

        event_name = constants.SESSION_CREATION_END_EVENT
        time_stamp = SparkEvents.get_utc_date_time()

        kwargs_list = [(constants.EVENT_NAME, event_name), (constants.TIMESTAMP, time_stamp), (constants.SESSION_GUID, session_guid),
                       (constants.LIVY_KIND, language), (constants.SESSION_ID, session_id), (constants.STATUS, status)]

        self.handler.handle_event(kwargs_list)

    @staticmethod
    def get_utc_date_time():
        return datetime.utcnow()

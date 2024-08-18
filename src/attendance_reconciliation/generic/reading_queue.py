import numpy as np

import structlog

logger = structlog.getLogger(__name__)


class ReadingQueue:

    def __init__(self, key, length=10, damp_outliers=True):
        self.key = key
        self.length = length
        self.damp_outliers = damp_outliers
        self.data_queue = []
        self.last_reading = 0
        self.max_consecutive_error = 5
        self.current_consecutive_error = 0

    def calculate_value(self, new_value_obj):
        (new_value, dq, error) = new_value_obj
        if dq != "U":
            if self.current_consecutive_error > self.max_consecutive_error:
                return new_value_obj
            else:
                self.current_consecutive_error += 1
                return self.last_reading, 'U', {}
        self.current_consecutive_error = 0
        np_data_array = np.array(self.data_queue)
        prev_mean = np.mean(np_data_array) if len(self.data_queue) > 0 else 0
        returned_value = new_value

        self.data_queue.append(new_value)
        if len(self.data_queue) > self.length:
            self.data_queue.pop(0)

        if len(self.data_queue) >= self.length:
            np_data_array = np.array(self.data_queue)
            mean = np.mean(np_data_array)
            std_dev = np.std(np_data_array)
            # logger.info("In Queue checker Mean %0.2f SD %0.2f Data %s", mean, std_dev, str(self.data_queue))
            if abs(new_value - mean) > 2 * std_dev:
                logger.info("Supposed Outlier %s found %0.2f Mean %0.2f SD %0.2f Data %s",
                            self.key, new_value, mean, std_dev, str(self.data_queue))
                returned_value = prev_mean
            last_reading_difference = abs(self.last_reading - new_value)

            if last_reading_difference > 0.2 * self.last_reading:
                logger.info("Greater LRD %s %0.2f %0.2f", self.key, self.last_reading, new_value)
                self.data_queue.pop(-1)
            self.last_reading = new_value

        return returned_value, dq, error

    def log_queue_data(self, key):
        logger.info("Queue data for %s %s", key, str(self.data_queue))

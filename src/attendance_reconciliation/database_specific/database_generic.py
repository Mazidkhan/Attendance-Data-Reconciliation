import sqlite3
import time
import traceback

import structlog

logger = structlog.getLogger(__name__)



class GenericDatabase:

    def __init__(self, db_file):
        logger.info("Generic Database Intitialized")
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            self.conn.commit()
        except Exception as e:
            logger.error("Exception in creating tables: %s", str(traceback.format_exc()))
            logger.info("Query: %s", create_table_sql)

    def fetch_execute(self, query, input_value):
        retries_counter = 0
        is_fetched_successfully = False
        dict_rows = []
        while retries_counter <= 3 and not is_fetched_successfully:
            try:
                c = self.conn.cursor()
                c.execute(query, input_value)
                rows = c.fetchall()
                logger.debug("Select from current output: %s", str(rows))
                dict_rows = [dict(ix) for ix in rows]
                self.conn.commit()
                c.close()
                is_fetched_successfully = True
            except sqlite3.IntegrityError:
                logger.info("Data Already saved %s", str(input_value))
                is_fetched_successfully = True
            except sqlite3.OperationalError:
                logger.info("Operational error Retries %s and data %s", str(retries_counter),
                            str(input_value))
                logger.debug("Operation error %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)
            except Exception:
                logger.info("Input while error Retries %s and data %s", str(retries_counter),
                            str(input_value))
                logger.error("Exception in insert/update data table: %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)
        return dict_rows

    def query_execute(self, query, input_value):
        retries_counter = 0
        is_saved_successfully = False
        while retries_counter <= 3 and not is_saved_successfully:
            try:
                c = self.conn.cursor()
                c.execute(query, input_value)
                self.conn.commit()
                c.close()
                is_saved_successfully = True
            except sqlite3.IntegrityError:
                logger.info("Data Already saved %s", str(input_value))
                is_saved_successfully = True
            except sqlite3.OperationalError:
                logger.info("Operational error Retries %s and data %s", str(retries_counter),
                            str(input_value))
                logger.debug("Operation error %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)
            except Exception:
                logger.info("Input while error Retries %s and data %s", str(retries_counter),
                            str(input_value))
                logger.error("Exception in insert/update data table: %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)

    def bulk_execute(self, query, input_value_array):
        retries_counter = 0
        is_saved_successfully = False
        while retries_counter <= 3 and not is_saved_successfully:
            try:
                if len(input_value_array) > 0:
                    c = self.conn.cursor()
                    c.executemany(query, input_value_array)
                    self.conn.commit()
                    c.close()
                is_saved_successfully = True
            except sqlite3.IntegrityError:
                logger.info("Data Already saved %s", str(input_value_array))
                logger.debug("Integrity Error %s", str(traceback.format_exc()))
                is_saved_successfully = True
            except sqlite3.OperationalError:
                logger.info("Operational error Retries %s and data %s", str(retries_counter),
                            str(input_value_array))
                logger.debug("Operation error %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)
            except Exception:
                logger.info("Input while error Retries %s and data %s", str(retries_counter),
                            str(input_value_array))
                logger.error("Exception in insert/update data table: %s", str(traceback.format_exc()))
                retries_counter = retries_counter + 1
                time.sleep(1)

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

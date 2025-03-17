import logging

from . import PostgresConnect


log = logging.getLogger('QUERIES')


class Queries(PostgresConnect):

    def get_example_data(self):
        query = '''
            SELECT *
            FROM spatial_ref_sys
            LIMIT 5;
        '''
        result = self.execute_query(query)
        return result

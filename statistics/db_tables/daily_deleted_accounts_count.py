import typing

from . import DAY_LEN_SECONDS, daily_start_of_range
from ..periodic_statistics import PeriodicStatistics


class DailyDeletedAccountsCount(PeriodicStatistics):
    @property
    def sql_create_table(self):
        # For September 2021, we have 10^6 accounts on the Mainnet.
        # It means we fit into integer (10^9)
        return '''
            CREATE TABLE IF NOT EXISTS daily_deleted_accounts_count
            (
                collected_for_day      DATE PRIMARY KEY,
                deleted_accounts_count INTEGER NOT NULL
            )
        '''

    @property
    def sql_drop_table(self):
        return '''
            DROP TABLE IF EXISTS daily_deleted_accounts_count
        '''

    @property
    def sql_select(self):
        return '''
            SELECT COUNT(accounts.deleted_by_receipt_id)
            FROM accounts
            JOIN receipts ON receipts.receipt_id = accounts.deleted_by_receipt_id
            WHERE receipts.included_in_block_timestamp >= %(from_timestamp)s
                AND receipts.included_in_block_timestamp < %(to_timestamp)s
        '''

    @property
    def sql_select_all(self):
        return '''
            SELECT
                DATE_TRUNC('day', TO_TIMESTAMP(DIV(blocks.block_timestamp, 1000 * 1000 * 1000))) AS date,
                COUNT(accounts.deleted_by_receipt_id) AS deleted_accounts_count_by_date
            FROM accounts
            JOIN receipts ON receipts.receipt_id = accounts.deleted_by_receipt_id
            WHERE receipts.included_in_block_timestamp < (CAST(EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW())) AS bigint) * 1000 * 1000 * 1000)
            GROUP BY date
            ORDER BY date
        '''

    @property
    def sql_insert(self):
        return '''
            INSERT INTO daily_deleted_accounts_count VALUES %s
            ON CONFLICT DO NOTHING
        '''

    @property
    def duration_seconds(self):
        return DAY_LEN_SECONDS

    def start_of_range(self, requested_statistics_timestamp: typing.Optional[int]) -> int:
        return daily_start_of_range(requested_statistics_timestamp)

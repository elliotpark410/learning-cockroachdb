
import time
import uuid
from typing import Optional
from dataclasses import dataclass

# Assuming these would be defined elsewhere in your application
class SQLException(Exception):
    """Custom exception for SQL-related errors"""
    pass

class DataAccessException(Exception):
    """Spring-style data access exception"""
    def __init__(self, message: str, root_cause: Exception = None):
        super().__init__(message)
        self.root_cause = root_cause

    def get_root_cause(self) -> Optional[Exception]:
        """Get the root cause exception"""
        return self.root_cause

class PSQLException(Exception):
    """PostgreSQL/CockroachDB specific exception"""
    def __init__(self, message: str, sql_state: str = None):
        super().__init__(message)
        self.sql_state = sql_state

    def get_sql_state(self) -> str:
        """Get the SQL state code"""
        return self.sql_state

@dataclass
class CartItem:
    """Represents a cart item"""
    # Add your cart item fields here
    pass

class CartItemDao:
    """Data Access Object for cart items"""
    def insert(self, cart_item: CartItem) -> uuid.UUID:
        """Insert cart item and return its UUID"""
        # Your database insertion logic here
        pass

def add_item_to_cart_manual_retry(cart_item: CartItem, cart_item_dao: CartItemDao) -> uuid.UUID:
    """
    Add item to cart with manual retry logic and exponential backoff.

    Specifically handles CockroachDB serialization errors (SQL state 40001) which
    indicate transaction conflicts that should be retried. This is a common pattern
    when working with CockroachDB's distributed architecture.

    Showing explicit retry configuration parameters & logic for visibility
    and ease of modification.
    Don't perform retries this way in a real-world situation!
    Consider using libraries like tenacity or backoff instead.

    Args:
        cart_item: The cart item to add
        cart_item_dao: Data access object for cart operations

    Returns:
        UUID of the inserted cart item

    Raises:
        SQLException: If all retry attempts fail
        DataAccessException: If all retry attempts fail or non-retryable error occurs
    """
    max_retries = 3
    initial_retry_delay = 1.0  # one second (float for time.sleep)
    retry_count = 0
    cart_item_id = None

    while retry_count < max_retries:
        try:
            # Perform insert; it'll usually work
            cart_item_id = cart_item_dao.insert(cart_item)
            break  # done!

        except (SQLException, DataAccessException) as exception:
            # Check if this is a CockroachDB serialization error that should be retried
            should_retry = False

            if isinstance(exception, DataAccessException):
                root_cause = exception.get_root_cause()
                if (isinstance(root_cause, PSQLException) and
                    root_cause.get_sql_state() == "40001"):
                    # CockroachDB serialization error - retry this transaction
                    should_retry = True
                    print(f"CockroachDB serialization error detected (40001), retrying... (attempt {retry_count + 1})")
            elif isinstance(exception, SQLException):
                # Generic SQL exception - also retry
                should_retry = True
                print(f"SQL exception detected, retrying... (attempt {retry_count + 1})")

            if should_retry:
                # Going to need to retry this

                # Start with initial_retry_delay, then double it every time afterwards
                delay = initial_retry_delay * (2 ** retry_count)

                try:
                    # Sleep with exponential backoff
                    time.sleep(delay)
                except KeyboardInterrupt:
                    # Re-raise KeyboardInterrupt to allow graceful shutdown
                    raise

                # Get ready to retry
                retry_count += 1
                if retry_count >= max_retries:
                    # This was the last retry!

                    # For demo purposes, print what happened if we hit max_retries
                    print("Hit max retries.")

                    # Raise the original exception that we'd been catching up until now;
                    # we've done all we can.
                    raise exception
            else:
                # Not a retryable error - raise immediately
                raise exception

    # The insert worked!
    return cart_item_id
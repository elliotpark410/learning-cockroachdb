@Override
@Transactional
public UUID addItemToCartManualRetry(CartItem cartItem) throws SQLException {
    // Showing explicit retry configuration parameters & logic for visibility
    // and ease of modification.
    // Don't perform retries this way in a real-world situation!
    int maxRetries = 3;
    int initialRetryDelay = 1000;  // one second
    int retryCount = 0;
    UUID cartItemId = null;

    while (retryCount < maxRetries) {
        try {  // Perform insert; it'll usually work

            cartItemId = cartItemDao.insert(cartItem);
            break;  // done!

        } catch (SQLException exception) {  // Going to need to retry this

            // Start with initialRetryDelay, then double it every time afterwards
            int delay = (int)(initialRetryDelay * Math.pow(2, retryCount));

            try {  // sleep needs to be wrapped in try/catch clause
                Thread.sleep(delay);
            } catch(InterruptedException ex) {
                Thread.currentThread().interrupt();
            }

            // Get ready to retry
            retryCount++;
            if (retryCount >= maxRetries) {  // This was the last retry!

                // For demo purposes, print what happened if we hit maxRetries
                System.out.println("Hit max retries.");

                // throw the SQLException that we'd been catching up until now;
                // we've done all we can.
                throw exception;
            }
        }
    }

        // The insert worked!
        return cartItemId;
    }
}
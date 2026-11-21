package com.pipinha.qualityfix;

/**
 * Added to the Brewin' and Chewin' keg by mixin, so its static tick can reach the batch quality.
 */
public interface KegBatchAccess {
    void pipinha$clearBatchIfEmpty();
}

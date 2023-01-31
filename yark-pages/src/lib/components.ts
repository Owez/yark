/**
 * Component states and configuration used inside of Svelte guts
 */

/**
 * Status of if a card should be a start card
 */
export enum StartCardState {
    /**
     * It shouldn't be a start card
     */
    None,
    /**
     * It should be a typical start card
     */
    Enabled,
    /**
     * It should be a maximized card with a sizable view-width
     */
    Max
}
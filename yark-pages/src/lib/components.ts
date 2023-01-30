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
     * It should be a full-size start card
     */
    Full,
    /**
     * It should be a half-height start card
     */
    Half
}
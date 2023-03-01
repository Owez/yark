/**
 * Element decoding utility functions, used for when a Yark library element needs to be parsed/understood
 */

/**
 * Type cover for a generic element known to exist
 * 
 * This takes the form of a kv object with a string date and some generic value, e.g. `{"..": 1, "..": 2, "..": 3}`
 */
export type Element = object;

/**
 * Gets the current element value from a provided element
 * @param element Element to get the most current value of
 */
export function getCurrentElement(element: Element): any | undefined {
    const values = Object.values(element)
    if (values.length == 0 || (values.length == 1 && values[0] == "")) { return undefined }
    return values.slice(-1)[0]
}

/**
 * Checks if the element has been updated to something other than it's initial value
 * @param element Element to check
 * @returns If the element has been updated
 */
export function elementWasUpdated(element: Element): boolean {
    return elementUpdateCount(element) > 1
}

/**
 * Gets update count of the provided element
 * @param element Element to get count for
 * @returns Times element was updated
 */
export function elementUpdateCount(element: Element): number {
    return Object.values(element).length
}

/**
 * Element decoding utility functions, used for when a Yark library element needs to be parsed/understood
 */

/**
 * Type cover for a generic element known to exist
 * 
 * This takes the form of a kv object with a string date and some generic value, e.g. `{"..": 1, "..": 2, "..": 3}`
 */
export type Element = Object;

/**
 * Gets the current element value from a provided element
 * @param element Element to get the most current value of
 */
export function getCurrentElement(element: Element): any | undefined {
    const values = Object.values(element)
    if (values.length == 0) { return undefined }
    return values[0]
}

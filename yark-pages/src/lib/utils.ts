/**
 * Utility functions and classes for project-wide ease of use
 */

/**
 * Truncates a string to a given length, adding ellipsis if it's over
 * @param input String to truncate
 * @param to Number of characters to truncate to
 * @returns Truncated string
 */
export function truncate(input: string, to?: number): string {
    // Default truncation
    if (to == undefined) {
        to = 32
    }

    // Don't change if input is ok
    if (input.length <= to) { return input }

    // Cut it
    const cut = input.substring(0, to - 2)

    // Return with ellipsis
    return `${cut}..`
}
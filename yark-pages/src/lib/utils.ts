/**
 * Utility functions and classes for project-wide ease of use
 */

/**
 * URL to the locally-running API server instance
 */
export const LOCAL_SERVER = 'http://127.0.0.1:7666';

/**
 * Truncates a string to a given length, adding ellipsis if it's over
 * @param input String to truncate
 * @param to Number of characters to truncate to
 * @returns Truncated string
 */
export function truncate(input: string, to?: number): string {
	// Default truncation
	if (to == undefined) {
		to = 32;
	}

	// Don't change if input is ok
	if (input.length <= to) {
		return input;
	}

	// Cut it
	const cut = input.substring(0, to - 2);

	// Return with ellipsis
	return `${cut}..`;
}

/**
 * Capitalizes first letter of provided string; from https://stackoverflow.com/questions/1026069/how-do-i-make-the-first-letter-of-a-string-uppercase-in-javascript
 * @param i String to capitalize
 */
export function capitalizeFirstLetter(i: string): string {
	return i.charAt(0).toUpperCase() + i.slice(1);
}

/**
 * Converts a date object into a human readable one
 * @param date Date object to convert
 * @returns Human-readable date with ordinal
 */
export function humanDate(date: Date): string {
	const options: Intl.DateTimeFormatOptions = {
		year: "numeric",
		month: "long",
		day: "numeric",
	};
	const fmt = new Intl.DateTimeFormat(undefined, options).format(date)
	let splitted = fmt.split(" ")
	const ordinal = getOrdinal(parseInt(splitted[0]))
	splitted[0] += ordinal
	return splitted.join(" ")
}

/**
 * Converts a date object into a compact, but readable, string
 * @param date Date to stringify
 */
export function compactDate(date: Date): string {
	const options: Intl.DateTimeFormatOptions = {
		weekday: "short",
		month: "numeric",
		day: "numeric",
		hour: "numeric",
		minute: "numeric",
	}
	return new Intl.DateTimeFormat(undefined, options).format(date).replace(",", "")
}

/**
 * Gets ordinal for number
 * @param i Number to get ordinal for
 * @returns Ordinal string representation
 */
function getOrdinal(i: number): string {
	if (i > 3 && i < 21) return 'th';
	switch (i % 10) {
		case 1: return "st";
		case 2: return "nd";
		case 3: return "rd";
		default: return "th";
	}
}
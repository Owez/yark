/**
 * Core archive interfaces and related functions
 */

/**
 * Meta-information about an archive returned from {@link getArchiveMeta}; can be saved permanently
 */
export interface ArchiveMeta { 
    id: string,
    version: number,
    url: string,
    videos_count: number,
    livestreams_count: number,
    shorts_count: number,
}

/**
 * Single video inside of an archive which tracks a video's entire metadata history
 */
export interface Video {
    id: string,
    uploaded: Date,
    width: number,
    height: number,
    title: Elements<string>,
    description: Elements<string>,
    views: Elements<number>,
    likes: Elements<number>,
    thumbnail: Elements<ImageHash>,
    deleted: Elements<boolean>,
    notes: Note[]
}

/**
 * Collection of timestamped values to mark changes to history
 */
export type Elements<T> = Map<Date, T>

/**
 * Singleton of an {@link Elements} collection
 */
export interface Element<T> {
    taken: Date,
    data: T
}

/**
 * Gets the current (most recent) element from a collection
 * @param elements Elements collection to get from
 * @returns The most recently-added element or nothing
 */
export function getCurrentElement<T>(elements: Elements<T>): Element<T> | null {
    let mostRecentElement: Element<T> | null = null;
    for (const [taken, data] of elements.entries()) {
        if (!mostRecentElement || taken > mostRecentElement.taken) {
            mostRecentElement = { taken, data };
        }
    }
    return mostRecentElement;
}

/**
 * Gets the current (most recent) element from a collection or errors out
 * @param elements Elements collection to get from
 * @returns The most recently-added element
 */
export function getCurrentElementDefo<T>(elements: Elements<T>): Element<T> {
    const res = getCurrentElement(elements)
    if (res == null) {
        throw new Error("Elements list shouldn't be empty, expected an element here")
    }
    return res
}

/**
 * Type cover for hashes of {@link Elements} to use for images (e.g. thumbnails)
 */
export type ImageHash = string;

/**
 * User-written note for a video to comment on something at a specific time
 */
export interface Note {
    id: string,
    timestamp: number,
    title: string,
    description?: string
}
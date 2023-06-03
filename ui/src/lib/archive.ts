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
export interface Elements<T> {
    // TODO
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
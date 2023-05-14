/**
 * Representation of a Yark archive and its included videos/metadata
 */
export interface Archive {
    version: number,
    url: string,
    videos: Video[],
    livestreams: Video[],
    shorts: Video[],
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
    thumbnail: Images,
    deleted: Elements<boolean>, notes: Note[]
}

/**
 * Collection of timestamped values to mark changes to history
 */
export interface Elements<T> {
    // TODO
}

/**
 * Type cover for hashes of {@link Images} to use
 */
export type ImageHash = string;

/**
 * Type cover of many {@link ImageHash}; this can be used to pull the image files from the archive
 */
export type Images = Elements<ImageHash>;

/**
 * User-written note for a video to comment on something at a specific time
 */
export interface Note {
    id: string,
    timestamp: number,
    title: string,
    description?: string
}
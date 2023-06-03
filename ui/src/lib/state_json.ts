/**
 * Manual serialization/deserialization of archive states to JSON
 * 
 * This exists because anything can be easily `JSON.stringify`'d but converting it back into proper interfaces has to be done manually, so we have a plain JSON version of all the interfaces we need for archive/state. This is mainly used because we need to manually convert datetimes. 
 */

// NOTE: if this can be done better, please do it better. i'm sure there's a decent library out there like `serde` to make this less manual and overall cleaner

import type { ArchiveMeta } from "./api";
import type { Elements, ImageHash, Note, Video } from "./archive";
import type { ArchiveState, VideosSnapshot } from "./state";

/**
 * Previously serialized {@link Date} currently as a string
 */
export type DateRaw = string;

/**
 * Converts a raw date to a proper date
 * @param dateRaw Raw date to convert back
 * @returns Converted date from {@link dateRaw} passed in
 */
function dateRawToDate(dateRaw: DateRaw): Date {
    const ts = Date.parse(dateRaw)
    return new Date(ts)
}

/**
 * Serialized version of {@link Elements}
 */
export interface SerializedElements<T> {
    [date: string]: T
}

/**
 * Deserializes {@link input} into a proper {@link Elements} collection
 * @param input Serialized version of an element
 * @returns Deserialized {@link input}
 */
export function deserializeElements<T>(input: SerializedElements<T>): Elements<T> {
    const elements: Elements<T> = new Map<Date, T>();
    for (const dateStr in input) {
        if (input.hasOwnProperty(dateStr)) {
            const date = new Date(dateStr);
            const value = input[dateStr];
            elements.set(date, value);
        }
    }
    return elements;
}

// TODO
export function serializeElements<T>(input: Elements<T>): SerializedElements<T> {
    const serialized: SerializedElements<T> = {};
    for (const [date, value] of input) {
        serialized[date.toISOString()] = value;
    }
    return serialized;
}

/**
 * Serialized version of a {@link Video}
 */
export interface SerializedVideo {
    id: string,
    uploaded: DateRaw,
    width: number,
    height: number,
    title: SerializedElements<string>,
    description: SerializedElements<string>,
    views: SerializedElements<number>,
    likes: SerializedElements<number>,
    thumbnail: SerializedElements<ImageHash>,
    deleted: SerializedElements<boolean>,
    notes: Note[]
}

/**
 * Deserializes {@link input} into a proper {@link Video}
 * @param input Serialized version of a video
 * @returns Deserialized {@link input}
 */
export function deserializeVideo(input: SerializedVideo): Video {
    return {
        id: input.id,
        uploaded: dateRawToDate(input.uploaded),
        width: input.width,
        height: input.height,
        title: deserializeElements(input.title),
        description: deserializeElements(input.description),
        views: deserializeElements(input.views),
        likes: deserializeElements(input.likes),
        thumbnail: deserializeElements(input.thumbnail),
        deleted: deserializeElements(input.deleted),
        notes: input.notes
    }
}

// TODO
export function serializeVideo(input: Video): SerializedVideo {
    return {
        id: input.id,
        uploaded: input.uploaded.toISOString(),
        width: input.width,
        height: input.height,
        title: serializeElements(input.title),
        description: serializeElements(input.description),
        views: serializeElements(input.views),
        likes: serializeElements(input.likes),
        thumbnail: serializeElements(input.thumbnail),
        deleted: serializeElements(input.deleted),
        notes: input.notes
    }
}

/**
 * Serialized version of a {@link VideosSnapshot}
 */
export interface SerializedVideosSnapshot {
    taken: DateRaw,
    videos: SerializedVideo[]
}

/**
 * Deserializes {@link input} into a proper {@link VideosSnapshot}
 * @param input Serialized version of a videos snapshot
 * @returns Deserialized {@link input}
 */
export function deserializeVideosSnapshot(input: SerializedVideosSnapshot): VideosSnapshot {
    return {
        taken: dateRawToDate(input.taken),
        videos: input.videos.map(serializedVideo => deserializeVideo(serializedVideo))
    }
}

// TODO
export function serializeVideosSnapshot(input: VideosSnapshot): SerializedVideosSnapshot {
    return {
        taken: input.taken.toISOString(),
        videos: input.videos.map(video => serializeVideo(video))
    }
}

/**
 * Serialized version of an {@link ArchiveState}
 */
export interface SerializedArchiveState {
    name: string,
    meta: ArchiveMeta,
    videos?: SerializedVideosSnapshot,
    livestreams?: SerializedVideosSnapshot,
    shorts?: SerializedVideosSnapshot
}

/**
 * Deserializes {@link input} into a proper {@link ArchiveState}
 * @param input Serialized version of an archive state
 * @returns Deserialized {@link input}
 */
export function deserializeArchiveState(input: SerializedArchiveState): ArchiveState {
    return {
        name: input.name,
        meta: input.meta,
        videos: input.videos == undefined ? undefined : deserializeVideosSnapshot(input.videos),
        livestreams: input.livestreams == undefined ? undefined : deserializeVideosSnapshot(input.livestreams),
        shorts: input.shorts == undefined ? undefined : deserializeVideosSnapshot(input.shorts)
    }
}

// TODO
export function serializeArchiveState(input: ArchiveState): SerializedArchiveState {
    return {
        name: input.name,
        meta: input.meta,
        videos: input.videos == undefined ? undefined : serializeVideosSnapshot(input.videos),
        livestreams: input.livestreams == undefined ? undefined : serializeVideosSnapshot(input.livestreams),
        shorts: input.shorts == undefined ? undefined : serializeVideosSnapshot(input.shorts),
    }
}

// TODO
export function jsonParseArchiveState(json: string): ArchiveState {
    const serializedArchiveState: SerializedArchiveState = JSON.parse(json)
    return deserializeArchiveState(serializedArchiveState)
}

// TODO
export function jsonStringifyArchiveState(archiveState: ArchiveState): string {
    const serializedArchiveState: SerializedArchiveState = serializeArchiveState(archiveState)
    return JSON.stringify(serializedArchiveState)
}

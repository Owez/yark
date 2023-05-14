/**
 * Connectivity wrapper for the Yark API
 */

import type { Archive, Video } from "./archive";

/**
 * Overarching custom exception for API errors
 */
export class ApiError extends Error {
    constructor(message: string = 'Unknown/general Yark API error') {
        super(message);
        this.name = 'ApiError';
    }
}

/**
 * Exception for when an internal server error occurs
 */
export class InternalServerError extends ApiError {
    constructor(message: string = 'Internal server error occurred') {
        super(message);
        this.name = 'InternalServerError';
    }
}

/**
 * Exception for when a resource is not found
 */
export class NotFound extends ApiError {
    kind: NotFoundKind

    constructor(kind?: NotFoundKind, message: string = 'Requested resource not found') {
        super(message);
        this.name = 'NotFound';
        this.kind = kind ?? NotFoundKind.Unknown;
    }
}

/**
 * Kind of {@link NotFound} object which couldn't be found during a query
 */
export enum NotFoundKind {
    Archive = 'archive',
    Video = 'video',
    Image = 'image',
    Note = 'note',
    Directory = 'directory',
    Unknown = "unknown"
}

/**
 * Exception for when authentication fails or is missing
 */
export class Unauthorized extends ApiError {
    constructor(message: string = 'Unauthorized') {
        super(message);
        this.name = 'Unauthorized';
    }
}

/**
 * Type cover for an admin secret known to the admin and the api
 */
export type AdminSecret = string;

/**
 * Method of request to send in an {@link sendApiRequest}
 */
export enum ApiRequestMethod {
    Post = 'POST',
    Get = 'GET',
    Patch = 'PATCH',
    Delete = 'DELETE',
}

/**
 * Parameters that make up an {@link sendApiRequest} action
 */
export interface ApiRequest {
    /**
     * Base URL of the API, leave blank for default localhost
     */
    base?: URL;
    /**
     * Path/route of the URL to request; should include query params
     */
    path: string;
    /**
     * HTTP method to use during the request
     */
    method: ApiRequestMethod;
    /**
     * Optional {@link AdminSecret} to unlock protected routes
     */
    adminSecret?: AdminSecret
    /**
     * Optional JSON body to provide more information
     */
    json?: object
}

/**
 * Wrapper around a fetch request allowing easy api-specific actions
 * @param info Information for this request
 * @returns Response corresponding to {@link info} or an exception inherited from {@link ApiError}
 */
async function sendApiRequest(info: ApiRequest): Promise<Response> {
    const url = createUrl(info);
    const headers = createHeaders(info);
    const response = await fetch(url, {
        method: info.method,
        headers,
        body: info.json ? JSON.stringify(info.json) : undefined,
    });
    handleResponse(response);
    return response;
}

/**
 * Creates the URL to use for an {@link sendApiRequest}
 * @param info Info context to create the URL from
 * @returns URL which defaults to `localhost:7776` if no base is provided in {@link info}
 */
function createUrl(info: ApiRequest): string {
    const base = info.base == undefined ? "http://localhost:7776" : info.base
    return new URL(info.path, base).toString();
}

/**
 * Creates the headers to use for an {@link sendApiRequest}
 * @param info Info context to use
 * @returns Headers to use for an {@link sendApiRequest}
 */
function createHeaders(info: ApiRequest): HeadersInit {
    const headers: HeadersInit = {};
    if (info.json !== undefined) {
        headers["Content-Type"] = "application/json";
    }
    if (info.adminSecret !== undefined) {
        headers["Authorization"] = `Bearer ${info.adminSecret}`;
    }
    return headers;
}

/**
 * Handles a response (error checking via status code and body) for an {@link sendApiRequest}
 * @param response Response to handle
 */
function handleResponse(response: Response): void {
    if (!response.ok) {
        if (response.status === 404) {
            handleNotFound(response);
        } else if (response.status === 401) {
            throw new Unauthorized();
        } else {
            throw new InternalServerError(`API request failed: ${response.status} ${response.statusText}`);
        }
    }
}

/**
 * Handles a {@link NotFound} exception stemming from {@link handleResponse}
 * @param response Response to handle once it's known that it's a `404` error
 */
async function handleNotFound(response: Response): Promise<void> {
    interface JsonResp {
        message: string;
    }
    try {
        const jsonResp: JsonResp = await response.json();
        if (jsonResp && jsonResp.message) {
            if (jsonResp.message.includes("video")) {
                throw new NotFound(NotFoundKind.Video);
            } else if (jsonResp.message.includes("image")) {
                throw new NotFound(NotFoundKind.Image);
            } else if (jsonResp.message.includes("note")) {
                throw new NotFound(NotFoundKind.Note);
            } else if (jsonResp.message.includes("directory")) {
                throw new NotFound(NotFoundKind.Directory);
            } else if (jsonResp.message.includes("archive")) {
                throw new NotFound(NotFoundKind.Archive);
            }
        }
    } catch {
        throw new NotFound();
    }
}

/**
 * Response from API with a message saying what happened
 */
interface MessageResponse {
    message: string
}

/**
 * Response from API with a message saying what happened and an id of the related object
 */
interface MessageIdResponse {
    message: string,
    id: string
}

/**
 * Creates an archive with an existing ID in the given path and target
 * @param path The path to the archive
 * @param target The target of the archive
 * @param id The ID of the archive
 * @param adminSecret The admin secret for authentication
 * @param base (Optional) The base URL for the API request
 * @returns A promise that resolves when the archive is created
 */
export async function createExistingArchive(path: string, target: string, id: string, adminSecret: AdminSecret, base?: URL): Promise<void> {
    const payload = {
        path: path,
        target: target,
        id: id
    }
    await sendApiRequest({
        base: base,
        path: "/archive",
        method: ApiRequestMethod.Post,
        adminSecret: adminSecret,
        json: payload
    })
}

/**
 * Creates a new archive in the given path and target
 * @param path The path to the archive
 * @param target The target of the archive
 * @param adminSecret The admin secret for authentication
 * @param base (Optional) The base URL for the API request
 * @returns A promise that resolves with the ID of the created archive
 */
export async function createNewArchive(path: string, target: string, adminSecret: AdminSecret, base?: URL): Promise<string> {
    const payload = {
        path: path,
        target: target,
    }
    const resp = await sendApiRequest({
        base: base,
        path: "/archive",
        method: ApiRequestMethod.Post,
        adminSecret: adminSecret,
        json: payload
    })
    const data: MessageIdResponse = await resp.json()
    return data.id
}

/**
 * Different types of specific archives queries for different video lists
 */
export enum ArchiveKind {
    Videos = "videos",
    Livestreams = "livestreams",
    Shorts = "shorts",
}

/**
 * Retrieves the videos from the archive with the given ID and kind
 * @param id The ID of the archive
 * @param kind The video list kind to get for the archive
 * @param base (Optional) The base URL for the API request
 * @returns A promise that resolves with an array of videos
 */
export async function getArchive(id: string, kind: ArchiveKind, base?: URL): Promise<Video[]> {
    const path = kind == undefined ? `/archive/${id}` : `/archive/${id}?kind=${kind}`
    const resp = await sendApiRequest({
        base: base,
        path: path,
        method: ApiRequestMethod.Get,
    })
    return await resp.json()
}

/**
 * Deletes an archive of the given ID
 * @param id The ID of the archive to delete
 * @param adminSecret The admin secret for authentication
 * @param base (Optional) The base URL for the API request
 * @returns A promise that resolves when the archive is deleted
 */
export async function deleteArchive(id: string, adminSecret: string, base?: URL): Promise<void> {
    await sendApiRequest({
        base: base,
        path: `/archive/${id}`,
        method: ApiRequestMethod.Delete,
        adminSecret: adminSecret,
    })
}

// TODO: get image file


/**
 * Retrieves the video with the given video ID inside of the given archive ID
 * @param archiveId The ID of the archive
 * @param videoId The ID of the video
 * @param base (Optional) The base URL for the API request
 * @returns A promise that resolves with the queried video, if found
 */
export async function getVideo(archiveId: string, videoId: string, base?: URL): Promise<Video> {
    const resp = await sendApiRequest({
        base: base,
        path: `/archive/${archiveId}/video/${videoId}`,
        method: ApiRequestMethod.Get,
    })
    return await resp.json()
}

// TODO: get video file

/**
 * Information for items of a {@link Note} to be created with {@link createNote}
 */
export interface NoteCreate {
    title: string,
    timestamp: number,
    body: string | null
}

/**
 * 
 * @param archiveId 
 * @param videoId 
 * @param info 
 * @param adminSecret 
 * @param base 
 * @returns 
 */
export async function createNote(archiveId: string, videoId: string, info: NoteCreate, adminSecret: string, base?: URL): Promise<string> {
    const resp = await sendApiRequest({
        base: base,
        path: `/archive/${archiveId}/video/${videoId}/note`,
        method: ApiRequestMethod.Post,
        adminSecret: adminSecret,
        json: info
    })
    const data: MessageIdResponse = await resp.json();
    return data.id
}

/**
 * 
 */
export interface NoteUpdate {
    title?: string,
    timestamp?: number,
    body?: string | null
}

/**
 * 
 * @param archiveId 
 * @param videoId 
 * @param noteId 
 * @param info 
 * @param adminSecret 
 * @param base 
 */
export async function updateNote(archiveId: string, videoId: string, noteId: string, info: NoteUpdate, adminSecret: string, base?: URL): Promise<void> {
    await sendApiRequest({
        base: base,
        path: `/archive/${archiveId}/video/${videoId}/note/${noteId}`,
        method: ApiRequestMethod.Patch,
        adminSecret: adminSecret,
        json: info
    })
}

/**
 * 
 * @param archiveId 
 * @param videoId 
 * @param noteId 
 * @param adminSecret 
 * @param base 
 */
export async function deleteNote(archiveId: string, videoId: string, noteId: string, adminSecret: string, base?: URL): Promise<void> {
    await sendApiRequest({
        base: base,
        path: `/archive/${archiveId}/video/${videoId}/note/${noteId}`,
        method: ApiRequestMethod.Delete,
        adminSecret: adminSecret,
    })
}

/**
 * 
 */
export interface DirectoryItem {
    path: string,
    directory: boolean
}

/**
 * 
 * @param path 
 * @param adminSecret 
 * @param base 
 * @returns 
 */
export async function getDir(path: string, adminSecret: string, base?: URL): Promise<DirectoryItem[]> {
    const payload = { path: path }
    const resp = await sendApiRequest({
        base: base,
        path: `/fs`,
        method: ApiRequestMethod.Get,
        adminSecret: adminSecret,
        json: payload
    })
    return await resp.json()
}

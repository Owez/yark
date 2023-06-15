import type { Cookies } from "@sveltejs/kit"
import { getArchiveMeta, ArchiveKind, getArchiveVideos } from "./api"
import type { ArchiveMeta, Video } from "./archive"
import { deserializeArchiveState, jsonParseArchiveState, jsonStringifyArchiveState, type SerializedArchiveState } from "./serialdeserial"

export interface Snapshot<T> {
    taken: Date,
    data: T
}

function snapshotValid<T>(snapshot?: Snapshot<T>, seconds?: number): boolean {
    if (snapshot == undefined) {
        return false
    }
    const secondsFixed = seconds == undefined ? 120 : seconds
    let snapshotMax = snapshot.taken
    snapshotMax.setSeconds(snapshotMax.getSeconds() + secondsFixed)
    const now = new Date()
    return snapshotMax > now
}

function newSnapshot<T>(data: T): Snapshot<T> {
    return {
        taken: new Date(),
        data: data
    }
}

/**
 * Gets an up-to-date videos list for an archive state; also saves to state as well as returning
 * @param state State of archive
 * @param kind Kind of videos list to get (doesn't include {@link ArchiveKind.Meta})
 * @param base (Optional) The base URL for the API request
 * @returns Up-to-date videos list for {@link kind} selected; saved to state as well
 */
export async function getVideosList(state: ArchiveState, kind: ArchiveKind, base?: URL): Promise<Video[]> {
    const metaData = state.meta.data
    switch (kind) {
        case ArchiveKind.Videos:
            if (state.videos != undefined && snapshotValid(state.videos)) {
                return state.videos.data
            }
            const newVideos = await getArchiveVideos(metaData.id, kind, base)
            state.videos = newSnapshot(newVideos)
            return state.videos.data

        case ArchiveKind.Livestreams:
            if (state.livestreams != undefined && snapshotValid(state.livestreams)) {
                return state.livestreams.data
            }
            const newLivestreams = await getArchiveVideos(metaData.id, kind, base)
            state.livestreams = newSnapshot(newLivestreams)
            return state.livestreams.data

        case ArchiveKind.Shorts:
            if (state.shorts != undefined && snapshotValid(state.shorts)) {
                return state.videos.data
            }
            const newShorts = await getArchiveVideos(metaData.id, kind, base)
            state.shorts = newSnapshot(newShorts)
            return state.shorts.data
        default:
            throw new Error("Meta-information archive kind isn't a valid videos list")
    }
}

/**
 * Archive state representing a fully saved archive
 */
export interface ArchiveState {
    name: string,
    meta: Snapshot<ArchiveMeta>,
    videos?: Snapshot<Video[]>,
    livestreams?: Snapshot<Video[]>,
    shorts?: Snapshot<Video[]>
}

/**
 * Gets archive state from archive identifier
 * @param id Identifier of the archive
 * @param base (Optional) The base URL for the API request
 * @returns Archive state reflecting the archive with {@link id}; only metainfo included
 */
export async function getArchiveStateRemote(id: string, name: string, base?: URL): Promise<ArchiveState | null> {
    const meta = await getArchiveMeta(id, base)
    const metaSnapshot = newSnapshot(meta)
    return meta == null ? null : { name: name, meta: metaSnapshot }
}

/**
 * Gets archive state from server-side cookies, deserializing properly
 * @param cookies Cookies to get state from
 * @returns Properly deserialized archive state
 */
export function getArchiveStateCookie(cookies: Cookies): ArchiveState | null {
    const stateRaw = cookies.get("archiveState")
    if (stateRaw == undefined) { return null }
    return jsonParseArchiveState(stateRaw)
}

/**
 * Represents a recent archive from a previous {@link ArchiveState} to pull again if wanted
 */
export interface RecentArchive {
    name: string,
    id: string
}

/**
 * Converts an archive state into a {@link RecentArchive}
 * @param state State to convert
 * @returns Converted {@link state} as a {@link RecentArchive} to use
 */
export function archiveStateToRecent(state: ArchiveState): RecentArchive {
    const metaData = state.meta.data
    return { name: state.name, id: metaData.id }
}

/**
 * Gets an {@link ArchiveState} reflecting the inputted {@link RecentArchive}
 * @param recent Recent archive to get state of
 * @param base (Optional) The base URL for the API request
 * @returns Archive state reflecting the archive with {@link recent.id}
 */
export async function recentArchiveToState(recent: RecentArchive, base?: URL): Promise<ArchiveState | null> {
    return getArchiveStateRemote(recent.id, recent.name, base)
}

/**
 * Saves provided {@link state} to the {@link document}'s cookie for browser-side saving
 * @param state Archive state to save
 * @param document Document to save {@link state} to
 */
export function saveArchiveStateClient(archiveState: ArchiveState, document: Document) {
    function setCookie(name: string, val: string, document: Document) {
        const value = val;
        document.cookie = name + "=" + value + "; path=/";
    }
    setCookie("archiveState", jsonStringifyArchiveState(archiveState), document)
}

/**
 * Saves provided {@link state} to the {@link cookies} for server-side saving
 * @param state Archive state to save
 * @param cookies Cookies to save to
 */
export function saveArchiveStateServer(archiveState: ArchiveState, cookies: Cookies) {
    cookies.set("archiveState", jsonStringifyArchiveState(archiveState), { path: "/" })
}
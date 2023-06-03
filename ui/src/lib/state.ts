import type { Cookies } from "@sveltejs/kit"
import { type ArchiveMeta, getArchiveMeta, ArchiveKind, getArchiveVideos } from "./api"
import type { Video } from "./archive"
import { deserializeArchiveState, type SerializedArchiveState } from "./state_json"

/**
 * Snapshot of a {@link Video} list used for {@link ArchiveState} operations
 */
export interface VideosSnapshot {
    taken: Date,
    videos: Video[]
}

/**
 * Checks if a snapshot is valid within {@link VideosSnapshot.taken} + {@link seconds}
 * @param snapshot Snapshot to check
 * @param seconds Seconds to add; defaults to `30`
 * @returns If it's valid
 */
function videosSnapshotValid(snapshot?: VideosSnapshot, seconds?: number): boolean {
    if (snapshot == undefined) {
        return false
    }
    const secondsFixed = seconds == undefined ? 120 : seconds
    let snapshotMax = snapshot.taken
    snapshotMax.setSeconds(snapshotMax.getSeconds() + secondsFixed)
    const now = new Date()
    return snapshotMax > now
}

/**
 * Creates a video snapshot rated for now
 * @param videos Videos list to use as data
 * @returns New snapshot for now
 */
function newVideosSnapshot(videos: Video[]): VideosSnapshot {
    return {
        taken: new Date(),
        videos: videos
    }
}

/**
 * Gets an up-to-date videos list for an archive state; also saves to state as well as returning
 * @param state State of archive
 * @param kind Kind of videos list to get (doesn't include {@link ArchiveKind.Meta})
 * @param base (Optional) The base URL for the API request
 * @returns Up-to-date videos list for {@link kind} selected; saved to state as well
 */
export async function getVideosList(state: ArchiveState, kind: ArchiveKind, base?: URL): Promise<VideosSnapshot> {
    switch (kind) {
        case ArchiveKind.Videos:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos
            }
            const newVideos = await getArchiveVideos(state.meta.id, kind, base)
            state.videos = newVideosSnapshot(newVideos)
            return state.videos

        case ArchiveKind.Livestreams:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos
            }
            const newLivestreams = await getArchiveVideos(state.meta.id, kind, base)
            state.livestreams = newVideosSnapshot(newLivestreams)
            return state.livestreams

        case ArchiveKind.Shorts:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos
            }
            const newShorts = await getArchiveVideos(state.meta.id, kind, base)
            state.shorts = newVideosSnapshot(newShorts)
            return state.shorts
        default:
            throw new Error("Meta-information archive kind isn't a valid videos list")
    }
}

/**
 * Archive state representing a fully saved archive
 */
export interface ArchiveState {
    name: string,
    meta: ArchiveMeta,
    videos?: VideosSnapshot,
    livestreams?: VideosSnapshot,
    shorts?: VideosSnapshot
}

/**
 * Gets archive state from archive identifier
 * @param id Identifier of the archive
 * @param base (Optional) The base URL for the API request
 * @returns Archive state reflecting the archive with {@link id}; only metainfo included
 */
export async function getArchiveStateRemote(id: string, name: string, base?: URL): Promise<ArchiveState | null> {
    const meta = await getArchiveMeta(id, base)
    return meta == null ? null : { name: name, meta: meta }
}

/**
 * Gets archive state from server-side cookies, deserializing properly
 * @param cookies Cookies to get state from
 * @returns Properly deserialized archive state
 */
export function getArchiveStateCookie(cookies: Cookies): ArchiveState | null {
    const stateRaw = cookies.get("archiveState")
    if (stateRaw == undefined) { return null }
    const serializedArchiveState: SerializedArchiveState = JSON.parse(stateRaw)
    return deserializeArchiveState(serializedArchiveState)
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
    return { name: state.name, id: state.meta.id }
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
export function saveArchiveStateClient(state: ArchiveState, document: Document) {
    function setCookie(name: string, val: string, document: Document) {
        const value = val;
        document.cookie = name + "=" + value + "; path=/";
    }
    setCookie("archiveState", JSON.stringify(state), document)
}

/**
 * Saves provided {@link state} to the {@link cookies} for server-side saving
 * @param state Archive state to save
 * @param cookies Cookies to save to
 */
export function saveArchiveStateServer(state: ArchiveState, cookies: Cookies) {
    cookies.set("archiveState", JSON.stringify(state))
}
import { type ArchiveMeta, createNewArchive, recreateArchive, getArchiveMeta, ArchiveKind, getArchiveVideos } from "./api"
import type { Video } from "./archive"

/**
 * Key used to access {@link window.localStorage} to get the {@link ArchiveState}
 */
const STORAGE_KEY = "archiveState"

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
function videosSnapshotValid(snapshot: VideosSnapshot, seconds?: number): boolean {
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
 * Gets an up-to-date videos list for an archive state
 * @param state State of archive
 * @param kind Kind of videos list to get (doesn't include {@link ArchiveKind.Meta})
 * @param base (Optional) The base URL for the API request
 * @returns Up-to-date videos list for {@link kind} selected
 */
export async function getVideosList(state: ArchiveState, kind: ArchiveKind, base?: URL): Promise<Video[]> {
    switch (kind) {
        case ArchiveKind.Videos:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos.videos
            }
            const newVideos = await getArchiveVideos(state.meta.id, kind, base)
            state.videos = newVideosSnapshot(newVideos)
            return newVideos

        case ArchiveKind.Livestreams:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos.videos
            }
            const newLivestreams = await getArchiveVideos(state.meta.id, kind, base)
            state.livestreams = newVideosSnapshot(newLivestreams)
            return newLivestreams

        case ArchiveKind.Shorts:
            if (state.videos != undefined && videosSnapshotValid(state.videos)) {
                return state.videos.videos
            }
            const newShorts = await getArchiveVideos(state.meta.id, kind, base)
            state.shorts = newVideosSnapshot(newShorts)
            return newShorts

        default:
            throw new Error("Meta-information archive kind isn't a valid videos list")
    }
}

export interface ArchiveState {
    meta: ArchiveMeta,
    videos?: VideosSnapshot,
    livestreams?: VideosSnapshot,
    shorts?: VideosSnapshot
}

/**
 * Gets archive state from archive identifier
 * @param id Identifier of the archive
 * @param base (Optional) The base URL for the API request
 * @returns Archive state reflecting the archive with {@link id}
 */
export async function getArchiveState(id: string, base?: URL): Promise<ArchiveState | null> {
    const meta = await getArchiveMeta(id, base)
    return meta == null ? null : { meta: meta }
}

/**
 * Saves archive state to local storage
 * @param state State to save
 */
export function saveArchiveState(state: ArchiveState) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

/**
 * Loads archive state back up from storage
 * @returns Freshly-loaded state
 */
export function loadArchiveState(): ArchiveState | null {
    const got = window.localStorage.getItem(STORAGE_KEY)
    if (got == null) { return null }
    return JSON.parse(got)
}

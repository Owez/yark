import { ArchiveKind, type ArchiveMeta } from '$lib/api.js';
import { getVideosList, saveArchiveStateServer, type ArchiveState, type VideosSnapshot } from '$lib/state.js';
import type { PageServerLoad } from './$types.js';

/**
 * Same as a normal {@link ArchiveState} but with all guaranteed elements
 */
interface ArchiveStateDefinitely {
    name: string,
    meta: ArchiveMeta,
    videos: VideosSnapshot,
    livestreams: VideosSnapshot,
    shorts: VideosSnapshot
}

export const load = (async ({ parent, cookies }) => {
    // Get archive state and make sure the lists are there
    const archiveState: ArchiveState = (await parent()).archiveState
    const videos = await getVideosList(archiveState, ArchiveKind.Videos)
    const livestreams = await getVideosList(archiveState, ArchiveKind.Livestreams)
    const shorts = await getVideosList(archiveState, ArchiveKind.Shorts)
    saveArchiveStateServer(archiveState, cookies)

    // Now we know the lists, apply to a guaranteed version
    const archiveStateDefinitely: ArchiveStateDefinitely = {
        name: archiveState.name,
        meta: archiveState.meta,
        videos,
        livestreams,
        shorts
    }
    return { archiveState: archiveStateDefinitely }
}) satisfies PageServerLoad
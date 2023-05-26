import { ArchiveKind } from '$lib/api.js';
import { getVideosList, saveArchiveStateServer } from '$lib/state.js';
import type { PageServerLoad } from './$types.js';

export async function load({ parent, cookies }): Promise<PageServerLoad> {
    const archiveState = (await parent()).archiveState
    await getVideosList(archiveState, ArchiveKind.Videos)
    await getVideosList(archiveState, ArchiveKind.Livestreams)
    await getVideosList(archiveState, ArchiveKind.Shorts)
    saveArchiveStateServer(archiveState, cookies)
    return { archiveState }
}
import { getArchiveKind, getVideosList, saveArchiveStateServer } from "$lib/state";
import type { LayoutServerLoad } from "./$types";

export const load = (async ({ parent, url, cookies }) => {
    // Get archive kind and state
    const archiveKind = getArchiveKind(url.pathname)
    if (archiveKind == null) { throw new Error("archiveKind should only be null on meta page") }
    const archiveState = (await parent()).archiveState

    // Get relevant videos list and save so it's up to date
    let videos = (await getVideosList(archiveState, archiveKind)).videos
    saveArchiveStateServer(archiveState, cookies)

    // Return all data
    return { archiveState, archiveKind, videos }
}) satisfies LayoutServerLoad;

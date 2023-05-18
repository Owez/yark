import { ArchiveKind, getArchiveVideos } from "$lib/api";
import { type ArchiveState, videosSnapshotValid, newVideosSnapshot } from "$lib/state";
import type { LayoutServerLoad } from "./$types";

export async function load({ cookies, url }): Promise<LayoutServerLoad> {
    // Get archive state
    const archiveStateCookie = cookies.get("archiveState")
    let archiveState: ArchiveState | null;
    if (archiveStateCookie == undefined) {
        archiveState = null
    } else {
        const parsed: ArchiveState = JSON.parse(archiveStateCookie)
        archiveState = parsed
    }

    // Return data
    return { archiveState }
}

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

    // Get archive kind and preload video lists
    const archiveKindQuery = url.searchParams.get("kind");
    let archiveKind = ArchiveKind.Meta;
    if (archiveKindQuery != null) {
        switch (archiveKindQuery) {
            case "videos":
                archiveKind = ArchiveKind.Videos
                if (archiveState != null && !videosSnapshotValid(archiveState.videos)) {
                    archiveState.videos = newVideosSnapshot(await getArchiveVideos(archiveState.meta.id, archiveKind))
                }
                break;
            case "livestreams":
                archiveKind = ArchiveKind.Livestreams
                if (archiveState != null && !videosSnapshotValid(archiveState.livestreams)) {
                    archiveState.livestreams = newVideosSnapshot(await getArchiveVideos(archiveState.meta.id, archiveKind))
                }
                break;
            case "shorts":
                archiveKind = ArchiveKind.Shorts
                if (archiveState != null && !videosSnapshotValid(archiveState.shorts)) {
                    archiveState.shorts = newVideosSnapshot(await getArchiveVideos(archiveState.meta.id, archiveKind))
                }
                break;
            default:
                break;
        }
    }

    // Return data
    return { archiveState, archiveKind }
}

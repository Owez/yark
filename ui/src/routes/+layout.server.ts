import { ArchiveKind } from "$lib/api";
import type { ArchiveState } from "$lib/state";
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
                break;
            case "livestreams":
                archiveKind = ArchiveKind.Livestreams
                break;
            case "shorts":
                archiveKind = ArchiveKind.Shorts
                break;
            default:
                break;
        }
    }

    // Return data
    return { archiveState, archiveKind }
}

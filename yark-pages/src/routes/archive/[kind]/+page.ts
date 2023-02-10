import { ArchiveVideoKind, fetchVideosBrief } from "$lib/archive";
import { get } from "svelte/store";
import type { PageLoad, RouteParams } from "./$types";
import { yarkStore } from "$lib/store";

export const load: PageLoad = async ({ params }) => {
    // Get video list kind and store to use
    const kind = getVideoKind(params)
    const store = get(yarkStore)
    const archive = store.openedArchive;
    if (archive == null) { throw new Error("No current archive set") }

    // Fetch videos from current archive
    const videos = await fetchVideosBrief(archive, kind)

    // Return the important information
    return { kind, videos }
}

/**
 * Get kind of video to download from params
 * @param params Current request parameters to get from
 */
function getVideoKind(params: RouteParams): ArchiveVideoKind {
    switch (params.kind) {
        case ("videos"):
            return ArchiveVideoKind.Videos
        case ("livestreams"):
            return ArchiveVideoKind.Livestreams
        case ("shorts"):
            return ArchiveVideoKind.Shorts
        default:
            throw new Error("Unknown video kind provided to fetch from archive")
    }
}
import type { ArchiveState } from "$lib/state";
import type { LayoutServerLoad } from "./$types";

export async function load({ cookies }): Promise<LayoutServerLoad> {
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

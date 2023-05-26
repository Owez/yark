import { getArchiveStateCookie, type ArchiveState } from "$lib/state";
import type { LayoutServerLoad } from "./$types";

export async function load({ cookies }): Promise<LayoutServerLoad> {
    // Get archive state
    const archiveState = getArchiveStateCookie(cookies)

    // Return data
    return { archiveState }
}

import { getArchiveStateCookie } from "$lib/state";
import type { LayoutServerLoad } from "./$types";

export const load = (({ cookies }) => {
    // Get archive state
    const archiveState = getArchiveStateCookie(cookies)

    // Return data
    return { archiveState }
}) satisfies LayoutServerLoad;

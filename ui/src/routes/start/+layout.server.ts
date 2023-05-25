import { redirect } from '@sveltejs/kit';
import type { RecentArchive } from '$lib/state';
import type { LayoutServerLoad } from './$types';

export async function load({ parent, cookies }): Promise<LayoutServerLoad> {
    // Make sure there isn't a current archive state
    const archiveState = (await parent()).archiveState
    if (archiveState != null) {
        throw redirect(307, "/archive")
    }

    // Get recent archives
    const recentArchivesRaw = cookies.get("recentArchives")
    const recentArchives: RecentArchive[] = recentArchivesRaw == undefined ? [] : JSON.parse(recentArchivesRaw)
    return { recentArchives }
}
import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export async function load({ parent }): Promise<PageLoad> {
    const archiveState = (await parent()).archiveState
    if (archiveState == null) {
        throw redirect(307, "/start")
    }

    return { archiveState }
}

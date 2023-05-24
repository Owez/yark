import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types.js';

export async function load({ parent }): Promise<LayoutLoad> {
    const archiveState = (await parent()).archiveState
    if (archiveState == null) {
        throw redirect(307, "/")
    }

    return { archiveState }
}

import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export async function load({ parent }): Promise<LayoutServerLoad> {
    // Get state and redirect if it's already loaded
    const archiveState = (await parent()).archiveState
    if (archiveState == null) {
        throw redirect(307, "/start")
    }

    return { archiveState }
}

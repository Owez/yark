import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load =(async ({ parent }) => {
    // Get state and redirect if it's already loaded
    const archiveState = (await parent()).archiveState
    if (archiveState == null) {
        throw redirect(307, "/start")
    }

    return { archiveState }
}) satisfies LayoutServerLoad

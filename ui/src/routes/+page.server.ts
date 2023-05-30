import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ parent }) => {
    const parentData = await parent()
    if (parentData.archiveState == null) {
        throw redirect(307, "/start")
    }
    throw redirect(307, "/archive")
}) satisfies PageServerLoad;
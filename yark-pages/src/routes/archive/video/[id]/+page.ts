import type { PageLoad } from "./$types";
import { fetchVideoDetails, getOpenedArchiveAlways } from "$lib/archive";

export const load: PageLoad = async ({ params }) => {
    // Get video id and archive to use
    const id = params.id;
    const archive = getOpenedArchiveAlways()

    // Fetch detailed video information
    const video = await fetchVideoDetails(archive, id)

    // Return the video
    return { video }
}
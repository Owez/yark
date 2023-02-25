import type { PageLoad } from "./$types";
import { fetchVideoDetails } from "$lib/archive";

export const load: PageLoad = async ({ params }) => {
    // Fetch detailed video information
    const id = params.id;
    const video = await fetchVideoDetails(id)

    // Return the video
    return { id, video }
}

import type { PageLoad } from "./$types";
import { fetchVideoDetails } from "$lib/archive";

export const load: PageLoad = async ({ params }) => {
    // Fetch detailed video information
    const video_id = params.id;
    const video = await fetchVideoDetails(video_id)

    // Return the video
    return { video_id, video }
}

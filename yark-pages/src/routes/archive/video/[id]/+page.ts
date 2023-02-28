import type { PageLoad } from "./$types";
import { fetchVideoDetails } from "$lib/archive";

export const load: PageLoad = async ({ params }) => {
    // Fetch detailed video information
    const videoId = params.id;
    const [video, videoRawArchive] = await fetchVideoDetails(videoId)

    // Return the video
    return { videoId, video, videoRawArchive }
}

import { ArchiveVideoKind, fetchVideosBrief, getOpenedArchiveAlways } from '$lib/archive';
import type { PageLoad, RouteParams } from './$types';

export const load: PageLoad = async ({ params }) => {
	// Get video list kind and archive to use
	const kind = getVideoKind(params);
	const archive = getOpenedArchiveAlways()

	// Fetch videos from current archive
	const videos = await fetchVideosBrief(archive, kind);

	// Return the important information
	return { kind, videos };
};

/**
 * Get kind of video to download from params
 * @param params Current request parameters to get from
 */
function getVideoKind(params: RouteParams): ArchiveVideoKind {
	switch (params.kind) {
		case 'videos':
			return ArchiveVideoKind.Videos;
		case 'livestreams':
			return ArchiveVideoKind.Livestreams;
		case 'shorts':
			return ArchiveVideoKind.Shorts;
		default:
			throw new Error('Unknown video kind provided to fetch from archive');
	}
}

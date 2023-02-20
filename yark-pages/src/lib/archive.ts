/**
 * Connector to the official Yark REST API for interfacing
 */

import { goto } from '$app/navigation';
import { yarkStore } from './store';

/**
 * Core archive representation used by various components
 */
export interface Archive {
	/**
	 * The base server url this archive can be found at
	 */
	server: string;
	/**
	 * The unique slug identifier of this archive
	 */
	slug: string;
}

/**
 * Payload for creating a brand new {@link Archive} using a server
 */
export interface CreateArchiveRemotePayload {
	/**
	 * See {@link Archive.server}
	 */
	server: string;
	/**
	 * See {@link Archive.slug}
	 */
	slug: string;
	/**
	 * The full path (from drive/root) on the server to save the new archive to, including the final directory name
	 */
	path: string;
	/**
	 * The YouTube target URL which the archive is intended to capture
	 */
	target: string;
}

/**
 * Payload for importing an existing {@link Archive} into a server
 */
export interface ImportArchiveRemotePayload {
	/**
	 * See {@link Archive.server}
	 */
	server: string;
	/**
	 * See {@link Archive.slug}
	 */
	slug: string;
	/**
	 * The full path (from drive/root) on the server to the archive to import
	 */
	path: string;
}

/**
 * Creates a brand new archive on the server, provided that the credentials are correct
 * TODO: document auth once done
 * @param param0 Payload for creation
 * @returns Representation of the newly-created archive
 */
export async function createNewRemote({
	server,
	slug,
	path,
	target
}: CreateArchiveRemotePayload): Promise<Archive> {
	// TODO: auth
	const payload = { slug, path, target };
	const url = new URL(server);

	url.pathname = '/archive';
	url.searchParams.set('intent', 'create');

	return await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	})
		.then((resp) => resp.json())
		.then((resp_json) => {
			return { server, slug: resp_json.slug };
		});
}

/**
 * Imports an existing archive on the server, effectively making the server aware of this existing archive
 * @param param0 Payload for importing
 * @returns Representation of the newly-imported archive
 */
export async function importNewRemote({
	server,
	slug,
	path
}: ImportArchiveRemotePayload): Promise<Archive> {
	const payload = { slug, path };
	const url = new URL(server);

	url.pathname = '/archive';
	url.searchParams.set('intent', 'existing');

	return await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	})
		.then((resp) => resp.json())
		.then((resp_json) => {
			return { server, slug: resp_json.slug };
		});
}

/**
 * Sets an archive to be the currently-operable archive in the app-wide store
 * @param archive Archive to set as current
 */
export function setCurrentArchive(archive: Archive): void {
	yarkStore.update((value) => {
		value.openedArchive = archive;

		if (value.recents.length >= 10) {
			value.recents.shift();
		}

		value.recents.push(archive);

		return value;
	});
	goto(`/archive/videos`);
}

/**
 * Fetches information on a whole list of videos (e.g., livestreams) in the archive for display
 * @param archive Archive to fetch videos inside of
 * @param kind Kind of videos to fetch
 * @returns Brief info about an entire list/category of videos on the archive
 */
export async function fetchVideosBrief(
	archive: Archive,
	kind: ArchiveVideoKind
): Promise<ArchiveBriefVideo[]> {
	const url = new URL(archive.server);
	url.pathname = `/archive/${archive.slug}`;
	url.searchParams.set('kind', archiveVideoKindToApiString(kind));

	return await fetch(url).then((resp) => resp.json());
}

/**
 * Video list kind which can be got from an archive
 */
export enum ArchiveVideoKind {
	Videos,
	Livestreams,
	Shorts
}

/**
 * Converts a {@link ArchiveVideoKind} to an API-compatible query string
 * @param kind Kind to convert to string
 * @returns Stringified API-compatible version
 */
function archiveVideoKindToApiString(kind: ArchiveVideoKind): string {
	switch (kind) {
		case ArchiveVideoKind.Videos:
			return 'videos';
		case ArchiveVideoKind.Livestreams:
			return 'livestreams';
		case ArchiveVideoKind.Shorts:
			return 'shorts';
	}
}

/**
 * Short information on a video, intended to be displayed on a long list
 */
export interface ArchiveBriefVideo {
	/**
	 * Video identifier to open to learn more about the video
	 */
	id: string;
	/**
	 * Current human-readable name of the video
	 */
	name: string;
	/**
	 * Date it was uploaded to display/sort using
	 */
	uploaded: Date;
	/**
	 * Current thumbnail identifier of the video to display
	 */
	thumbnail: string;
}
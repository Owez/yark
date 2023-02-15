/**
 * Connector to the official Yark REST API for interfacing
 */

import { goto } from '$app/navigation';
import { yarkStore } from './store';

/**
 * Type alias for archive paths
 *
 * - Includes full `/x/y/z` if local
 * - Includes only archive name (or local path) if federated
 */
export type ArchivePath = string;

export interface CreateArchivePayload {
	server: string;
	slug: string;
	path: string;
	target: string;
}

export interface CreateExistingArchivePayload {
	server: string;
	slug: string;
	path: string;
}

export interface Archive {
	server: string;
	slug: string;
}

export async function createNewRemote({
	server,
	slug,
	path,
	target
}: CreateArchivePayload): Promise<Archive> {
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

export async function fromExistingRemote({
	server,
	slug,
	path
}: CreateExistingArchivePayload): Promise<Archive> {
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
